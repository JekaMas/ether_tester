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

        if test_scenario is None:
            raise Exception('TestScriptNotGiven')

        for c in self.containers:
            base_level_str = StringIO(c.get_net_stats())
            base_level = pandas.read_csv(base_level_str, sep="\t")
            base_levels.append(base_level)

            stats = pandas.DataFrame(columns=base_level.columns.values.tolist())
            stats_list.append(stats)

        start_time = datetime.datetime.now()
        delta = 0

        template_dict_array = [{'result{}'.format(t): '' for t in range(len(test_scenario))} for c in self.containers]

        run = 1
        while delta < n:
            # todo: run in parallel
            print("\nRun #{}------------------------------------------------".format(run))
            for i, c in enumerate(self.containers):
                template_dict = template_dict_array[i]
                if test_scenario is not None:
                    for j, test_command in enumerate(test_scenario):
                        res = c.run(command=test_command, state_dict=template_dict, debug=self.debug)
                        template_dict['result{num}'.format(num=j)] = res

                        if self.debug:
                            print(
                                "Container {}, iteration {}: {}".format(c.container.description,
                                                                        j, res))
                            print("------------------------------------------------------")

                data = c.get_net_stats()

                new_level = StringIO(data)
                df = pandas.read_csv(new_level, sep="\t")
                df = df.subtract(base_levels[i])

                stats_list[i] = stats_list[i].append(df)

            current_time = datetime.datetime.now()
            delta = int((current_time - start_time).total_seconds())
            run = run + 1

        for i in range(0, containers_count):
            stats_list[i] = stats_list[i].astype(int)

        return stats_list
