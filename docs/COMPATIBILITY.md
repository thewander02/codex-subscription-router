# Compatibility

The patcher is intentionally tied to known ChatGPT desktop bundle structures.
It verifies every modified renderer, main-process, and native binary anchor and
stops instead of applying a partial patch.

## Release 0.1.0

| Component | Tested value |
| --- | --- |
| Official ChatGPT version | `26.803.61601` |
| Official bundle build | `6396` |
| `app.asar` SHA-256 | `d5a44ed9e2f1db5f81dbbe85408aed256f3203c5b16f00817bb9d7cd941343cf` |
| Architecture | Apple silicon (`arm64`) |

A different official version may work when all anchors remain identical, but
it is unverified. The patcher rejects a version, build, or ASAR hash mismatch by
default; `--allow-untested-source` is an explicit diagnostic override. Never
weaken an anchor-count or binary-constant check merely to make a new build
complete. Review the upstream change and update the patch deliberately.

## Fork: build 8109

| Component | Tested value |
| --- | --- |
| Official ChatGPT version | `26.901.51231` |
| Official bundle build | `8109` |
| `app.asar` SHA-256 | `64fc2f27d2dddfa968acfacbe5e4e0328071bdc406351ff4a7d18f0b4692c83d` |
| Official ASAR header SHA-256 | `e2ab6e5985856e148ff78e79658e1241e9ab258d82453d201326bdd2e6779717` |
| Architecture | Apple silicon (`arm64`) |

The renderer port is isolated in `scripts/renderer_8109.py`. Profile/usage UI
now lives in `app-primary`, while queries and RPC dispatch remain in
`app-initial`. The ASAR contains 16 CUA identifier references; the separate
native CUA package retains 49 references and the same checked team constants.
The bootstrap's updater initialization moved inside its startup try block.
Both normal and startup-failure updater calls are disabled in the copy.

ASAR integrity uses the SHA-256 of `getRawHeader().headerString`, as the official
build does. The whole archive hash above remains the source compatibility gate.
Apple Development signing teams are resolved from a signed disposable probe,
not guessed from the certificate display name. Vendor push entitlements are
removed along with other team-scoped grants.

Run `python3 scripts/check_source_8109.py /path/to/extracted-asar` to exercise
all desktop/renderer anchors and syntax checks on disposable copies. This does
not distribute or modify the source app.
