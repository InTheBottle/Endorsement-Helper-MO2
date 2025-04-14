
try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QLineEdit, QScrollArea, QPushButton, QHBoxLayout,
        QLabel, QCheckBox, QDialog, QDialogButtonBox, QSpinBox, QComboBox
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QLineEdit, QScrollArea, QPushButton, QHBoxLayout,
            QLabel, QCheckBox, QDialog, QDialogButtonBox, QSpinBox, QComboBox
        )
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QIcon
    except ImportError:
        from PySide2.QtWidgets import (
            QWidget, QVBoxLayout, QLineEdit, QScrollArea, QPushButton, QHBoxLayout,
            QLabel, QCheckBox, QDialog, QDialogButtonBox, QSpinBox, QComboBox
        )
        from PySide2.QtCore import Qt
        from PySide2.QtGui import QIcon

import mobase
import os, json, configparser, webbrowser
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), "EndorsementHelperData.json")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endorsement Helper Settings")
        layout = QVBoxLayout()

        self.sort_label = QLabel("Sort mods by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Install Date"])
        layout.addWidget(self.sort_label)
        layout.addWidget(self.sort_combo)

        self.hide_marked = QCheckBox("Hide mods I’ve marked as endorsed")
        layout.addWidget(self.hide_marked)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_settings(self):
        return {
            "sort_order": self.sort_combo.currentText(),
            "hide_marked": self.hide_marked.isChecked()
        }

    def set_settings(self, settings):
        self.sort_combo.setCurrentText(settings.get("sort_order", "Name"))
        self.hide_marked.setChecked(settings.get("hide_marked", True))


def run_dialog(dialog):
    return dialog.exec() if hasattr(dialog, "exec") else dialog.exec_()

class EndorsementHelper(mobase.IPluginTool):
    
    def load_data(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "EndorsementHelperData.json"), "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            self.data = {}
    def __init__(self):
        super().__init__()
        self._organizer = None
        self.mods = []
        self.user_settings = {"reminder_days": 0, "sort_order": "Name", "hide_marked": True}
        self.data = {}

    def init(self, organizer: mobase.IOrganizer):
        self._organizer = organizer
        print("Endorsement Helper initialized")
        return True
        self._organizer = organizer
        self.load_data()
        return True

    def name(self): return "Endorsement Helper"
    def displayName(self): return "Endorsement Helper"
    def description(self): return "Display unendorsed mods with filters and local tracking."
    def tooltip(self): return "Manage endorsements manually with smart filters and tracking."
    def icon(self): return QIcon()
    def isActive(self): return True
    def settings(self): return []
    def extract_summary(self, path):
        for fname in ["readme.txt", "description.txt"]:
            full = os.path.join(path, fname)
        if os.path.exists(full):
            try:
                with open(full, "r", encoding="utf-8") as f:
                    return f.read(300).strip()
            except Exception:
                return ""
            
    def mark_endorsed(self, name):
        self.data[name] = {"marked": True}
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
         print(f"Error saving endorsement data: {e}")
        self.refresh()


    def display(self):
        self.load_data()
        self.window = QWidget()
        self.window.setWindowTitle("Endorsement Helper")
        self.window.resize(1860, 600)
        layout = QVBoxLayout()
        
        # Embedded sorting/hide controls
        control_row = QWidget()
        control_layout = QHBoxLayout()
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Install Date"])
        self.sort_combo.currentTextChanged.connect(self.refresh)
        self.hide_checkbox = QCheckBox("Hide mods I’ve marked as endorsed")
        self.hide_checkbox.setChecked(True)
        self.hide_checkbox.stateChanged.connect(self.refresh)
        control_layout.addWidget(QLabel("Sort mods by:"))
        control_layout.addWidget(self.sort_combo)
        control_layout.addStretch()
        control_layout.addWidget(self.hide_checkbox)
        control_row.setLayout(control_layout)
        layout.addWidget(control_row)

        self.stats = QLabel()
        layout.addWidget(self.stats)
    

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search mods...")
        self.search.textChanged.connect(self.refresh)
        layout.addWidget(self.search)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        self.scroll.setWidget(self.container)

        self.window.setLayout(layout)
        self.refresh()
        self.window.show()

    def open_settings(self):
        self.settings_dialog = SettingsDialog(self.window)
        self.settings_dialog.set_settings(self.user_settings)
        if run_dialog(self.settings_dialog):
            self.user_settings = self.settings_dialog.get_settings()
            self.refresh()
            self.save_data()

    def refresh(self):
        for i in reversed(range(self.container_layout.count())):
            self.container_layout.itemAt(i).widget().setParent(None)

        
        mods = self._organizer.modList().allMods()
        active = [m for m in mods if self._organizer.modList().state(m) & mobase.ModState.ACTIVE]
        game = self._organizer.managedGame()
        game_name = game.gameNexusName() if game else "skyrimspecialedition"

        self.mods = []
        search_text = self.search.text().lower()
        seen_ids = set()

        for mod in active:
            mod_info = self._organizer.modList().getMod(mod)
            nexus_id = mod_info.nexusId()
            if not nexus_id or nexus_id in seen_ids:
                continue
            seen_ids.add(nexus_id)

            name = mod_info.name()
            if search_text and search_text not in name.lower():
                continue

            if self.hide_checkbox.isChecked() and self.data.get(name, {}).get("marked"):
                continue

            meta = os.path.join(mod_info.absolutePath(), "meta.ini")
            endorsed = False
            if os.path.exists(meta):
                config = configparser.ConfigParser()
                config.read(meta, encoding="utf-8")
                if config.has_section("General"):
                    endorsed = config.get("General", "endorsed", fallback="0") == "1"

            if endorsed:
                continue

            path = mod_info.absolutePath()
            install_time = datetime.fromtimestamp(os.path.getctime(path))

            self.mods.append((name, nexus_id, install_time, path))

        if self.sort_combo.currentText() == "Install Date":
            self.mods.sort(key=lambda x: x[2], reverse=True)
        else:
            self.mods.sort(key=lambda x: x[0].lower())

        for name, nexus_id, _, path in self.mods:
            url = f"https://www.nexusmods.com/{game_name}/mods/{nexus_id}"
            row = QWidget()
            row_layout = QHBoxLayout()
            label = QLabel(name)
            tooltip = self.extract_summary(path)
            if tooltip:
                label.setToolTip(tooltip)
            button = QPushButton("🡕 Nexus")
            button.clicked.connect(lambda _, u=url: webbrowser.open(u))
            mark = QPushButton("✅ Mark")
            mark.clicked.connect(lambda _, n=name: self.mark_endorsed(n))
            row_layout.addWidget(label)
            row_layout.addWidget(button)
            row_layout.addWidget(mark)
            row.setLayout(row_layout)
            self.container_layout.addWidget(row)

        self.stats.setText(f"Unendorsed mods shown: {len(self.mods)}")


def createPlugin():
    return EndorsementHelper()