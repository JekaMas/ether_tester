run:
	python3 -m main.py

deps: get-geth
	pip install -r requirement.txt

get-geth:
	docker pull ethereum/client-go
