import datetime
from io import StringIO
from string import Template

import pandas


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
                    for j, test_command in enumerate(test_scenario):
                        test_command = Template(test_command).safe_substitute(template_dict)

                        res = self.containers[i].run(test_command, debug=self.debug)
                        template_dict['result{num}'.format(num=j)] = res.strip('\'\"')

                        if self.debug:
                            print(
                                "Container {}, iteration {}: {}".format(self.containers[i].container.description,
                                                                        j, res))

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
