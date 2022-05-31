.PHONY: repos.json
repos.json:
	ocrd-kwalitee json > "$@"
