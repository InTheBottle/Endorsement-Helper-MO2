# Endorsement-Helper-MO2
Python script to sort only unendorsed mods and provides links to mod pages to endorse

# Endorsement Helper (MO2 Plugin)

Endorsement Helper is a plugin for Mod Organizer 2 that helps you track which active mods have not been endorsed on Nexus Mods. It provides a filtered view and local tracking to avoid duplicates and unnecessary reminders.

## Features

- Lists active mods that are not endorsed
- Filters by name
- Sorts mods by name or install date
- Option to hide mods you’ve already marked
- Button to open the mod’s Nexus page
- Marks are stored locally and do not affect your mod files or meta.ini
- Prevents showing the same Nexus mod multiple times by checking Nexus ID

## Installation

1. Place `endorsement_helper.py` into the `plugins/` folder in your Mod Organizer 2 directory.
2. Launch MO2 and open it from the Tools > Tool Plugins menu.

## Usage

- Use the search bar to filter mods by name
- Use the dropdown to sort by name or install date
- Click **Nexus** to visit the mod page
- Click **Mark** to hide it from the list
- Enable or disable “Hide mods I’ve marked as endorsed” in the window
- Marked mods are stored in `EndorsementHelperData.json` in the plugin folder

## Notes

- This tool does not connect to your Nexus Mods account
- It does not modify your mod list or metadata
- All markings are stored locally and privately
