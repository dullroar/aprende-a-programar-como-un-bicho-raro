# Blockers

## P0-002 (iteration 4)

The sandbox denied `tar -x` of the English archive into the repo (Bash don't-ask mode). Simple commands such as `git archive -o <scratch>` worked. No repo files changed apart from loop bookkeeping. To unblock: allow the extraction (or run it by hand: `git -C <clone> archive <sha> | tar -x --exclude=.gitignore`, merge English `.gitignore` entries into ours, add fetch-only `upstream` remote), then set P0-002 back to `todo`.

