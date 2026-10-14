#!/usr/bin/env python3
"""Export one signing identity from the keychain as a PKCS#12 file.

    exportcert.py --identity NAME --password PW --out FILE [--keychain PATH]

Xcode never writes a .p12 to disk: for a free Apple ID the certificate and its
private key are created locally and live only in the login keychain, which is why
"where is the p12" has no answer. Keychain Access can export one by hand, but this
does it without the GUI.

Two things make it less obvious than it looks:

* `security export` writes PKCS#12 using RC2-40, which OpenSSL 3 refuses to read
  unless `-legacy` is passed. Everything is unwrapped to PEM and repacked with
  AES, so the result is readable by anything — including the re-signers in tools
  like LiveContainer.
* The certificate's name and the private key's name are *different* items in the
  keychain, so "export the identity called X" cannot mean "take the two blocks
  with the same name". They are paired by their public key instead.

The output file contains a private key. It is written 0600 and the intermediate
copies are removed.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

CERT = re.compile(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", re.S)
KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S)
NAME = re.compile(r'friendlyName: "?([^"\n]+)"?')


def run(*args, **kwargs):
    return subprocess.run(args, capture_output=True, text=True, **kwargs)


def openssl(*args):
    result = run("openssl", "pkcs12", *args)
    return result


def public_key(block):
    """The public key of a certificate or private key, as DER text."""
    if block.startswith("-----BEGIN CERTIFICATE"):
        cmd = ("openssl", "x509", "-pubkey", "-noout")
    else:
        cmd = ("openssl", "pkey", "-pubout")
    result = run(*cmd, input=block)
    return result.stdout if result.returncode == 0 else None


def extract(path, password):
    """Unwrap Apple's export into a PEM bundle, with and without -legacy."""
    for extra in (["-legacy"], []):
        result = openssl("-in", path, "-passin", "pass:" + password,
                         "-nodes", "-out", "-", *extra)
        if result.returncode == 0 and "BEGIN CERTIFICATE" in result.stdout:
            return result.stdout
    return None


def select(bundle, wanted):
    """Return (cert_pem, key_pem) for the identity named `wanted`."""
    blocks = []
    current_name = None
    for line in bundle.splitlines():
        found = NAME.search(line)
        if found:
            current_name = found.group(1)
            continue
        if line.startswith("-----BEGIN"):
            blocks.append([current_name, [line]])
        elif blocks:
            blocks[-1][1].append(line)
        elif current_name and line.strip():
            current_name = line.strip()

    blocks = [(name, "\n".join(lines)) for name, lines in blocks if name]
    certs = [b for b in blocks if b[1].startswith("-----BEGIN CERTIFICATE")]
    keys = [b for b in blocks if "PRIVATE KEY-----" in b[1].split("\n")[0]]

    key_pubkeys = {}
    for _, block in keys:
        pub = public_key(block)
        if pub:
            key_pubkeys.setdefault(pub, block)

    for name, cert in certs:
        if wanted not in name:
            continue
        pub = public_key(cert)
        if pub in key_pubkeys:
            return cert, key_pubkeys[pub]
    return None, None


def main():
    try:
        run_export()
    except OSError as error:
        sys.exit("error: %s" % error)


def run_export():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--identity", required=True, help="certificate name, e.g. Apple Development: you@example.com (AB12CD34EF)")
    parser.add_argument("--password", required=True, help="password for the .p12")
    parser.add_argument("--out", required=True)
    parser.add_argument("--keychain",
                        default=os.path.expanduser("~/Library/Keychains/login.keychain-db"))
    args = parser.parse_args()

    if not os.path.exists(args.keychain):
        sys.exit("error: no such keychain: %s" % args.keychain)

    scratch = tempfile.mkdtemp(prefix="xloader-cert-")
    try:
        os.chmod(scratch, 0o700)
        everything = os.path.join(scratch, "keychain.p12")
        result = run("security", "export", "-k", args.keychain,
                     "-t", "identities", "-f", "pkcs12",
                     "-P", args.password, "-o", everything)
        if result.returncode != 0 or not os.path.exists(everything):
            sys.exit("error: security export failed: %s" % result.stderr.strip())

        bundle = extract(everything, args.password)
        if bundle is None:
            sys.exit("error: could not read the export back — is the password right?")

        cert, key = select(bundle, args.identity)
        if cert is None:
            sys.exit("error: no identity matching \"%s\" in %s" % (args.identity, args.keychain))
        if key is None:
            sys.exit("error: found the certificate but not its private key")

        cert_path = os.path.join(scratch, "cert.pem")
        key_path = os.path.join(scratch, "key.pem")
        open(cert_path, "w").write(cert + "\n")
        open(key_path, "w").write(key + "\n")

        # Repack with algorithms everything can read.
        packed = openssl("-export", "-in", cert_path, "-inkey", key_path,
                         "-out", args.out, "-passout", "pass:" + args.password,
                         "-keypbe", "AES-256-CBC", "-certpbe", "AES-256-CBC",
                         "-macalg", "sha256")
        if packed.returncode != 0:
            sys.exit("error: openssl could not build the .p12: %s" % packed.stderr.strip())

        os.chmod(args.out, 0o600)
        print(args.out)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()