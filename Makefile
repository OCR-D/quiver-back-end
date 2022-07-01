.PHONY: repos.json
repos.json:
	ocrd-kwalitee json > "$@"

init-deps:
	bash dependencies.sh init
	ocrd-kwalitee dep-conflicts

update-deps:
	bash dependencies.sh update