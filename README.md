# Install Firefox Addon
Python script to automatically install Firefox addons right from your shell

## Why? I have been digging since hours through the entire web and found out Ubuntu has a script doing the exact same.
For now, it does the same, albeit it uses AMO (addons.mozilla.org) search's API,
and can modify the SQLite database used for addons storage (not indexedDB, yet).

## Installation
This script depends on (unsurprinsingly) Firefox, and optionally sqlite3 from PyPI, for storage modification support.
You can download it using tools like `wget` or `curl`, chmod and execute it. The following lines do all this for you:
```sh
wget https://raw.githubusercontent.com/demostanis/InstallFirefoxAddon/main/InstallFirefoxAddon.py && \
chmod +x InstallFirefoxAddon.py && pip install sqlite3 && ./InstallFirefoxAddon.py --help
```

## Usage
Simply call the script with `<addon>` argument:
`./InstallFirefoxAddon.py "uBlock Origin"`

You will then be prompted to choose the correct addon between search results.

If you want not to be prompted and to automatically choose the first addon, use the `--first` option:
`./InstallFirefoxAddon.py -f "Dark Reader"`

Once you restart Firefox, the addons will be there.

To get current storage (often containing your settings) of an installed addon:
`./InstallFirefoxAddon.py -r "NoScript"`

This will show a large JSON dump.

If you redirect this command to a file, it will take `storage({...})` form, which can be understood by this script:
`./InstallFirefoxAddon.py -r NoScript > NoScript.prefs.py`

`cat NoScript.prefs.py # OUTPUT: storage({"policy/0":"..." ...})`

You can then use `--prefs` option to replace entries in the storage database by the ones in the file generated by the previous command:
`./InstallFirefoxAddon.py -p NoScript.prefs.py NoScript`

## License
Licensed under BSD-3-Clause.
