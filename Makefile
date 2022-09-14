dependencies: init
	rm deps.json
	rm dep_conflicts.json
	bash dependencies.sh init
	python3 kwalitee/dependencies.py

.PHONY: repos.json
repos.json: dependencies
	ocrd-kwalitee repo json > "$@"

init:
	git submodule update --init
	git submodule foreach --recursive 'git submodule update --init' || echo 0
