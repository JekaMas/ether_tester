from .geth import Geth


# todo: implement
class Status(Geth):
    'docker build -f {status_path} -t status_image:{tag} .'
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

