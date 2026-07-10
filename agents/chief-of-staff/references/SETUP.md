# Chief-of-Staff Home Setup

Your home directory is **not yet tracked in a git repository**. Until it is,
your workflows and operating state live only on this machine and cannot follow
you to another. Do this before other work unless the user tells you to defer.

Home directory (local path to preserve): `{{HOME}}`

## Goal

The home directory becomes a symlink into a cloned git repo, mirroring the
local path inside the repo:

    {{HOME}}  ->  <clone>/.agents/homes/chief-of-staff

## Steps

1. **Identify the tracking repo.** This is the user-facing tracking repository
   the chief of staff shares with the user — the same repo that holds
   `projects/`, `decisions/`, and the daily report. If one already exists, use
   it. If not, ask the user whether to create it, then `gh repo create`
   (private by default).

2. **Clone it** somewhere outside the home dir, e.g. `~/src/<repo>`.

3. **Move existing home contents into the repo, mirroring the path:**

       mkdir -p <clone>/.agents/homes/chief-of-staff
       # Copy everything real from {{HOME}} (workflows/, references you
       # authored, etc.) into that directory. Do NOT copy transient logs.

4. **Ignore machine-local noise** — add `<clone>/.agents/homes/chief-of-staff/.gitignore`
   (adjust to what actually exists):

       state/*.log
       state/*.launchd.*.log

5. **Replace the home directory with a symlink** (only after contents are
   safely copied):

       rm -rf {{HOME}}
       ln -s <clone>/.agents/homes/chief-of-staff {{HOME}}

6. **Commit and push.**

7. **Re-run `scripts/session_start.py`** to confirm you now get the session
   brief instead of this guide.

## Notes

- Preserve, don't discard: migrate every real workflow and reference you have.
- The symlink is the *only* signal that setup is complete; nothing else marks it.
- After this, workflows you capture live in the repo automatically and are
  shared across machines.
