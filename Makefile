dependencies: init
	rm deps.json
	rm dep_conflicts.json
	bash dependencies.sh init
	python3 quiver/dependencies.py

.PHONY: repos.json
repos.json: dependencies
	ocrd-quiver repo json > "$@"

init:
	git submodule update --init
	git submodule foreach --recursive 'git submodule update --init' || echo 0
