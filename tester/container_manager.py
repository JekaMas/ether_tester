from .script import Script


class ContainerManager(object):
    def __init__(self, name=None, container=None):
        self.container = container
        self.id = None
        self.pid = None

        self.name = name
        if self.container is not None:
            self.name = self.container.name

    def get_id(self):
        if self.id is not None:
            return self.id

        docker_name_id_all = 'docker ps --format "{{.ID}} {{.Names}}"'
        docker_name_id = 'grep {container_name}'.format(container_name=self.name)
        docker_id = 'awk \'{print $1}\''

        self.id = Script.pipe([docker_name_id_all, docker_name_id, docker_id])

        return self.id

    def get_pid(self):
        if self.pid is not None:
            return self.pid

        self.pid, p = Script.sh('docker inspect -f \'{{{{ .State.Pid }}}}\' {container_id}'.
                                format(container_id=self.get_id()))

        return self.pid

    def get_net_stats(self):
        pid_net_stats = 'cat /proc/{container_pid}/net/dev'.format(container_pid=self.get_pid())
        get_eth0 = 'grep eth0'
        format_stats = 'awk \'{{sum = $2+$10;rec=$2;tra=$10}} END ' \
                       '{{print \"Receive\\tTransmit\\tTotal\\n\" rec \"\\t\" tra \"\\t\" sum}}\''

        return Script.pipe([pid_net_stats, get_eth0, format_stats])

    def get_command(self, command):
        def fn():
            return self.container.run(command)

        return fn

    def send_command(self, command):
        p_stdin = 'cat /proc/{container_pid}/fd/0'.format(container_pid=self.get_pid())
        sent_stdin = 'echo "{command}" > {stdin}'.format(command=command, stdin=p_stdin)

        Script.sh(sent_stdin)

    def run(self, command, debug=False):
        return self.container.run(command, debug)
