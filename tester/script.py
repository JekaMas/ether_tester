import fcntl
import os
import subprocess


class Script(object):
    @staticmethod
    def set_non_blocking(fd):
        """
        Set the file description of the given file descriptor to non-blocking.
        """
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    @staticmethod
    def sh(command, wait=True, stdin=None, stdout=None, debug=False):
        if debug:
            print(command)

        if stdout is None:
            stdout = subprocess.PIPE

        if stdin is None:
            stdin = subprocess.PIPE

        p = None
        try:
            p = subprocess.Popen(command, universal_newlines=True, shell=True, stdin=stdin, stdout=stdout, bufsize=1)
            Script.set_non_blocking(p.stdout)
        except Exception as e:
            err = str(e)
            print(err)
            if p is not None:
                p.kill()
            return

        if wait:
            out, err = p.communicate()

            if p.returncode != 0:
                print("got an error %d %s. output %s" % (p.returncode, err, out))
                exit(1)
                return

            return out.strip(), p

        return "", p

    @staticmethod
    def pipe(commands):
        cmd = ""
        if not isinstance(commands, list):
            cmd = commands
        elif len(commands) == 1:
            cmd = commands[0]
        else:
            cmd = " | ".join(commands)

        out, p = Script.sh(cmd)
        return out
