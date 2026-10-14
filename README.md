# XLoader

Install `.ipa` files on your own iPhone using your own Apple ID.

XLoader uses Xcode on your Mac to handle code signing, then re-signs the IPA with the signing assets Xcode generates. Everything runs locally, so there’s no external signing server or account to register for. A free Apple ID works.

```bash
git clone https://github.com/KaushikDuddala/XLoader.git
cd XLoader
./xloader app.ipa
```

XLoader asks you to choose a device, signing team, and bundle identifier. It suggests a default for each, so you can usually just press Enter.

## What it does

1. Finds connected iPhones and selects a device.
2. Detects your available development teams, preferring the one configured in Xcode.
3. Creates a temporary Xcode project for each bundle identifier that needs signing. Xcode uses this project to generate the signing certificate and provisioning profile.
4. Re-signs the app and its extensions, installs it using `devicectl`, and launches it.

The signed IPA is saved to `work/signed.ipa`.

## Using a free Apple ID

Apple allows free developer accounts to sign apps for personal devices, but the provisioning profiles expire after seven days. XLoader uses this signing process, so the usual free-account restrictions apply.

| Limit | Details |
|---|---|
| Profile lifetime | 7 days. Run XLoader again to refresh it. |
| Installed apps | Up to 3 apps per free team, enforced by iOS. |
| App IDs | Up to 10 per free team. Reinstalling the same app reuses its ID. |
| Capabilities | Limited to what the provisioning profile supports. |

Free provisioning only supports a limited set of entitlements. Features that require things like HealthKit, App Groups, push notifications, or keychain sharing won't work without the necessary entitlements. XLoader can still install an app that uses them, but those features may not work.

## Bundle identifiers

Your Team ID is the root of a namespace that Apple grants to your account, in the
same way that `TEAM.*` is a wildcard App ID you own. Anything below that root can
be registered by you, which is why XLoader puts your Team ID in front of the
original identifier:

```text
com.kdt.livecontainer -> XXXXXXXXXX.com.kdt.livecontainer
```

The original identifier stays readable at the end, so you can still tell which app
it is. To find your own Team ID, run `./xloader` and look at the team menu, or
check the name shown next to your account in Xcode under **Settings → Accounts**.

Putting the Team ID at the end instead — `com.kdt.livecontainer.XXXXXXXXXX` — fails
whenever the original developer has registered a wildcard App ID covering their own
namespace, which many apps with extensions do. Apple then refuses to register it:

> The app identifier "com.kdt.livecontainer.XXXXXXXXXX" cannot be registered to
> your development team because it is not available.

The generated identifier is consistent for the same app and team, so running XLoader again updates the existing installation instead of registering another App ID.

If the app is already installed under a different identifier, XLoader looks for it and offers to update it in place, preserving its app data.

### Use an identifier of your own

Signing under a bundle identifier that belongs to someone else's app is what gets developer accounts suspended. From Apple's side, an app signed by your account that claims to be a well-known app looks like an attempt to impersonate it, and popular identifiers are also the most heavily reported.

Let XLoader generate the identifier, or pass `--bundle-id` with one that starts with your Team ID. XLoader warns when the identifier you choose isn't namespaced to your team:

```text
'com.facebook.Facebook' is not namespaced to your team
an identifier you do not own can get the account suspended.
XXXXXXXXXX.com.example.app is the safe form.
```

Identifiers are checked before anything is sent to Apple: two or more dot-separated components of letters, digits and hyphens, each starting and ending with a letter or digit, 155 characters at most.

## Choosing a signing team

XLoader creates a project in `stub/` and stores the selected development team in its settings. The project is left in place, so you can change the team yourself if needed.

Open the project in Xcode:

```text
stub/XLoaderStub.xcodeproj
```

Go to **Signing & Capabilities**, select the team you want to use, and save the project. XLoader will use that team on subsequent runs.

This is useful if you have multiple Apple IDs configured in Xcode.

## List connected devices and installed apps

Run:

```bash
./xloader --list
```

Example output:

```text
devices
  + Kindle Colorsoft           iOS 27.0    USB       00008150-001A6C2602BA401C

installed on Kindle Colorsoft
  XXXXXXXXXX.com.kdt.livecontainer       LiveContainer      3.8.0 (yours)
  net.thunderbird.ios                    Thunderbird        1.0
```

Apps shown in cyan were installed by a developer and can be re-signed. The `(yours)` marker means the app was signed by XLoader.

## Command-line options

```text
-y, --yes           Skip prompts and use detected defaults
-l, --list          List connected devices and installed apps, then exit
    --device UDID   Use this device instead of prompting
    --team TEAM     Use this Team ID instead of prompting
    --bundle-id ID  Install using this exact bundle identifier
    --keep-watch    Keep the Apple Watch app in the IPA
```

The Watch app is removed by default because free developer accounts generally can't sign it. Leaving it in the IPA can cause installation to fail.

## Exporting your signing certificate

Some apps can sign other apps at runtime. LiveContainer, for example, includes ZSign and may need your signing identity to install or sign apps itself.

XLoader can copy a `.p12` certificate into an app's container:

```bash
./xloader app.ipa --push ~/Downloads/your-cert.p12
```

With a free Apple ID, Xcode keeps the signing private key in your login keychain, and Apple doesn't provide a downloadable certificate for this type of account. XLoader can export the signing identity for you:

```bash
./xloader --export-cert xloader.p12
```

Keep the exported file private. It contains sensitive signing material.

## Requirements

- macOS
- Full Xcode installation, not just the Command Line Tools
- An iPhone connected over USB or Wi-Fi
- An Apple ID added to Xcode
- Python 3, which is available with macOS

No additional dependencies need to be installed.

XLoader was developed and tested with Xcode 27. Xcode 15 is the minimum version because that's when `devicectl` was introduced.

## Troubleshooting

See `GUIDE.md` for the full troubleshooting guide. A few common issues:

- **The iPhone hasn't been registered with Apple yet:** Open `stub/XLoaderStub.xcodeproj`, select your team and the connected iPhone as the run destination, then press Run once. You only need to do this once per device.
- **No App IDs available:** You've reached the free team's limit of 10. Reinstall existing apps rather than creating new identifiers.
- **The app installs but won't launch:** Check the error printed by XLoader. On a free account, the problem is often an entitlement that the provisioning profile doesn't support.

## License

MIT.

## Project layout

```text
xloader                          Main script: arguments, menus, and workflow
lib/devicedb.py                  Queries devicectl and formats device information
lib/xcodeproj.py                 Reads and updates signing settings in the stub project
lib/sign.py                      Builds entitlements from provisioning profiles
lib/exportcert.py                Exports a signing identity from the keychain
template/XLoaderStub.xcodeproj   Blank project copied to stub/ on first run
template/src/                    Source files for the stub project
```

`stub/` and `work/` are created at runtime and aren't tracked by Git. You can edit files in `stub/`; `work/` is used for temporary files.

## Credits

Based on code from [sidex](https://github.com/nodzen/sidex). 