import os
import signal
import subprocess
import sys

from portal import app, csrf


@app.route("/webhooks/github", methods=["GET", "POST"])
@csrf.exempt
def webhooks():
    """Endpoint that acepts post requests from Github Webhooks"""

    cmd = """
    git pull origin master
    """
    p = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    out, err = p.communicate()
    app.logger.debug("Return code: {}".format(p.returncode))
    app.logger.error("Error message: {}".format(err))

    parent_pid = os.getppid()
    app.logger.debug("Parent PID: {}".format(parent_pid))
    os.kill(parent_pid, signal.SIGHUP)

    return out
