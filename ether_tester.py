import subprocess
import pandas
from io import StringIO
import time
import random
import string
import os
import fcntl
import datetime
import yaml
import threading
from string import Template


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


class AtomicCounter:
    def __init__(self, initial=0):
        """Initialize a new atomic counter to given initial value (default 0)."""
        self.value = initial
        self._lock = threading.Lock()

    def increment(self, num=1):
        """Atomically increment the counter by num (default 1) and return the
        new value.
        """
        with self._lock:
            self.value += num
            return self.value


class Geth(Container):
    port = AtomicCounter()
    json_rpc_port = AtomicCounter()

    port_default = 30303
    json_rpc_port_default = 8545
    ropsten_defaults = "--testnet --syncmode \"fast\" --bootnodes \"enode://7ab298cedc4185a894d21d8a4615262ec6bdce66c9b6783878258e0d5b31013d30c9038932432f70e5b2b6a5cd323bf820554fcb22fbc7b45367889522e9c449@51.15.63.93:30303,enode://f59e8701f18c79c5cbc7618dc7bb928d44dc2f5405c7d693dad97da2d8585975942ec6fd36d3fe608bfdc7270a34a4dd00f38cfe96b2baa24f7cd0ac28d382a1@51.15.79.88:30303,enode://e2a3587b7b41acfc49eddea9229281905d252efba0baf565cf6276df17faf04801b7879eead757da8b5be13b05f25e775ab6d857ff264bc53a89c027a657dd10@51.15.45.114:30303,enode://fe991752c4ceab8b90608fbf16d89a5f7d6d1825647d4981569ebcece1b243b2000420a5db721e214231c7a6da3543fa821185c706cbd9b9be651494ec97f56a@51.15.67.119:30303,enode://482484b9198530ee2e00db89791823244ca41dcd372242e2e1297dd06f6d8dd357603960c5ad9cc8dc15fcdf0e4edd06b7ad7db590e67a0b54f798c26581ebd7@51.15.75.138:30303,enode://9e99e183b5c71d51deb16e6b42ac9c26c75cfc95fff9dfae828b871b348354cbecf196dff4dd43567b26c8241b2b979cb4ea9f8dae2d9aacf86649dafe19a39a@51.15.79.176:30303,enode://12d52c3796700fb5acff2c7d96df7bbb6d7109b67f3442ee3d99ac1c197016cddb4c3568bbeba05d39145c59c990cd64f76bc9b00d4b13f10095c49507dd4cf9@51.15.63.110:30303,enode://0f7c65277f916ff4379fe520b875082a56e587eb3ce1c1567d9ff94206bdb05ba167c52272f20f634cd1ebdec5d9dfeb393018bfde1595d8e64a717c8b46692f@51.15.54.150:30303,enode://e006f0b2dc98e757468b67173295519e9b6d5ff4842772acb18fd055c620727ab23766c95b8ee1008dea9e8ef61e83b1515ddb3fb56dbfb9dbf1f463552a7c9f@212.47.237.127:30303,enode://d40871fc3e11b2649700978e06acd68a24af54e603d4333faecb70926ca7df93baa0b7bf4e927fcad9a7c1c07f9b325b22f6d1730e728314d0e4e6523e5cebc2@51.15.132.235:30303,enode://ea37c9724762be7f668e15d3dc955562529ab4f01bd7951f0b3c1960b75ecba45e8c3bb3c8ebe6a7504d9a40dd99a562b13629cc8e5e12153451765f9a12a61d@163.172.189.205:30303,enode://88c2b24429a6f7683fbfd06874ae3f1e7c8b4a5ffb846e77c705ba02e2543789d66fc032b6606a8d8888eb6239a2abe5897ce83f78dcdcfcb027d6ea69aa6fe9@163.172.157.61:30303,enode://ce6854c2c77a8800fcc12600206c344b8053bb90ee3ba280e6c4f18f3141cdc5ee80bcc3bdb24cbc0e96dffd4b38d7b57546ed528c00af6cd604ab65c4d528f6@163.172.153.124:30303,enode://00ae60771d9815daba35766d463a82a7b360b3a80e35ab2e0daa25bdc6ca6213ff4c8348025e7e1a908a8f58411a364fe02a0fb3c2aa32008304f063d8aaf1a2@163.172.132.85:30303,enode://86ebc843aa51669e08e27400e435f957918e39dc540b021a2f3291ab776c88bbda3d97631639219b6e77e375ab7944222c47713bdeb3251b25779ce743a39d70@212.47.254.155:30303,enode://a1ef9ba5550d5fac27f7cbd4e8d20a643ad75596f307c91cd6e7f85b548b8a6bf215cca436d6ee436d6135f9fe51398f8dd4c0bd6c6a0c332ccb41880f33ec12@51.15.218.125:30303\" --cache=256"

    is_wait_sync = False
    is_synced = False

    def __init__(self, eth_value, container_command=None, version='latest', description=None, init_time=1,
                 is_wait_sync=False):
        port = Geth.port_default + Geth.port.increment()
        json_rpc_port = Geth.json_rpc_port_default + Geth.json_rpc_port.increment()

        docker_command = 'docker run -i --rm -p {json_rpc_port}:8545 -p {port}:30303 ' \
                         '-v {eth_value}:/root/.ethereum'.format(
            json_rpc_port=json_rpc_port, port=port, eth_value=eth_value)

        if container_command is None:
            container_command = Geth.ropsten_defaults

        container_command = "ethereum/client-go:{version} {container_command}".format(version=version,
                                                                                      container_command=container_command)
        container_command += " --rpc --rpcaddr \"0.0.0.0\" --verbosity 2 console"

        self.docker_command = docker_command
        self.container_command = container_command
        self.description = description
        self.init_time = init_time
        self.is_wait_sync = is_wait_sync

        super().__init__(self.docker_command, self.container_command, self.description, self.init_time)

    def start(self):
        super().start()
        if self.is_wait_sync and not self.is_synced:
            self.wait_sync()

    def run(self, command, debug=False, queue=None, force_skip_sync=False):
        if not force_skip_sync and self.is_wait_sync and not self.is_synced:
            self.wait_sync()

        result = super().run(command, debug)

        if queue is not None:
            queue.put(result)

        return result

    def wait_sync(self):
        print("waiting for sync", self.description)

        diff = 0
        previous_diff = 0

        tries = 0
        max_tries = 10
        while True:
            time.sleep(60)
            result_json = self.run("eth.syncing", force_skip_sync=True).strip()
            if result_json == "false":
                break

            try:
                result = yaml.load(result_json)
            except Exception as e:
                err = str(e)
                print('Loading json error={error}\njson=\"{json}\"\nlength={length}'.format(error=err,
                                                                                            json=result_json,
                                                                                            length=len(result_json)))
                raise

            current_block = int(result.get('currentBlock'))
            highest_block = int(result.get("highestBlock"))

            if highest_block > 0 and current_block >= highest_block:
                break

            print('{name} is still syncing. {current_block} out of {highest_block}'.format(name=self.description,
                                                                                           current_block=current_block,
                                                                                           highest_block=highest_block),
                  sep=None)

            diff = highest_block - current_block

            if previous_diff != 0 and diff == previous_diff:
                tries += 1
                if tries == max_tries:
                    raise BaseException("Cant sync after {tries} tries".format(tries=tries))

            previous_diff = diff

        print('{name} syncing done'.format(name=self.description), sep=None)
        self.is_synced = True


# todo: implement
class Status(Geth):
    pass


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


class Cluster(object):
    def __init__(self, containers, is_wait_sync=None, debug=False):
        self.is_wait_sync = is_wait_sync
        self.containers = containers
        self.container_managers = []
        self.is_started = False
        self.debug = debug
        self.stats = []

        for c in containers:
            if is_wait_sync is not None:
                c.wait_sync = is_wait_sync
            self.container_managers.append(ContainerManager(container=c))

        self.stats_collector = StatisticsCollector(self.container_managers, debug=self.debug)

    def start(self):
        if self.is_started:
            return

        threads = []
        for c in self.containers:
            t = threading.Thread(target=c.start)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.is_started = True

        return self

    def collect_stats(self, n, test_scenario=None):
        if not self.is_started:
            return None

        self.stats = self.stats_collector.collect_stats(n, test_scenario)

        return self.stats

    def print_stats(self):
        if len(self.stats) == 0:
            return

        print("Statistics:")
        for i, c in enumerate(self.containers):
            print(c.description)
            if len(self.stats[i]) == 0:
                print('Zero traffic on {num} container\n'.format(num=i))
                continue
            print("Stats (bytes/s):\n{}".format(self.stats[i].describe(include='all').astype(int)))
            print("\nTraffic sum(bytes):\n{}".format(self.stats[i].sum(axis=0)))
            print()

        # search for bias
        bias_sum = []
        bias_num = 0
        for i, c in enumerate(self.containers):
            if len(self.stats[i]) != 0:
                bias_sum = self.stats[0].sum(axis=0)
                bias_num = i
                break

        for i, c in enumerate(self.containers):
            if i == bias_num:
                print("Network difference wrt {num} container:".format(num=bias_num))
                continue
            if len(self.stats[i]) == 0:
                continue

            print("\nTraffic sum(bytes) - '{}':\n{}".format(c.description,
                                                            (self.stats[i].sum(axis=0) - bias_sum) / bias_sum * 100))


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


class StatisticsCollector(object):
    def __init__(self, containers, debug=False):
        # should implements get_net_stats()
        self.containers = containers
        self.debug = debug

    def collect_stats(self, n, test_scenario=None):
        base_levels = []
        stats_list = []
        containers_count = len(self.containers)

        for i in range(0, containers_count):
            base_level_str = StringIO(self.containers[i].get_net_stats())
            base_level = pandas.read_csv(base_level_str, sep="\t")
            base_levels.append(base_level)

            stats = pandas.DataFrame(columns=base_level.columns.values.tolist())
            stats_list.append(stats)

        start_time = datetime.datetime.now()
        delta = 0

        template_dict = dict()
        if test_scenario is not None:
            for i in range(0, len(test_scenario)):
                template_dict['result{num}'.format(num=i)] = ''

        while delta < n:
            # todo: run in parallel
            for i in range(0, containers_count):
                if test_scenario is not None:
                    # in test_scenario the results of prev steps can be used in placeholders like '$result0' -
                    # https://docs.python.org/3.1/library/string.html#template-strings
                    for i, test_command in enumerate(test_scenario):
                        test_command = Template(test_command).safe_substitute(template_dict)
                        print("Template", template_dict, test_command)

                        res = self.containers[i].run(test_command, debug=self.debug)
                        template_dict['result{num}'.format(num=i)] = res.strip('\'\"')

                        if self.debug:
                            print(
                                "Container {}, iteration {}: {}".format(self.containers[i].container.description,
                                                                        i, res))

                data = self.containers[i].get_net_stats()

                new_level = StringIO(data)
                df = pandas.read_csv(new_level, sep="\t")
                df = df.subtract(base_levels[i])

                stats_list[i] = stats_list[i].append(df)

            current_time = datetime.datetime.now()
            delta = int((current_time - start_time).total_seconds())

        for i in range(0, containers_count):
            stats_list[i] = stats_list[i].astype(int)

        return stats_list


cluster = Cluster(
    [
        Geth(
            eth_value="~/.ethereum/docker",
            description="Geth with Whisper service",
            init_time=20),
        Geth(
            eth_value="~/.ethereum/docker2",
            description="Geth without Whisper service",
            init_time=20)
    ],
    is_wait_sync=True, debug=False).start()

# stats_list = stats.collect_stats(60)
cluster.collect_stats(60, ['personal.newAccount(\"passphrase\")', 'miner.setEtherbase(\"$result0\")'])
cluster.print_stats()

# todo test latest vs v1.7.3

# todo test geth vs status - double scenario needed

# examples
'''
use already running container:
geth_docker_name1 = "ethereum1"
geth1 = ContainerManager(name=geth_docker_name1)


start new container:
g1 = Geth(
    eth_value="~/.ethereum/docker",
    description="Geth with Whisper service",
    init_time=20)

geth1 = ContainerManager(name="geth_with_whisper", container=g1)

run single command:
g1.run("eth.syncing", debug=True)

Use test scenario:
empty
stats_list = stats.collect_stats(60)

simple
stats_list = stats.collect_stats(60, ['personal.newAccount(\"passphrase\")'])


with template (https://docs.python.org/3.1/library/string.html#template-strings)
stats_list = stats.collect_stats(60, ['personal.newAccount(\"passphrase\")', 'miner.setEtherbase($result0)'])
'''
