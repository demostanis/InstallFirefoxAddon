# Install Firefox Addon
Python script to automatically install Firefox addons right from your shell

## Why? I have been digging since hours through the entire web and found out Ubuntu has a script doing the exact same.
For now, it does the same, albeit it uses AMO (addons.mozilla.org) search's API.
It is planned to have the ability to customize SQLite addons databases, in the future.

## Installation
This script has no dependencies except the language it is written in, Python 3.
You can download it using tools like `wget` or `curl`, chmod and execute it.

## Usage
Simply call the script with `<addon>` argument:
`./InstallFirefoxAddon.py "uBlock Origin"`
You will then be prompted to choose the correct addon between search results.
If you want not to be prompted and to automatically choose the first addon, use the `--first` option:
`./InstallFirefoxAddon.py -f "Dark Reader"`
Once you restart Firefox, the addons will be there.
