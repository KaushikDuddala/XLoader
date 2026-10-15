# Development

## Layout

```text
xloader                          Main script: arguments, menus, and workflow
lib/accounts.py                  Teams Xcode is signed in to
lib/devicedb.py                  Queries devicectl and formats device information
lib/xcodeproj.py                 Reads and updates signing settings in the stub project
lib/sign.py                      Builds entitlements from provisioning profiles
lib/exportcert.py                Exports a signing identity from the keychain
template/XLoaderStub.xcodeproj   Blank project copied to stub/ on first run
template/src/                    Source files for the stub project
docs/                            Documentation linked from the README
```

`stub/` and `work/` are created at runtime and aren't tracked in Git. See [options.md](options.md#the-stub-project-and-work-directory).

## Why there is a Python helper per concern

XLoader is a single shell script with several small Python modules next to it. The split is deliberate:

- **`devicedb.py`** owns everything that talks to `devicectl` and nothing else. It prints tab-separated rows and exits quietly if a phone is asleep or half-paired, so a device problem degrades to an empty list instead of stopping the run.
- **`sign.py`** owns the rule that matters most: entitlements come from the provisioning profile, never from the original app. A free profile grants four keys; copying the app's own entitlements in produces a signature iOS accepts on install and refuses to launch.
- **`xcodeproj.py`** reads and writes two settings in the stub project, and treats a value containing `__` as unset, which is how the template marks "not configured yet".
- **`accounts.py`** reads Xcode's preferences to find the teams you are signed in to. `defaults read` prints a format that is neither plist nor JSON, so this exports the domain and parses a real plist.
- **`exportcert.py`** is separate because it has two non-obvious problems of its own, both documented in its docstring.

Everything the shell script does is orchestration and prompting. Logic that benefits from being read, tested or reasoned about on its own lives in Python.

## Checks

`.github/workflows/ci.yml` runs on every push:

```bash
bash -n xloader
shellcheck -s bash xloader
python3 -m py_compile lib/*.py
plutil -lint template/XLoaderStub.xcodeproj/project.pbxproj
```

ShellCheck runs at its default severity, which includes style and informational findings. Treat those as failures rather than filtering them out.

To run them locally without the CI:

```bash
bash -n xloader
shellcheck -s bash xloader          # brew install shellcheck
python3 -m py_compile lib/*.py
plutil -lint template/XLoaderStub.xcodeproj/project.pbxproj
```

## Portability notes

The script targets the bash that ships with macOS, which is 3.2. Two things in that version are worth remembering:

- `set -u` makes `"${array[@]}"` an error when the array is empty. Every expansion of an array that might be empty is guarded.
- Lowercase expansion (`${var,,}`) does not exist. Use `tr '[:upper:]' '[:lower:]'`.

## The stub template

`template/` holds the blank Xcode project XLoader copies to `stub/`. It carries a `__TEAM__` placeholder rather than a real Team ID, so nothing personal is committed.

If you change the template, bump `TEMPLATE_VERSION` in `xloader`. That makes XLoader refresh the copy in `stub/` once, while preserving the team and bundle identifier you set in Xcode.

## Testing against a real device

Most of the interesting behaviour only shows up against a real iPhone:

- Install and launch something end to end.
- Run with a device that has never been paired, to see the registration message.
- Run with no Apple ID signed in, to check the setup instructions.
- Try an IPA with extensions, since each one needs its own profile.