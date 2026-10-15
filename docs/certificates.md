# Signing certificates

Most apps need nothing beyond what XLoader already installs. This page is for the ones that sign other apps themselves.

## The difference

When XLoader signs an app, it places a provisioning profile in it and gives it a valid signature. That is everything iOS needs, and it is enough for the app to install and launch.

Some apps do more. LiveContainer, for example, bundles ZSign, an IPA re-signing library, and will not use it until it holds a copy of your signing *identity* — your Apple Development certificate and private key, not the profile. That is a separate piece of information and a separate mechanism.

## Why it cannot go in the IPA

A private key inside an app bundle is readable by anyone who has the file. XLoader does not put one there.

The certificate is copied into the app's own container instead, after installation:

```bash
./xloader app.ipa --push ~/Downloads/your-cert.p12
```

The file lands in the app's Documents folder, which is visible in Finder or the Files app because these apps enable file sharing.

When the app being installed is LiveContainer, XLoader offers this automatically and can produce the certificate itself.

## There is no .p12 on your Mac

With a free Apple ID there is no `.p12` file anywhere to find. Xcode creates the certificate locally the first time it signs something and keeps the private key in your login keychain. Apple does not issue a downloadable certificate for free accounts, so there is nothing to look for.

XLoader takes it from the keychain:

```bash
./xloader --export-cert ~/Downloads/xloader.p12
```

This needs neither an IPA nor a connected device. It asks for a password and suggests one. Write it down, because the app asks for it during import. macOS may show a keychain permission prompt the first time; answer Always Allow.

## Checking the export

```bash
openssl pkcs12 -in xloader.p12 -info -nokeys -passin pass:YOURPASSWORD
```

The output should contain both a `friendlyName` and a `localKeyID`. A file exported from the certificate rather than the private key has no `localKeyID` and the app will reject it.

## Preferring Keychain Access

1. Open **Keychain Access**, and go to **My Certificates**.
2. Expand `Apple Development: <your account> (<ID>)`.
3. Select the **private key** underneath it.
4. **File → Export Items**, and choose the `.p12` format.

Exporting the private key rather than the certificate is the part that matters. Name the file something short; the default is full of spaces and colons.

## Two things about handling this file

**Delete it once the app has imported it.** It is your private key in a file, and by that point it also exists on your phone.

**`--export-cert` passes the password to `security` on the command line**, where macOS notes it is briefly visible in the process list. On a single-user Mac that is a reasonable trade for automation; on a shared machine, export from Keychain Access instead.

## The SideStore import path

LiveContainer can import a certificate directly from SideStore, which reads it from SideStore's shared App Group container. That requires the App Group `group.com.SideStore.SideStore`.

Free provisioning does not include App Group entitlements, so on a free Apple ID this path is unavailable. XLoader reports it on every run:

```text
app cannot use: healthkit, …, application-groups
```

A paid developer account with App Groups enabled on the App ID removes this restriction. The `--push` route does not go through App Groups, so it is the one to use on a free account.