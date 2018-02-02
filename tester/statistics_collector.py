import datetime
from io import StringIO
from string import Template

import pandas


class StatisticsCollector(object):
    def __init__(self, containers, debug=False):
        # should implements get_net_stats()
        self.containers = containers
        self.debug = debug

    def collect_stats(self, n, test_scenario_js=None, test_scenario_py=None):
        base_levels = []
        stats_list = []
        containers_count = len(self.containers)

        if test_scenario_py is not None and test_scenario_js is not None:
            raise Exception('TestScriptNotSingle')
        if test_scenario_py is None and test_scenario_js is None:
            raise Exception('TestScriptNotGiven')

        test_scenario = None
        is_python_script = False
        if test_scenario_js is not None:
            test_scenario = test_scenario_js
        if test_scenario_py is not None:
            test_scenario = test_scenario_py
            is_python_script = True

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
                    if not is_python_script:
                        # in test_scenario the results of prev steps can be used in placeholders like '$result0' -
                        # https://docs.python.org/3.1/library/string.html#template-strings
                        for j, test_command in enumerate(test_scenario):
                            test_command = Template(test_command).safe_substitute(template_dict)

                            res = c.run(command_js=test_command, debug=self.debug)
                            template_dict['result{num}'.format(num=j)] = res.strip('\'\"')

                            if self.debug:
                                print(
                                    "Container {}, iteration {}: {}".format(c.container.description,
                                                                            j, res))
                                print("------------------------------------------------------")
                    else:
                        #todo execute python scenario
                        pass

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
