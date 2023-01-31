dependencies: init
	rm data/deps.json data/dep_conflicts.json || echo "No data to delete. Continue JSON creation."
	bash dependencies.sh
	python3 quiver/dependencies.py

.PHONY: data/repos.json
repos.json: dependencies
	quiver-ocrd repo json -o data/repos.json

init:
	git submodule update --init
	git submodule foreach --recursive 'git submodule update --init' || echo 0

.PHONY: data/ocrd_all_releases.json
releases: init
	quiver-ocrd releases -o data/ocrd_all_releases.json

benchmarks: init clean-workspaces
	quiver-ocrd benchmarks

clean-workspaces:
	rm -rf workflows/workspaces
	rm -rf workflows/nf-results
	rm -rf workflows/ocrd_workflows/*.nf