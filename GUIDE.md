# XLoader guide

Setup instructions, background information, and a troubleshooting reference. The
[README](README.md) covers what the tool does; this file covers what to do when
something doesn't work as expected.

## Before the first run

XLoader drives Xcode, so Xcode has to be installed and configured first.

1. Install Xcode from the App Store and open it once. It is a large download and
   it runs some setup on first launch.
2. Add your Apple ID in Xcode under **Settings → Accounts**. Any Apple ID works.
3. Connect the iPhone over USB and tap **Trust** when prompted. Keep the phone
   unlocked while XLoader is running; a locked phone often fails to answer
   queries.
4. Enable Developer Mode on the iPhone under **Settings → Privacy & Security →
   Developer Mode**. This is required for anything that didn't come from the App
   Store. The phone restarts after you turn it on.

Check the setup with:

```bash
./xloader --list
```

If your device appears in the output, the basics are working.

## Running XLoader

```bash
./xloader /path/to/app.ipa
```

Running it without arguments asks for an IPA path, and you can drag the file into
the terminal window.

XLoader then asks three questions. Each one shows a default it has already
detected, so pressing Enter accepts it.

**Which iPhone?** All devices Xcode knows about, with connected devices listed
first. The display shows the model name, iOS version, connection type, and UDID.
If a device you just plugged in isn't listed, choose *scan again*.

**Which team signs this?** The teams XLoader can find, with a description of where
each one was detected. The entry marked with the signing certificate is usually
the right one. The choice is saved and reused on later runs.

**Install as which bundle identifier?** See the section below.

After that XLoader mints the profiles, signs the app, installs it, and launches
it. Most of the time is spent waiting on Apple.

## Bundle identifiers

An app from the App Store owns its bundle identifier outright. Your copy can't
use the same one, so it has to be renamed. XLoader uses your Team ID as the
prefix:

```text
com.kdt.livecontainer   ->   XXXXXXXXXX.com.kdt.livecontainer
```

Your Team ID is the root of a namespace Apple grants to your account, so every
identifier underneath it is available for you to register. That is the reason for
the prefix: it puts the identifier somewhere you own instead of somewhere the
original developer may already have claimed with a wildcard App ID.

To find your Team ID, open the stub project and look at **Signing & Capabilities**,
or run `./xloader` and read the team menu. Xcode shows the same value next to your
account under **Settings → Accounts**.

Extensions get identifiers underneath the app's own, so they continue to resolve
correctly.

Two additional options appear in that menu when they apply:

- **An identifier already on this iPhone.** If the app is installed under some
  identifier, XLoader offers that one first. Reinstalling under the same
  identifier replaces the existing app and keeps its data. Choosing the new
  identifier instead installs a second, separate copy.
- **Replace another app.** Identifiers XLoader has used before for other apps.
  Selecting one installs this IPA over that app in place, which is useful when
  you deliberately want to replace an existing installation.

You can also type an identifier yourself. XLoader validates it before use: two or
more dot-separated components of letters, digits and hyphens, each starting and
ending with a letter or digit, 155 characters at most. The same check is applied
to the identifier the IPA declares, so a malformed one fails immediately instead
of several minutes into the signing process.

## Using an identifier of your own

Keep the generated identifier, or supply one that starts with your Team ID. Signing
under an identifier that belongs to another app is a common reason developer
accounts get suspended: an app signed by your account that presents itself as a
well-known app looks like an impersonation attempt to Apple, and identifiers
belonging to popular apps attract the most reports.

XLoader prints a warning if the identifier you select isn't namespaced to your
team:

```text
'com.example.somethingelse' is not namespaced to your team
an identifier you do not own can get the account suspended.
XXXXXXXXXX.com.example.app is the safe form.
```

This applies whether the identifier comes from `--bundle-id`, from the menu, or
from another app you installed earlier. If you deliberately choose to replace an
existing installation under an identifier your team already signed, that
identifier is already namespaced and no warning appears.

## The stub project

`stub/XLoaderStub.xcodeproj` is a blank Xcode application. Its only job is to give
Xcode something to build, because Xcode will only issue signing certificates and
provisioning profiles from a real project.

The project is created on the first run and then left alone. XLoader writes the
selected team into its settings, so opening it in Xcode shows a valid team rather
than an empty one.

There are two reasons to open it yourself:

1. **Changing the team.** Select the target, open **Signing & Capabilities**, and
   choose a different team. Save the project. XLoader reads the setting on every
   run.
2. **Registering a new device.** See the next section.

Deleting the `stub/` directory is safe. XLoader recreates it from `template/` on
the next run, and will ask which team to use again.

## Registering a new device

The first time you use a particular iPhone with a particular team, Apple has not
registered the pairing and will refuse to issue a profile. XLoader stops with a
message like this:

```text
error: Apple does not know 00008150-... for your team yet.

  Open .../stub/XLoaderStub.xcodeproj in Xcode, set your Team under Signing &
  Capabilities, choose Kindle Colorsoft as the destination, press Run once,
  then try again.
```

To register the device, open the stub project, pick the iPhone in the destination
menu at the top of the Xcode window, and press Run. Xcode builds and installs the
blank app, which registers the pairing with Apple.

This only needs to be done once per device and team combination. It is not
related to any particular app.

## Refreshing an installation

Provisioning profiles are valid for seven days. After that the app stops opening.
This is Apple's rule for every free signing method and not something specific to
XLoader.

Run XLoader again with the same IPA. It mints fresh profiles, re-signs the app,
and installs it over the existing copy. The bundle identifier is unchanged, so
the app's data is preserved.

## Command-line options

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

`--push` can be given more than once. It is intended for apps that need extra
files at runtime, such as a signing certificate.

## Apps that sign other apps

Some apps re-sign IPAs themselves. LiveContainer includes ZSign, an IPA
re-signing library, and will not use it until it has a copy of your signing
identity. That is a different thing from the provisioning profile XLoader already
places in the app, and it cannot be placed in the `.ipa` bundle: a private key
inside a bundle is readable by anyone who has the file.

XLoader copies the file into the app's container instead:

```bash
./xloader app.ipa --push ~/Downloads/your-cert.p12
```

If the app is LiveContainer, XLoader offers this automatically after installing
and can produce the certificate itself.

## Exporting a certificate

With a free Apple ID there is no `.p12` file anywhere on your Mac. Xcode creates
the certificate locally the first time it signs something and keeps the private
key in your login keychain. Apple does not issue a downloadable certificate for
free accounts, so there is nothing to look for.

XLoader can export it:

```bash
./xloader --export-cert ~/Downloads/xloader.p12
```

This does not need an IPA or a connected device. It asks for a password and
suggests one; write it down, because the app will ask for it during import.
macOS may show a keychain permission prompt the first time. Choose Always Allow.

To verify the result before using it:

```bash
openssl pkcs12 -in xloader.p12 -info -nokeys -passin pass:YOURPASSWORD
```

The output should contain both a `friendlyName` and a `localKeyID`. A file
exported from the certificate rather than the private key has no `localKeyID` and
the app will reject it.

If you would rather use Keychain Access, the steps are: open **My Certificates**,
expand `Apple Development: <your account>`, select the **private key** underneath,
then **File → Export Items** and choose the `.p12` format.

Delete the exported file once the app has imported it. It contains your private
key, and by that point it also exists on your phone.

## Limitations of the SideStore import path

LiveContainer can import a certificate directly from SideStore, which reads it
from SideStore's shared App Group container. That requires the App Group
`group.com.SideStore.SideStore`, and free provisioning does not include App Group
entitlements.

On a free Apple ID this path is therefore unavailable, and XLoader reports it on
every run:

```text
app cannot use: healthkit, …, application-groups
```

A paid developer account with App Groups enabled on the App ID removes this
restriction.

## Troubleshooting

| Symptom | Resolution |
|---|---|
| Xcode not found | Install the full Xcode application. The Command Line Tools are not sufficient. |
| Xcode 15 or newer is required | Update Xcode. The minimum is 15 because `devicectl` was introduced in that version. |
| No devices found | Check the cable or Wi-Fi connection, confirm Trust was accepted, and unlock the phone. Wi-Fi pairing requires both devices on the same network. |
| Apple does not know this iPhone yet | Register the device. See the section above. Required once per device. |
| not enough available app IDs | Free teams are limited to 10 App IDs and there is no interface for deleting them. Reinstall existing apps instead of creating new identifiers. |
| cannot be registered … not available | The identifier is already owned by another team. XLoader retries with a different identifier and prints the one it used. Repeated failures mean you have reached the App ID limit above. |
| Installed, but iOS would not launch it | Read the reason XLoader prints. On a free account it is usually an entitlement the profile cannot grant. |
| An app installs but a widget or share extension does not work | The extension needs a capability that free profiles cannot provide. The app itself works. |
| No notifications | Expected. Apple does not issue push entitlements to free accounts. |
| Beta iOS with a stable Xcode | Install the matching beta Xcode, switch with `sudo xcode-select -s`, and run again. |
| Another XLoader run is in progress | Wait for it to finish. If no run is active, delete the `.xloader.lock` directory. |
| Could not clear work/ | A file in the directory is in use. Quit Xcode and delete `work/` manually. |

## Notes

**Three app limit.** iOS allows a free account to keep about three sideloaded
apps installed at a time and refuses a fourth. Delete an app on the phone and try
again.

**Warranty.** Installing apps this way does not affect your warranty. It is
standard free-tier development signing, the same process Xcode uses for apps you
build yourself.

**Platform.** macOS only, because XLoader uses Xcode directly. There is no
Windows or Linux version.