from pathlib import Path
import json

# revert dependencies
with open('data/deps.json', 'r', encoding='utf-8') as f:
    deps_json = json.load(f)

    result = {}
    for dependency in deps_json:
        deps = deps_json[dependency]
        for pkg, version in deps.items():
            if not pkg in result:
                result[pkg] = {}
                result[pkg][dependency] = version
            else:
                result[pkg][dependency] = version

    # toss every dependency that only has one version.
    # it'll never have any conflicts because a) only one project uses it or b) several projects use the same version.
    filtered = {}
    for pkg in result:
        versions = result[pkg].values()
        versions_wo_duplicates = list(set(versions))
        if not len(result[pkg]) == 1 and not len(versions_wo_duplicates) == 1:
            filtered[pkg] = result[pkg]
    json_str = json.dumps(filtered, indent=4, sort_keys=True)
    Path('data/dep_conflicts.json').write_text(json_str, encoding='utf-8')