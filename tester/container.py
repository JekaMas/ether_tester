import time
import random
import string
from .script import Script


class Container(object):
    def __init__(self, docker_command, container_command, description=None, init_time=1):
        self.name = Container.get_random_name(6)
        self.docker_command = docker_command
        self.container_command = container_command
        self.command = '{docker_command} --name={container_name} {container_command}'. \
            format(docker_command=self.docker_command, container_name=self.name,
                   container_command=self.container_command)

        self.description = description
        self.p = None
        self.last_output = ""
        self.init_time = init_time

    def start(self):
        print(self.command)

        out, self.p = Script.sh(self.command, wait=False)
        time.sleep(self.init_time)
        self.print_output()

    def get_output(self):
        out = []
        while True:
            inchar = self.p.stdout.readline()
            if inchar:  # neither empty string nor None
                line = str(inchar).strip()
                if line == ">":
                    # strip the greetings
                    continue

                out.append(line)
            else:
                break

        self.last_output = "\n".join(out)
        return self.last_output.strip()

    def print_output(self):
        if not self.last_output:
            self.get_output()

        out = self.last_output
        self.last_output = ""
        print(out, end='')  # or end=None to flush immediately

    def run(self, command, debug=False):
        self.p.stdin.write(command + "\n")
        time.sleep(1)

        if debug:
            print("RUN", self.description, command + "\n")

        return self.get_output()

    @staticmethod
    def get_random_name(n):
        return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(n))
