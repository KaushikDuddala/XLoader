#!/usr/bin/env python3
"""Turn freshly minted provisioning profiles into usable code signatures.

    app-id PROFILE                 bundle id a profile was minted for
    entitlements TEAM PROF APPDIR  write <binary>.entitlements.plist for the app
                                   and every embedded extension, then report what
                                   each signature will be limited to

The rule that makes side-loading work on a free account: the entitlements we
sign with are the ones the *profile* grants, never the ones the original app
asked for. A free profile grants four keys. Copying the app's own entitlements in
produces a signature iOS refuses to launch ("inadequate entitlements"), and it
only does so at launch, long after the install looked fine.
"""

import glob
import os
import plistlib
import re
import subprocess
import sys

APP_ID = re.compile(r"^[A-Z0-9]{10}\.")


def profile(path):
    """Decode a .mobileprovision (a CMS-signed plist) into a dict."""
    raw = subprocess.run(["security", "cms", "-D", "-i", path], capture_output=True).stdout
    return plistlib.loads(raw)


def app_id(path):
    print((profile(path).get("Entitlements") or {}).get("application-identifier", ""))


def original_entitlements(binary):
    """What the IPA's own signature asked for, or {} when it is not signed."""
    raw = subprocess.run(
        ["codesign", "-d", "--entitlements", ":-", binary], capture_output=True
    ).stdout
    if not raw.lstrip().startswith(b"<?xml"):
        return {}
    try:
        return plistlib.loads(raw)
    except Exception:
        return {}


def readable_name(key):
    """com.apple.developer.healthkit -> healthkit, for messages a person reads."""
    for prefix in ("com.apple.developer.", "com.apple.security."):
        if key.startswith(prefix):
            return key[len(prefix):]
    return key


def binaries(app_dir):
    """The app itself, then its extensions, so signing can go inside-out."""
    extensions = sorted(glob.glob(os.path.join(app_dir, "PlugIns", "*.appex")))
    return [(app_dir, "app")] + [
        (path, os.path.basename(path)[: -len(".appex")]) for path in extensions
    ]


def entitlements(team, profile_dir, app_dir):
    for binary, name in binaries(app_dir):
        path = os.path.join(profile_dir, name + ".mobileprovision")
        try:
            result = dict(profile(path)["Entitlements"])
        except Exception as error:                    # missing or truncated file
            sys.exit("error: no usable profile for %s (%s): %s" % (name, path, error))

        original = original_entitlements(binary)

        # Mirror the app's keychain groups only when the profile names specific
        # ones. A wildcard "TEAM.*" cannot back a list of explicit groups, and
        # declaring them anyway is what gets the app rejected at launch.
        allowed = result.get("keychain-access-groups", [])
        if allowed and not any(g.endswith(".*") for g in allowed) and "keychain-access-groups" in original:
            result["keychain-access-groups"] = [
                re.sub(APP_ID, team + ".", group)
                for group in original["keychain-access-groups"]
            ]

        with open(binary + ".entitlements.plist", "wb") as handle:
            plistlib.dump(result, handle)

        # Report what the app wanted but the profile will not grant, so the
        # features that end up switched off are a known quantity.
        dropped = sorted(key for key in original if key not in result)
        readable = [readable_name(key) for key in dropped]
        print("\t".join([
            name,
            str(result.get("application-identifier", "?")).split(".", 1)[-1],
            ", ".join(readable) or "-",
        ]))


def main(argv):
    if len(argv) == 2 and argv[0] == "app-id":
        app_id(argv[1])
    elif len(argv) == 4 and argv[0] == "entitlements":
        entitlements(argv[1], argv[2], argv[3])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])