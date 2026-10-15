# Troubleshooting

## Setup and detection

| Symptom | Cause and fix |
|---|---|
| Xcode not found | Install the full Xcode application. The Command Line Tools are not sufficient. |
| Xcode 15 or newer is required | Update Xcode. That is the minimum because `devicectl` was introduced in 15. |
| Xcode has no Apple ID signed in | Xcode cannot issue signing assets. See [setup.md](setup.md#signing-in-to-xcode). XLoader prints these instructions itself rather than failing later. |
| No devices found | Cable or Wi-Fi, Trust accepted, phone unlocked. Wi-Fi pairing needs both devices on the same network. |
| Device shows `not connected` | The phone is asleep. It will wake during install, but unlocking it first is quicker. |
| Apple does not know this iPhone yet | Register the device once. See [setup.md](setup.md#registering-a-new-device). |

## Signing

| Symptom | Cause and fix |
|---|---|
| `not enough available app IDs` | Free teams get 10, and there is no interface for deleting them. Reinstall apps you already have rather than adding new ones. |
| `cannot be registered … not available` | Another team owns that identifier. XLoader retries with a different one and prints what it used. Repeated failures mean you have reached the App ID limit above. |
| `No Apple Development certificate for …` | Xcode has not created one yet. Open the stub project, set the team, choose the phone as the destination, press Run once. |
| Signing team is the wrong account | Pick it in `stub/XLoaderStub.xcodeproj` under Signing & Capabilities. See [signing-teams.md](signing-teams.md). |
| Another XLoader run is in progress | Wait for it. If nothing is running, delete `.xloader.lock`. |

## Running apps

| Symptom | Cause and fix |
|---|---|
| Installed, but iOS would not launch it | Read the reason XLoader prints. On a free account it is almost always an entitlement the provisioning profile cannot grant. |
| An app works but a widget or share extension does not | Same cause. The extension needs a capability free profiles cannot provide; the app itself is fine. |
| No notifications | Expected. Apple does not issue push entitlements to free accounts. |
| App stopped opening after a few days | The provisioning profile expired. Run the same command again. See the README. |
| App installed but shows as a second copy | It went in under a different identifier. Reinstall and choose the identifier already on the phone to replace it instead. |
| iOS refuses a fourth app | Free accounts keep about three sideloaded apps at once. Delete one on the phone. |

## Environments

| Symptom | Cause and fix |
|---|---|
| Beta iOS with a stable Xcode | Install the matching beta Xcode, `sudo xcode-select -s /Applications/Xcode-beta.app`, re-run. |
| Could not clear `work/` | Something holds a file there. Quit Xcode and delete the directory by hand. |
| Bundle identifier rejected by XLoader | See the validation rules in [bundle-identifiers.md](bundle-identifiers.md#validation). |
| Identifier warning about not being namespaced | See [bundle-identifiers.md](bundle-identifiers.md#use-an-identifier-of-your-own). |

## Getting more detail

XLoader prints Apple's own error text when signing fails, so the quickest route is usually to read the last few lines of the output. For anything about the code itself, the repository is at
[github.com/KaushikDuddala/XLoader](https://github.com/KaushikDuddala/XLoader).