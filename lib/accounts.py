#!/usr/bin/env python3
"""Read the Apple accounts and teams Xcode has been signed in to.

    teams    one row per team Xcode knows: Team ID, name, kind

XLoader needs this to pick a signing team, and to notice when Xcode has never
been signed in at all. Xcode keeps its state in com.apple.dt.Xcode; the useful
key is IDEProvisioningTeamByIdentifier, which records a team per signed-in
account along with a readable name and whether it is free provisioning.

Empty output means no Apple ID has been added to Xcode, which is the single most
common reason a first run fails.
"""

import plistlib
import subprocess
import sys

DOMAIN = "com.apple.dt.Xcode"
KEY = "IDEProvisioningTeamByIdentifier"


def teams():
    # `defaults read` prints its own hybrid format that is neither plist nor
    # JSON, so export the whole domain and pick the key out of a real plist.
    result = subprocess.run(
        ["defaults", "export", DOMAIN, "-"], capture_output=True
    )
    if result.returncode != 0 or not result.stdout:
        return []
    try:
        stored = plistlib.loads(result.stdout).get(KEY) or {}
    except Exception:
        return []

    found = []
    for entry in stored.values():
        for team in entry if isinstance(entry, list) else [entry]:
            if not isinstance(team, dict) or "teamID" not in team:
                continue
            found.append((
                team["teamID"],
                team.get("teamName") or team.get("teamType") or "unknown",
                "free" if team.get("isFreeProvisioningTeam") else "paid",
            ))
    return sorted(found)


def main(argv):
    if argv == ["teams"]:
        for team_id, name, kind in teams():
            print("\t".join([team_id, name, kind]))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])