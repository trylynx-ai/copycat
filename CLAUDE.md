# CLAUDE.md

This file provides guidance to AI coding agents when working with code in this repository.

## What this is

A Splunk add-on that generates fake logs/events so the Lynx AI Agent for Splunk can be tested against realistic data types and parsing scenarios. Published on Splunkbase as app 8540.

Everything shipped to Splunk lives under `copycat/` - that directory *is* the app and is what gets packaged. Files at the repo root (`pyproject.toml`, `README.md`, `.github/`) are development scaffolding and are not part of the final package.

## Commands

```bash
# Run the generator (uv is recommended; plain python3 works too)
uv run copycat/bin/copycat.py app --count 5
uv run copycat/bin/copycat.py api -n 10 --start 2026-01-01T00:00:00 --end 2026-01-31T23:59:59

# Package the app the same way CI does, for local AppInspect or manual install
mkdir -p build && cp -a copycat build/copycat && tar -czvf build/copycat.tgz -C build copycat && rm -rf build/copycat
```

There is no test suite, linter, or formatter configured. Verify changes by running the generator and eyeballing output against the `props.conf` regexes.

## Architecture

The whole app is four moving parts that must stay in sync per log type:

1. **`copycat/bin/copycat.py`** - stdlib-only generator. One `generate_<type>_logs(timestamp)` function per type, all registered in the `log_generators` dict, which is also the source of truth for argparse's `choices`. Each function returns a single line beginning with the timestamp. `main()` prints one event per line to stdout; with `--start`/`--end` it produces sorted random timestamps in that range (backfill), otherwise `datetime.now()`.
2. **`copycat/default/inputs.conf`** - one `[script://./bin/copycat.py <type>]` stanza per type, `interval = 10`, `python.version = python3.9`, routing to `index = copycat_<type>` / `sourcetype = copycat:<type>`.
3. **`copycat/default/indexes.conf`** - a `copycat_<type>` index per type.
4. **`copycat/default/props.conf`** - per-sourcetype `TIME_FORMAT = %Y-%m-%d %T.%f` plus an `EXTRACT-copycat_<type>_fields` regex with named capture groups matching the event format produced by the generator.

Adding a log type means touching all four. Changing an event's *format* means updating the matching `EXTRACT-` regex in `props.conf` (and `TIME_FORMAT` if the timestamp changes) - the regexes are tightly coupled to the exact f-string in the generator.

Keep `sourcetype` names stable (`copycat:<type>`); they are the contract with anyone querying the data. Changes to `indexes.conf` require a Splunk restart.

## Constraints

- **Python 3.9, standard library only.** 3.9 is what Splunk ships; `pyproject.toml` pins `==3.9.*` and `dependencies = []`. Do not add dependencies or use post-3.9 syntax.
- **Scripted-input hygiene:** non-interactive, fast, events to stdout only, no stderr noise.
- **`default/` is shipped defaults; `local/` is for site overrides** and should not be committed unless explicitly requested. Inputs are intentionally `disabled = false` in `default/` here even though real deployments would toggle them in `local/`.
- Keep changes lean - minimal comments and abstractions, sane and supportable `.conf` defaults. Assume the reader is a Splunk admin / PS engineer.
- No secrets, tokens, or environment-specific paths in the app.

## Release flow

Bump `version` in **both** `pyproject.toml` and `copycat/default/app.conf` (`[id]`, `[launcher]`) - they are expected to match. On push to `main`, `.github/workflows/add_tag.yml` reads the version from `pyproject.toml` and creates a `v<version>` tag if it doesn't exist; that tag triggers `appinspect.yml`, which packages `copycat/` into a tarball, runs Splunk AppInspect, and uploads the artifact. AppInspect also runs on every PR to `main`, so `.conf` changes should be AppInspect-clean.
