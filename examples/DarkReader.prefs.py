# Calling ./InstallFirefoxAddon.py -p examples/DarkReader.prefs.py "Dark Reader"
# imports this file and executes the storage function, which replaces Dark Reader's
# storage (preferences) by the ones in this file. Thus, once Firefox will be fired up,
# Dark Reader will have brightness set at 75 and won't change browser theme.

storage({
  "theme": {
     "brightness": 75
  },
  "changeBrowserTheme": false
})

# vim:set ft=python:
