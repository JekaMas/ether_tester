from tester.cluster import Cluster
from tester.geth import Geth

class UseCase:
    @staticmethod
    def run():
        cluster = Cluster(
            [
                Geth(
                    shh=True,
                    eth_host_volume_path="~/.ethereum/docker",
                    description="Geth with Whisper service",
                    init_time=20),
                Geth(
                    eth_host_volume_path="~/.ethereum/docker2",
                    description="Geth without Whisper service",
                    init_time=20)
            ],
            is_wait_sync=True, debug=False).start()

        # idle case
        # stats_list = stats.collect_stats(60)

        # create account case
        cluster.collect_stats(60, ['personal.newAccount(\"passphrase\")', 'miner.setEtherbase(\"$result0\")'])

        cluster.print_stats()

        cluster.stop()
