# Build 8109 validation

Validated locally on an Apple silicon Mac against ChatGPT 26.901.51231 (8109).
This is a compatibility fork, not a claim of an upstream release certification.

## Fixes

- Fresh installs work with macOS `/bin/bash` 3.2 under `set -u`.
- Existing installs retain `--force`, recoverable backups, and external state.
- The installer clones this fork into its own source directory.
- Version-specific renderer anchors cover the split primary/initial bundles,
  account menu, direct plugin RPCs, reset hooks, profile selector, and task owner.
- Signing resolves the real TeamIdentifier, removes vendor push entitlements,
  and records the correct ASAR header integrity hash.
- The copied app's normal and failure-path updater calls are disabled.

## Verified

- Go tests and vet, JavaScript syntax, Python regressions, shell syntax, and
  source-only release metadata checks pass.
- Source compatibility and every changed renderer/desktop anchor pass against
  a disposable extraction, including syntax checks on patched bundles.
- A team-signed app launches and the local router recognizes the existing
  Primary subscription. The official source ASAR hash is unchanged.
- The account menu loads live quota, a masked email, plan, and Add another
  subscription. The native usage/reset sheet opens without spending a reset.
- Profile and Plugins settings open with subscription selectors.
- A real new chat returned `ROUTER_OK`, and its follow-up returned
  `ROUTER_FOLLOWUP_OK`; task ownership displays Primary.

## Manual checks and limitations

- A second subscription must be signed in by the account holder before real
  cross-account routing, failover, and secondary OAuth can be smoke-tested.
  Their backend routing and scoping unit tests pass.
- No reset credits were consumed and no reset purchase was attempted.
- macOS privacy consent for the independent app/helper remains user-controlled.
  Signature validation does not by itself verify Appshots or Computer Use.
- The copy has no OpenAI push-notification entitlement; vendor push delivery is
  unavailable. Local runtime capabilities are preserved.
- Profile editing targets Primary. Select Primary before editing; combined and
  secondary profile views are for reading statistics.
- Existing app/helper backups and router account state are retained.
