# Setup

Everything that has to happen before XLoader can sign anything.

## Requirements

| | |
|---|---|
| macOS | Any version that runs Xcode 15 or newer |
| Xcode | The full application from the App Store. The Command Line Tools are not sufficient, because XLoader drives Xcode itself |
| iPhone | Connected over USB, or paired over Wi-Fi |
| Apple ID | Added to Xcode. A free account is fine |
| Python 3 | Ships with macOS |

XLoader was developed and tested against Xcode 27. The floor is 15, which is where `devicectl` was introduced. Older syntax may behave differently; if an install succeeds but the app will not launch, that is the first thing to check.

## Installing Xcode

1. Install Xcode from the App Store and open it once.
2. Let it finish setting itself up before continuing. The first launch takes a while and leaves the app partly configured; quitting early is a common cause of the next step failing.

## Signing in to Xcode

Xcode needs an Apple ID before it can issue a signing certificate or a provisioning profile. Both are per team, and a free account gets its own team automatically.

Open Xcode, go to **Settings → Accounts**, click the `+` button, and choose **Apple ID**.

Sign in with every Apple ID you might want to sign with. Xcode keeps them side by side, each with its own team, and XLoader offers all of them in the team menu by name. This matters if you have more than one account; see [signing-teams.md](signing-teams.md).

XLoader checks for this before it starts and prints these instructions if no account is present, rather than failing several minutes in.

## Developer Mode

The iPhone requires Developer Mode for anything that did not come from the App Store.

On the phone: **Settings → Privacy & Security → Developer Mode**, and turn it on. The phone restarts afterwards and asks you to confirm.

This is a one-time setting per phone, not per app.

## Connecting the iPhone

Plug it in over USB and tap **Trust** when the phone asks. Leave the phone unlocked while XLoader is running, because a locked phone answers queries slowly or not at all, and `devicectl` needs to wake the device to install.

For Wi-Fi, pair once over USB with the phone unlocked. After that both devices need to be on the same network.

Check the connection at any time:

```bash
./xloader --list
```

Your device should appear with `connected` next to it. If it shows `not connected`, the phone is asleep or the cable is not making contact.

## Registering a new device

The first time you use a particular iPhone with a particular team, Apple has not registered the pairing and will refuse to issue a profile. XLoader stops with a message like this:

```text
error: Apple does not know 00008150-... for your team yet.

  Open .../stub/XLoaderStub.xcodeproj in Xcode, set your Team under Signing &
  Capabilities, choose Kindle Colorsoft as the destination, press Run once,
  then try again.
```

To register the device:

1. Open `stub/XLoaderStub.xcodeproj` in Xcode. XLoader created it on the first run.
2. Select the target `XLoaderStub` and open **Signing & Capabilities**.
3. Choose your team.
4. Pick the iPhone in the destination menu at the top of the Xcode window.
5. Press Run.

Xcode builds and installs the blank app, which registers the pairing with Apple. This happens once per device and team combination. It is not related to any particular app you are installing.

## Checking the setup

```bash
./xloader --list
```

If your device is listed and connected, the basics are working and you can install something.