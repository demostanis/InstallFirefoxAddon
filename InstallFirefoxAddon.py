#!/usr/bin/env python3

"""
 TODO:
  - Add option to choose profile (and not loop through each)
  - Support IndexedDB
  - More verbosity
"""

import os
import io
import re
import sys
import json
import glob
import hashlib
import argparse
import urllib.request
import urllib.parse

from pathlib import Path

def find_download_link(contents):
    if match := re.search(r"(https://addons.mozilla.org\/firefox\/downloads\/file\/\d+\/.*\.xpi)..Download file", contents):
        return match.group(1)

def find_guid(contents):
    for line in contents.split(","):
        if match := re.search(r"^\"guid\":\"(.*)\"", line):
            return match.group(1)

def research(addon):
    lang = os.environ.get("LANG", "en_US") 
    req = urllib.request.urlopen(f"https://addons.mozilla.org/api/v4/addons/autocomplete/?q={urllib.parse.quote(addon)}&lang={lang}")
    return json.loads(req.read())

def input_for_addon(search_results, invalid_choice=False):
    if not invalid_choice:
        for i, addon in enumerate(search_results["results"]):
            print(f"{i}. " + addon["name"])

    if invalid_choice:
        text = "You didn't choose a valid addon, please try again: "
    else:
        text = "Please choose an addon to install: "

    choice = input(text)
    if choice.isdigit() and 0 <= int(choice) <= len(search_results["results"]):
        return search_results["results"][int(choice)]
    else:
        for result in search_results["results"]:
            if result["name"].lower() == choice.lower():
                return result
        input_for_addon(search_results, invalid_choice=True)

def process(addon):
    request = urllib.request.urlopen(addon["url"])
    contents = request.read().decode("utf-8")
    link = find_download_link(contents)
    guid = find_guid(contents)

    addon_xpi = urllib.request.urlopen(link)
    sha256sum = re.search(r"sha256:(.*)", urllib.parse.unquote(addon_xpi.url))
    addon_xpi = addon_xpi.read()

    m = hashlib.sha256(addon_xpi).hexdigest()
    if m == sha256sum.group(1):
        install(addon_xpi, guid)
    else:
        print("SHA256 sums don't match!")
        sys.exit(1)

def install(addon_xpi, guid):
    home = os.environ["HOME"]
    dest = glob.glob(f"{home}/.mozilla/firefox/**.default-release/")

    for profile in dest:
        Path(profile + "/extensions").mkdir(parents=True, exist_ok=True)
        with open(f"{profile}/extensions{guid}.xpi", "wb") as f:
            f.write(addon_xpi)
            f.close()

def read_database(addon):
    """
     We can't read IndexedDB storage yet,
     it is so fucking complex:
     https://stackoverflow.com/questions/22917139/how-can-i-access-firefoxs-internal-indexeddb-files-using-python
    """

    import sqlite3

    result = research(addon)["results"][0]
    request = urllib.request.urlopen(result["url"])
    contents = request.read().decode("utf-8")
    guid = find_guid(contents)

    home = os.environ["HOME"]
    profiles = glob.glob(f"{home}/.mozilla/firefox/**.default-release/")
    for profile in profiles:
        conn = sqlite3.connect(profile + "storage-sync-v2.sqlite")
        c = conn.cursor()
        c.execute("SELECT * FROM storage_sync_data")
        results = c.fetchall()

        for i, result_addon in enumerate(results):
            (addon_guid, data, _) = result_addon
            if addon_guid == guid:
                pretty_json = json.dumps(json.loads(data), indent=2)
                if sys.stdout.isatty():
                    print(f"{addon_guid}: \n" \
                        f"{pretty_json}\n" \
                        f"You can redirect this command output to {addon}.prefs.py\n" \
                        "to be able to reinstall this addon with the same preferences:\n" \
                        f"./{' '.join(sys.argv)} > {addon}.prefs.py")
                else:
                    print(f"storage({pretty_json})")
            elif i == len(results):
                print("Couldn't find addon, it either isn't installed or uses indexedDB.")
                sys.exit(1)

        conn.close()

def process_prefs(prefs_py, addon):
    def storage(prefs):
        import sqlite3

        result = research(addon)["results"][0]
        request = urllib.request.urlopen(result["url"])
        contents = request.read().decode("utf-8")
        guid = find_guid(contents)

        home = os.environ["HOME"]
        profiles = glob.glob(f"{home}/.mozilla/firefox/**.default-release/")
        for profile in profiles:
            conn = sqlite3.connect(profile + "storage-sync-v2.sqlite")
            c = conn.cursor()
            """
             CREATE TABLE storage_sync_data (
               ext_id TEXT NOT NULL PRIMARY KEY,
               data TEXT,
               sync_change_counter INTEGER NOT NULL DEFAULT 1
             );
            """
            c.execute("INSERT OR REPLACE INTO storage_sync_data VALUES (?,?,?)", (guid, json.dumps(prefs, separators=(",", ":")), 1))
            conn.commit()

    null = None
    true = True
    false = True
    with open(prefs_py) as f:
        eval(f.read())

def main():
    parser = argparse.ArgumentParser(description="Download and install Firefox Addons right from your shell")
    parser.add_argument("addon", type=str, help="Addon to install")
    parser.add_argument("-f", "--first", action="store_true")
    parser.add_argument("-r", "--readdb", action="store_true")
    parser.add_argument("-p", "--prefs")

    args = parser.parse_args()

    if args.readdb:
        read_database(args.addon)
    elif args.prefs:
        process_prefs(args.prefs, args.addon)
    else:
        search = research(args.addon) 
        choose_first = args.first

        if not len(search["results"]):
            print("No addons found.")
            sys.exit(1)

        if choose_first:
            process(search["results"][0])
        else:
            process(input_for_addon(search))

if __name__ == "__main__":
    main()

# vim:set ft=python ts=4 et:

