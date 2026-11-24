#!/usr/bin/env bash
# Run the fast check of the edition.
#
# Run me when: I changed a file and want the fast check of the edition.
#
# It runs "python3 -I tools/verify.py --fast" and passes all arguments on.
# Exit code 0 means pass.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -I tools/verify.py --fast "$@"
