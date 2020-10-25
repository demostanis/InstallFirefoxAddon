#!/usr/bin/env python3

import os
import io
import re
import sys
import json
import uuid
import glob
import hashlib
import argparse
import urllib.request
import urllib.parse

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
    dest = glob.glob(f"{home}/.mozilla/firefox/**.default-release/extensions/")

    for profile in dest:
        with open(profile + guid + ".xpi", "wb") as f:
            f.write(addon_xpi)
            f.close()

def main():
    parser = argparse.ArgumentParser(description="Download and install Firefox Addons right from your shell")
    parser.add_argument("addon", type=str, help="Addon to install")
    parser.add_argument("-f", "--first", action="store_true")

    args = parser.parse_args()
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

