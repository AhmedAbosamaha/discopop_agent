#!/usr/bin/env python3
"""Start a launcher script on the Mac so that it outlives the shell and the session that started it.

    python3 evaluation/agent/tools/detach.py LOG SCRIPT [ARGS...]

The script runs in a new session (no controlling terminal), its stdin from /dev/null and its stdout and stderr
appended to LOG; the process id is printed, so that `caffeinate -ims -w <pid>` can keep the Mac awake exactly as
long as the launcher runs. A launcher started this way waits for its server jobs and fetches their runs when they
end (the experiment record says which launcher started which runs).
"""
import os
import subprocess
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    log, cmd = sys.argv[1], sys.argv[2:]
    with open(log, "ab") as out, open(os.devnull, "rb") as nul:
        p = subprocess.Popen(cmd, stdin=nul, stdout=out, stderr=subprocess.STDOUT, start_new_session=True,
                             close_fds=True)
    print(p.pid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
