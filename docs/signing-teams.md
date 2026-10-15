# Signing teams

A *team* is the 10-character identifier Apple gives every developer account. Free and paid accounts both have one, they are just different, and they are what a certificate and a provisioning profile belong to.

## Picking one

XLoader offers the teams it can find, in the order it prefers them:

1. **Teams signed in to Xcode**, by name. This is the authoritative list and includes accounts that have never signed anything.
2. **Teams from recent Xcode logins.** Xcode writes one Capabilities bundle per account; the newest one is usually the account you used last.
3. **Teams that already have a signing certificate in your keychain.**
4. **A team already used by something on the iPhone.**

A team with no certificate cannot sign anything, so those are ranked last unless nothing better turns up.

```text
which team signs this?
   1) XXXXXXXXXX  Personal Team · has a certificate (default)
   2) YYYYYYYYYY  Personal Team · has a certificate
   3) type another Team ID
   4) open the stub project in Xcode and pick it there
```

Press Enter to take the default. The choice is saved and reused, so this menu appears once.

## Changing it later

XLoader writes the team it selected into `stub/XLoaderStub.xcodeproj` and leaves that project alone afterwards. To change it:

1. Open `stub/XLoaderStub.xcodeproj` in Xcode.
2. Select the target `XLoaderStub` and open **Signing & Capabilities**.
3. Choose a different team.
4. Save.

XLoader reads that setting on every run, so the change sticks. This is also the way to pick a team it did not offer, without typing a Team ID by hand.

The team can be pinned from the command line as well:

```bash
./xloader app.ipa --team XXXXXXXXXX
```

## More than one Apple ID

If you have several Apple IDs in Xcode, each has its own team, and picking the wrong one signs the app as the wrong account. Two consequences worth knowing:

- **The App ID budget is per team.** Ten identifiers each, not ten in total.
- **An identifier signed by one team cannot be reused by another.** Switching teams means a new identifier, and therefore a separate install rather than an update. Your previous copy stays on the phone.

The name shown next to each team in the menu is the one Xcode recorded, which is usually the name on the account itself. If the names are similar, the Team ID is what distinguishes them.

## Finding a Team ID by hand

If you would rather not use Xcode:

- Xcode shows it under **Settings → Accounts**, next to your account.
- [developer.apple.com/account](https://developer.apple.com/account) → Membership shows the same value.
- `./xloader --list` marks apps signed by your team, and their identifiers contain it.

## Paid accounts

A paid developer account works the same way and is better on every axis: profiles last a year instead of seven days, the App ID limit is far higher, and capabilities like App Groups, push and HealthKit become available. XLoader does not care which kind of account it is signing with, and uses whichever team you select.