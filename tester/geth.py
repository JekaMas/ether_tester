from .container import Container
from .counter import AtomicCounter
import time
import yaml


class Geth(Container):
    port = AtomicCounter()
    json_rpc_port = AtomicCounter()

    port_default = 30303
    json_rpc_port_default = 8545
    ropsten_defaults = "--testnet --syncmode \"fast\" --cache=256"
    ropsten_bootnodes = [
        "enode://7ab298cedc4185a894d21d8a4615262ec6bdce66c9b6783878258e0d5b31013d30c9038932432f70e5b2b6a5cd323bf820554fcb22fbc7b45367889522e9c449@51.15.63.93:30303",
        "enode://f59e8701f18c79c5cbc7618dc7bb928d44dc2f5405c7d693dad97da2d8585975942ec6fd36d3fe608bfdc7270a34a4dd00f38cfe96b2baa24f7cd0ac28d382a1@51.15.79.88:30303",
        "enode://e2a3587b7b41acfc49eddea9229281905d252efba0baf565cf6276df17faf04801b7879eead757da8b5be13b05f25e775ab6d857ff264bc53a89c027a657dd10@51.15.45.114:30303",
        "enode://fe991752c4ceab8b90608fbf16d89a5f7d6d1825647d4981569ebcece1b243b2000420a5db721e214231c7a6da3543fa821185c706cbd9b9be651494ec97f56a@51.15.67.119:30303",
        "enode://482484b9198530ee2e00db89791823244ca41dcd372242e2e1297dd06f6d8dd357603960c5ad9cc8dc15fcdf0e4edd06b7ad7db590e67a0b54f798c26581ebd7@51.15.75.138:30303",
        "enode://9e99e183b5c71d51deb16e6b42ac9c26c75cfc95fff9dfae828b871b348354cbecf196dff4dd43567b26c8241b2b979cb4ea9f8dae2d9aacf86649dafe19a39a@51.15.79.176:30303",
        "enode://12d52c3796700fb5acff2c7d96df7bbb6d7109b67f3442ee3d99ac1c197016cddb4c3568bbeba05d39145c59c990cd64f76bc9b00d4b13f10095c49507dd4cf9@51.15.63.110:30303",
        "enode://0f7c65277f916ff4379fe520b875082a56e587eb3ce1c1567d9ff94206bdb05ba167c52272f20f634cd1ebdec5d9dfeb393018bfde1595d8e64a717c8b46692f@51.15.54.150:30303",
        "enode://e006f0b2dc98e757468b67173295519e9b6d5ff4842772acb18fd055c620727ab23766c95b8ee1008dea9e8ef61e83b1515ddb3fb56dbfb9dbf1f463552a7c9f@212.47.237.127:30303",
        "enode://d40871fc3e11b2649700978e06acd68a24af54e603d4333faecb70926ca7df93baa0b7bf4e927fcad9a7c1c07f9b325b22f6d1730e728314d0e4e6523e5cebc2@51.15.132.235:30303",
        "enode://ea37c9724762be7f668e15d3dc955562529ab4f01bd7951f0b3c1960b75ecba45e8c3bb3c8ebe6a7504d9a40dd99a562b13629cc8e5e12153451765f9a12a61d@163.172.189.205:30303",
        "enode://88c2b24429a6f7683fbfd06874ae3f1e7c8b4a5ffb846e77c705ba02e2543789d66fc032b6606a8d8888eb6239a2abe5897ce83f78dcdcfcb027d6ea69aa6fe9@163.172.157.61:30303",
        "enode://ce6854c2c77a8800fcc12600206c344b8053bb90ee3ba280e6c4f18f3141cdc5ee80bcc3bdb24cbc0e96dffd4b38d7b57546ed528c00af6cd604ab65c4d528f6@163.172.153.124:30303",
        "enode://00ae60771d9815daba35766d463a82a7b360b3a80e35ab2e0daa25bdc6ca6213ff4c8348025e7e1a908a8f58411a364fe02a0fb3c2aa32008304f063d8aaf1a2@163.172.132.85:30303",
        "enode://86ebc843aa51669e08e27400e435f957918e39dc540b021a2f3291ab776c88bbda3d97631639219b6e77e375ab7944222c47713bdeb3251b25779ce743a39d70@212.47.254.155:30303",
        "enode://a1ef9ba5550d5fac27f7cbd4e8d20a643ad75596f307c91cd6e7f85b548b8a6bf215cca436d6ee436d6135f9fe51398f8dd4c0bd6c6a0c332ccb41880f33ec12@51.15.218.125:30303"]

    is_wait_sync = False
    is_synced = False

    def __init__(self, eth_value, container_command=None, bootnodes=None, shh=False, version='latest', description=None,
                 init_time=1,
                 is_wait_sync=False):
        port = Geth.port_default + Geth.port.increment()
        json_rpc_port = Geth.json_rpc_port_default + Geth.json_rpc_port.increment()

        docker_command = 'docker run -i --rm -p {json_rpc_port}:8545 -p {port}:30303 ' \
                         '-v {eth_value}:/root/.ethereum'.format(
            json_rpc_port=json_rpc_port, port=port, eth_value=eth_value)

        if container_command is None:
            container_command = Geth.ropsten_defaults

        if bootnodes is None:
            self.bootnodes = self.ropsten_bootnodes
        else:
            self.bootnodes = bootnodes
        container_command += " --bootnodes=\"{bootnodes}\"".format(bootnodes=','.join(self.bootnodes))

        if shh is True:
            container_command += " --shh"

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
