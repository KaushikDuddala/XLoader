#!/usr/bin/env python3
"""Read and write signing settings in the stub Xcode project.

XLoader keeps a throwaway Xcode project around so that the team you pick in the
Xcode GUI is the team it uses on every later run. The only settings it ever reads
or writes are the two that make the project's Signing tab valid:

    get PBXPROJ KEY          e.g. get pbxproj DEVELOPMENT_TEAM
    set PBXPROJ KEY VALUE    e.g. set pbxproj DEVELOPMENT_TEAM ABCDE12345

Values containing `__` are how the shipped template marks "not configured yet",
and are reported as empty so callers can treat them as unset.
"""

import re
import sys

ASSIGNMENT = r'(%s\s*=\s*)"?[^";]*"?(\s*;)'
FALLBACK_ANCHOR = "\t\t\t\tCODE_SIGN_STYLE = Automatic;"
TEAM_ID = re.compile(r"^[A-Z0-9]{10}$")
BUNDLE_ID = re.compile(r"^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def get(path, key):
    match = re.search(r"\b" + key + r'\s*=\s*"?([^";]*)"?\s*;', read(path))
    value = match.group(1).strip() if match else ""
    # `__TEAM__` is how the shipped template marks "not configured yet", and a
    # malformed id is exactly what makes Xcode's Signing tab light up red.
    if "__" in value or not (TEAM_ID.match(value) or BUNDLE_ID.match(value)):
        value = ""
    print(value)


def set_value(path, key, value):
    text = read(path)
    if re.search(r"\b" + key + r"\s*=", text):
        text = re.sub(ASSIGNMENT % key, lambda m: m.group(1) + value + m.group(2), text)
    else:
        text = text.replace(FALLBACK_ANCHOR, "%s\n\t\t\t\t%s = %s;" % (FALLBACK_ANCHOR, key, value))
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def main(argv):
    if len(argv) == 3 and argv[0] == "get":
        get(argv[1], argv[2])
    elif len(argv) == 4 and argv[0] == "set":
        set_value(argv[1], argv[2], argv[3])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])