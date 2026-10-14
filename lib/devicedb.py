#!/usr/bin/env python3
"""Ask devicectl about the iPhone and print plain TSV.

Every subcommand writes tab separated rows to stdout and nothing else, so the
shell script can consume them with `while IFS=$'\\t' read`.

    devices                  udid, name, os, state, transport
    apps UDID TEAM           bundle id, name, version, mine, kind
    find BUNDLE_ID           id of the already-installed copy of an app (reads apps TSV)
    teams                    team ids seen in installed bundle ids (reads apps TSV)

Errors are ignored on purpose: a phone that is asleep or half-paired should
degrade to an empty list rather than take the whole run down.
"""

import json
import re
import subprocess
import sys

PHYSICAL_UDID = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{16}$")
TEAM_IN_ID = re.compile(r"\.([A-Z0-9]{10})(\.|$)")
TRANSPORTS = {"wired": "USB", "sameMachine": "same Mac", "wireless": "Wi-Fi"}


def devicectl(*args):
    return subprocess.run(
        ["xcrun", "devicectl", *args, "-j", "/dev/stdout"],
        capture_output=True,
        text=True,
    ).stdout


def load_json(blob):
    try:
        return json.loads(blob)
    except ValueError:
        return {}


def cmd_devices(_args):
    rows = []
    for device in load_json(devicectl("list", "devices")).get("result", {}).get("devices", []):
        props = device.get("properties") or {}
        hardware, connection = props.get("hardware") or {}, props.get("connection") or {}
        udid = hardware.get("udid") or device.get("udid") or ""
        if not PHYSICAL_UDID.match(udid):
            continue  # simulators have UUIDs; you cannot install to them
        name = (device.get("deviceProperties") or {}).get("name") or hardware.get("marketingName") or "iPhone"
        components = (props.get("software") or {}).get("osVersionNumber", {}).get("components", [])
        os_version = "%s.%s" % tuple(components[:2]) if len(components) > 1 else "?"
        state = connection.get("state") or "unknown"
        rows.append({
            "connected": state == "connected",
            "name": name,
            "udid": udid,
            "os": os_version,
            "state": state,
            "transport": TRANSPORTS.get(connection.get("transportType") or "", ""),
        })
    rows.sort(key=lambda row: (not row["connected"], row["name"].lower()))
    for row in rows:
        print("\t".join([row["udid"], row["name"], row["os"], row["state"], row["transport"]]))


def cmd_apps(args):
    if len(args) != 2:
        sys.exit("usage: apps <udid> <team>")
    team = args[1]
    rows = []
    for app in load_json(devicectl("device", "info", "apps", "--device", args[0])).get("result", {}).get("apps", []):
        bundle_id = app.get("bundleIdentifier") or ""
        if not bundle_id:
            continue
        # Ids we sign come in three shapes, depending on how old they are:
        # TEAM.app (current), app.TEAM (XLoader 0.2 and older), or the
        # untouched original. All three have to count as ours.
        signed_by_us = bool(team) and (
            bundle_id.startswith(team + ".")
            or (".%s." % team) in bundle_id
            or bundle_id.endswith("." + team)
        )
        rows.append((
            bundle_id,
            app.get("name") or "?",
            app.get("version") or "?",
            "yes" if signed_by_us else "no",
            "dev" if app.get("builtByDeveloper") else "store",
        ))
    for row in sorted(rows):
        print("\t".join(row))


def cmd_find(args):
    """The installed copy of `want`, under any id scheme we have ever used."""
    want = args[0]
    for line in sys.stdin:
        bundle_id = line.split("\t")[0]
        if bundle_id == want or bundle_id.startswith(want + ".") or bundle_id.endswith("." + want):
            print(bundle_id)
            return


def cmd_teams(_args):
    seen = []
    for line in sys.stdin:
        match = TEAM_IN_ID.search(line.split("\t")[0])
        if match and match.group(1) not in seen:
            seen.append(match.group(1))
    print("\n".join(seen))


COMMANDS = {
    "devices": cmd_devices,
    "apps": cmd_apps,
    "find": cmd_find,
    "teams": cmd_teams,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    COMMANDS[sys.argv[1]](sys.argv[2:])