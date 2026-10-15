# Bundle identifiers

An app from the App Store owns its bundle identifier outright. Your copy cannot use the same one, so it has to be renamed before it can be signed.

## How XLoader generates one

Your Team ID is the root of a namespace Apple grants to your account, the same way `TEAM.*` is a wildcard App ID you own. Anything underneath that root is available for you to register, which is why XLoader puts your Team ID in front of the original identifier:

```text
com.kdt.livecontainer   ->   XXXXXXXXXX.com.kdt.livecontainer
```

The original identifier stays readable at the end, so you can still tell which app it is.

To find your own Team ID, run XLoader and read the team menu, or look at the value Xcode shows next to your account under **Settings → Accounts**.

## Why not the other way round

Appending the Team ID instead, `com.kdt.livecontainer.XXXXXXXXXX`, fails whenever the original developer has registered a wildcard App ID covering their own namespace. Many apps with extensions do exactly that. Every child identifier under their wildcard then belongs to them, and Apple refuses to register it for you:

> The app identifier "com.kdt.livecontainer.XXXXXXXXXX" cannot be registered to
> your development team because it is not available.

XLoader treats this particular error as recoverable and retries with a different identifier, printing the one it settled on.

## Reinstalling keeps the same identifier

The generated identifier is a pure function of the original identifier and your team, so running XLoader twice on the same IPA produces the same result. That matters because your free team only gets 10 App IDs: re-running updates the existing installation instead of consuming another one.

If the app is already installed under a different identifier, XLoader finds it by looking for any installed identifier related to the original one, and offers to update it in place. Updating under the same identifier replaces the app and keeps its data; choosing the generated identifier instead installs a second, separate copy.

Extensions get identifiers underneath the app's own, so they continue to resolve correctly.

## Use an identifier of your own

You can supply an identifier with `--bundle-id`, or type one at the bundle identifier prompt.

Keep the generated identifier, or use one that starts with your Team ID. Signing under an identifier that belongs to another app is a common reason developer accounts get suspended: an app signed by your account that presents itself as a well-known app reads as an impersonation attempt, and identifiers belonging to popular apps attract the most reports.

XLoader prints a warning if the identifier you choose isn't namespaced to your team:

```text
'com.example.somethingelse' is not namespaced to your team
an identifier you do not own can get the account suspended.
XXXXXXXXXX.com.example.app is the safe form.
```

This applies wherever the identifier comes from, including an identifier belonging to another app you installed earlier. Deliberately replacing an installation under an identifier your team already signed is namespaced, so no warning appears.

## Validation

Identifiers are checked before anything is sent to Apple, so a bad one fails immediately instead of several minutes into the signing process.

An identifier is accepted when it is at most 155 characters and consists of two or more dot-separated components, each made of letters, digits and hyphens and each starting and ending with a letter or digit.

| Example | Result |
|---|---|
| `com.example.app` | accepted |
| `XXXXXXXXXX.com.example.app` | accepted |
| `a.b` | accepted |
| `com.example.my-app.2` | accepted |
| `example` | rejected, needs two components |
| `com..example` | rejected, empty component |
| `com.example.app_name` | rejected, underscore |
| `com.example.my app` | rejected, space |
| `-com.example.app` | rejected, leading hyphen |
| `com.example.app-` | rejected, trailing hyphen |

The same check is applied to the identifier the IPA itself declares and to each of its extensions. An extension with an unusable identifier is skipped with a note rather than failing the whole install.