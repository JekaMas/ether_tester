import threading

from .container_manager import ContainerManager
from .statistics_collector import StatisticsCollector


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

    def stop(self):
        if not self.is_started:
            return

        threads = []
        for c in self.containers:
            t = threading.Thread(target=c.stop)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.is_started = False

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
