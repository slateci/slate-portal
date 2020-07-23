from portal import app, csrf
import sys
import subprocess
import os
import signal

@app.route('/webhooks/github', methods=['GET', 'POST'])
@csrf.exempt
def webhooks():
    """Endpoint that acepts post requests from Github Webhooks"""

    cmd = """
    git pull origin master
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate()
    print("Return code: {}".format(p.returncode))
    print("Error message: {}".format(err))

    parent_pid = os.getppid()
    print("Parent PID: {}".format(parent_pid))
    os.kill(parent_pid, signal.SIGHUP)

    return out