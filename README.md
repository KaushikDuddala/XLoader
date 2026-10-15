# XLoader

Install `.ipa` files on your own iPhone using your own Apple ID.

XLoader uses Xcode on your Mac to handle code signing, then re-signs the IPA with the signing assets Xcode generates. Everything runs locally, so there's no external signing server or account to register for. A free Apple ID works.

## Requirements

- macOS
- Full Xcode from the App Store, not just the Command Line Tools
- An iPhone connected over USB or Wi-Fi
- An Apple ID added to Xcode
- Python 3, which ships with macOS

Xcode 15 is the minimum version. No other dependencies need to be installed.

If Xcode has never been signed in to an Apple ID, XLoader will tell you and print setup instructions rather than failing partway through. The full walkthrough is in [docs/setup.md](docs/setup.md).

## Install

```bash
git clone https://github.com/KaushikDuddala/XLoader.git
cd XLoader
./xloader app.ipa
```

Running `./xloader` without an IPA asks for one, and you can drag the file into the terminal window.

## The three questions

XLoader asks you to pick a device, a signing team, and a bundle identifier. Each one comes with a default it has already detected, so you can usually press Enter through all three.

```text
which iPhone?
   1) Kindle Colorsoft  iOS 27.0 · USB · 00008150-00100D91028A401C (default)

which team signs this?
   1) XXXXXXXXXX  Personal Team · has a certificate (default)

install MyApp as which bundle identifier?
   1) XXXXXXXXXX.com.example.myapp  yours, always available, fresh install (default)
```

Your team choice is remembered between runs. If it picks the wrong one, see [docs/signing-teams.md](docs/signing-teams.md).

## Running it again

Free Apple IDs get provisioning profiles that expire after seven days. After that the app stops opening. Run the same command again with the same IPA: it mints fresh profiles and updates the app in place, keeping its data.

| Limit on a free account | |
|---|---|
| Profile lifetime | 7 days, refresh by re-running |
| Installed apps | 3 at a time, enforced by iOS |
| App IDs | 10 per team, reused when you reinstall the same app |

Features that need HealthKit, App Groups, push notifications, or keychain sharing don't work on a free account. Apps that use them still install and run; those specific features stay off.

## When something goes wrong

Start with [docs/troubleshooting.md](docs/troubleshooting.md). The three most common situations:

- **Nothing is found to install with.** Xcode has no Apple ID signed in, or the iPhone hasn't been registered with Apple yet. Both are covered in [docs/setup.md](docs/setup.md).
- **The app installs but won't launch.** An entitlement the free provisioning profile can't grant. The reason is printed by XLoader.
- **The identifier can't be registered.** Another team already owns it. XLoader normally retries with a different one and tells you which it used.

## More

| | |
|---|---|
| [docs/setup.md](docs/setup.md) | Requirements, signing in to Xcode, Developer Mode, registering a new iPhone |
| [docs/bundle-identifiers.md](docs/bundle-identifiers.md) | How identifiers are generated and validated, and why yours matters |
| [docs/signing-teams.md](docs/signing-teams.md) | Choosing a team, and using more than one Apple ID |
| [docs/options.md](docs/options.md) | Every command-line option, and `--list` |
| [docs/certificates.md](docs/certificates.md) | Exporting your signing identity for apps that sign other apps |
| [docs/development.md](docs/development.md) | Project layout and how the checks run |

## Credits

Based on code from [sidex](https://github.com/nodzen/sidex).

## License

MIT.