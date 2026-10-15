# Command-line options

```text
-y, --yes           Skip prompts and use detected defaults
-l, --list          List connected devices and installed apps, then exit
    --device UDID   Use this device instead of prompting
    --team TEAM     Use this Team ID instead of prompting
    --bundle-id ID  Install using this exact bundle identifier
    --push FILE     Copy FILE into the app's Documents folder after install
    --export-cert FILE    Write the signing identity for this team to FILE as a .p12
    --export-password PW  Password for --export-cert
    --keep-watch    Keep the Apple Watch app in the IPA
```

`./xloader --help` prints the same list.

Prompts fall back to their defaults whenever XLoader is not attached to a terminal, so the same command works from a script or a scheduled job. `-y` forces that behaviour even when you are at a terminal.

## --list

Shows every device Xcode knows about, and everything installed on the ones that are connected.

```bash
./xloader --list
```

```text
devices
  + Kindle Colorsoft           iOS 27.0    USB       00008150-00100D91028A401C

installed on Kindle Colorsoft
  XXXXXXXXXX.com.kdt.livecontainer       LiveContainer      3.8.0 (yours)
  net.thunderbird.ios                    Thunderbird        1.0
```

- `+` means connected, `-` means Xcode knows about it but it is not reachable.
- Apps printed in cyan were installed by a developer, which means they can be re-signed.
- `(yours)` means the identifier contains your Team ID, so XLoader signed it.

This is also the quickest way to check whether XLoader can see your iPhone at all, which is worth doing before [registering a new device](setup.md#registering-a-new-device).

## --device, --team, --bundle-id

Each one skips the corresponding prompt.

```bash
./xloader app.ipa --device 00008150-00100D91028A401C
./xloader app.ipa --team XXXXXXXXXX
./xloader app.ipa --bundle-id XXXXXXXXXX.com.example.app
```

`--team` also writes the value to the stub project, so it becomes the default for later runs.

`--bundle-id` is used exactly as given, without any namespacing. See [bundle-identifiers.md](bundle-identifiers.md) for why the Team ID belongs at the front.

## --keep-watch

The Watch app is removed from the IPA by default. Free accounts cannot sign it, and leaving it in place makes the install fail. Use this to keep it, which matters only if you have an account that can sign it.

## --push and --export-cert

Both are for apps that need something extra at runtime, such as a signing certificate. See [certificates.md](certificates.md).

## The stub project and work directory

XLoader keeps two directories next to the script, neither of which is tracked in Git:

| | |
|---|---|
| `stub/` | The throwaway Xcode project used to produce signing assets. Created once, then left alone, so your team choice survives. Safe to edit in Xcode. Deleting it is harmless; it is recreated. |
| `work/` | Scratch space, rebuilt on every run. Holds the unpacked IPA and the signed output at `work/signed.ipa`. |

Two XLoader runs cannot share `work/`, so a second run refuses to start while the first is in progress. If a run was killed and left the lock behind, delete `.xloader.lock`.