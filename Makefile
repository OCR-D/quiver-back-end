dependencies:
	if [ -f 'deps.json' ]; then\
		$(MAKE) update-deps;\
	else\
		$(MAKE) init-deps;\
	fi

init-deps:
	bash dependencies.sh init
	ocrd-kwalitee dep-conflicts

update-deps:
	bash dependencies.sh update

.PHONY: repos.json
repos.json: dependencies
	ocrd-kwalitee json > "$@"