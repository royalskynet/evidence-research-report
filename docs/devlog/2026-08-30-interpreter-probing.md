# Dev Log — Probe the interpreter, don't trust `PATH`

**Date**: 2026-08-30
**Scope**: `claude/evidence-research-report/scripts/`, `references/retrieval-resilience.md`

## Problem

The fetch-resilience chain's last tier renders pages locally, and `scripts/setup_render.sh` provisions it. When `uv` is available the script builds an isolated venv, which is fine. When `uv` is absent it falls back to line 21:

```sh
VENV_PY="$(command -v python3)"
```

and then installs into that interpreter's user site-packages. That fallback assumes the first `python3` on `PATH` is a working interpreter. On a machine where that assumption did not hold, the failure was remarkably hard to read.

The visible error, from an unrelated tool on the same machine, was:

```
ModuleNotFoundError: No module named 'yaml'
```

The obvious response — install the package — does not work, and cannot. The interpreter in question was a Homebrew build whose `pyexpat` extension fails to load:

```
ImportError: dlopen(.../pyexpat.cpython-3xx-darwin.so): Symbol not found:
  _XML_SetAllocTrackerActivationThreshold
  Referenced from: .../pyexpat.cpython-3xx-darwin.so
  Expected in: /usr/lib/libexpat.1.dylib
```

The extension was built against a newer `libexpat` than the one it resolves against at runtime. That breaks `import xml`, which breaks `xmlrpc.client`, which breaks `pip` itself. So the interpreter cannot install the package whose absence it is reporting. The error message names a missing module; the actual fault is a dynamic-linking mismatch two layers down, and every message along that path points away from the cause.

## Why the environment repairs are a gamble

Three repairs suggest themselves, and none is clearly correct:

- **Reinstall the Python formula.** If the reinstall pulls the same prebuilt bottle, it reinstalls the same bytes and the same mismatch.
- **Reinstall or relink the expat library.** On the affected machine expat was not a separate keg at all — the extension links against the OS-provided library by design, so there is nothing to relink.
- **Upgrade to a newer Python formula.** This is the only one with a real chance, but it is a bet: it helps only if the newer bottle happens to have been built against a library the machine actually has, which is not something you can determine without trying it. It also rebuilds every dependent venv, so the blast radius extends to unrelated tools. Two different Python versions on the machine shared the same bottle lineage and were both affected, so "upgrade one and see" does not even isolate the variable cleanly.

The working explanation is an OS-version skew — the bottle was built expecting a newer system `libexpat` than the OS ships. That explanation is consistent with everything observed, but it is inference from symptoms rather than something verified against build metadata, and the decision below deliberately does not depend on it being right.

## Approach: capability probing

Rather than repair the environment, select an interpreter that demonstrably works:

```sh
if ! python3 -c 'import yaml' >/dev/null 2>&1; then
  for candidate in /usr/bin/python3 /usr/local/bin/python3; do
    if [ -x "$candidate" ] && "$candidate" -c 'import yaml' >/dev/null 2>&1; then
      # prepend a shim directory containing a python3 symlink to this candidate
      break
    fi
  done
fi
```

Three properties make this the right shape:

- **It tests the capability, not the identity.** Version numbers, install paths, and formula names are all proxies for "can this interpreter do the thing I need." Probing asks the question directly, so it stays correct under environment changes nobody told us about.
- **It is self-disabling.** Once the default interpreter works, the guard's condition is false and the fallback never engages. There is no cleanup step to remember and no stale pin to rot.
- **It does not require understanding the root cause.** The diagnosis above may be wrong in its details; the probe is correct either way.

The alternative — hardcoding an absolute path to a known-good interpreter — was rejected because it inverts the failure mode. It works today and silently becomes the *cause* of a failure later, on a machine where that path is missing or is itself broken.

## What this suggests for this repo

`setup_render.sh`'s no-`uv` fallback is the place this bites. It picks an interpreter by position on `PATH` and then mutates it by installing packages into it, which is both the least reliable selection strategy and the most invasive use of the result. Worth considering:

- probe the chosen interpreter before installing into it, and fall through to another candidate rather than failing partway through provisioning
- prefer the `uv`-managed venv path more strongly, since an isolated venv sidesteps the entire class of problem — the affected machine's venv-based tooling was completely unaffected while its `PATH`-based tooling was not
- when a script depends on an interpreter having a capability, say so in a probe rather than in a comment

More generally: a dependency error that names a missing package is not always about a missing package. When installing the package fails in a way that implicates the installer itself, the interpreter is the suspect, not the package index.
