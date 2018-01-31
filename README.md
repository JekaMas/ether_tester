## Executing a use case

```shell
make run usecase=<usecase-file-name> # usecase-file-name is the name of a file in ./usecases/
```

e.g.
```shell
make run usecase=create_2_accounts_with_and_without_whisper
```

## Start new test cluster

```
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
```


## Run test scenario with params and print stats

```
# create account case
cluster.collect_stats(60, ['personal.newAccount(\"passphrase\")', 'miner.setEtherbase(\"$result0\")'])

cluster.print_stats()

cluster.stop()
```

## Use already running container
If can use any container already running without starting new one.

```
geth_docker_name1 = "ethereum1"
geth1 = ContainerManager(name=geth_docker_name1)
```
