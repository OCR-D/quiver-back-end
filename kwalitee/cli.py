import click
from pathlib import Path
from ocrd.decorators import ocrd_loglevel
from ocrd_utils import getLogger
from yaml import safe_load
import json
from pkg_resources import resource_filename
from os import remove

from .filter import filter_release_projects
from .repo import Repo
from .release import get_releases

def _check_cloned(ctx):
    uncloned = []
    for repo in ctx.repos:
        if not repo.is_cloned():
            uncloned.append(repo)
    if uncloned:
        raise Exception("Some repos not yet cloned: %s" % [str(r) for r in uncloned])

class CliCtx():
    def __init__(self, config_file):
        self.log = getLogger('ocrd.kwalitee')
        with open(config_file, 'r') as f_config_file:
            self.config = safe_load(f_config_file.read())
            self.repos = []
            for repo_desc in self.config['repolist']:
                url = repo_desc['url']
                official = repo_desc.get('official', False)
                compliant_cli = repo_desc.get('compliant_cli', False)
                self.repos.append(Repo(self.config, url, official, compliant_cli))
pass_ctx = click.make_pass_decorator(CliCtx)

@click.group()
@click.option('-c', '--config-file', help="", default=resource_filename(__name__, 'config.yml'))
@ocrd_loglevel
@click.pass_context
def cli(ctx, config_file, **kwargs): # pylint: disable=unused-argument
    ctx.obj = CliCtx(config_file)

@cli.command('clone', help='''

        Clone all repos
''')
@pass_ctx
def clone_all(ctx):
    for repo in ctx.repos:
        if repo.is_cloned():
            ctx.log.info("Already cloned %s" % repo)
        else:
            ctx.log.info("Cloning %s" % repo)
            repo.clone()

@cli.command('pull', help='''

        Pull all repos
''')
@pass_ctx
def pull_all(ctx):
    _check_cloned(ctx)
    for repo in ctx.repos:
        ctx.log.info("Pulling %s" % repo)
        repo.pull()


@cli.command('json', help='''

    Generate JSON

''')
@click.option('-o', '--output', help="Output file. Omit to print to STDOUT")
@pass_ctx
def generate_json(ctx, output=None):
    ret = []
    _check_cloned(ctx)
    for repo in ctx.repos:
        ctx.log.info("# Assessing %s" % repo.id)
        repo.clone()
        ret.append(repo.to_json())
    json_str = json.dumps(ret, indent=4, sort_keys=True)
    if output:
        Path(output).write_text(json_str)
    else:
        print(json_str)


@cli.command('releases', help='''

    Generate JSON for ocrd_all releases

''')
@click.option('-o', '--output', help="Output file. '-' to print to STDOUT")
def generate_ocrd_all_releases(output=None):
    ret = get_releases()
    filtered = filter_release_projects(ret)
    json_str = json.dumps(filtered, indent=4, sort_keys=True)
    if output:
        Path(output).write_text(json_str, encoding='utf-8')
    else:
        print(json_str)


@cli.command('dep-conflicts', help='''

    Generate JSON for possibly conflicting depencies. The output is written to 'dep_conflicts.json'.

''')
def generate_dependency_conflicts():
    '''
    Generate JSON for possibly conflicting depencies
    '''
    
    # revert dependencies
    f = open('deps.json')
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
    # remove old version of dep_conflicts.json
    remove('dep_conflicts.json')
    Path('dep_conflicts.json').write_text(json_str, encoding='utf-8')


@cli.command('ocrd-tool')
@click.option('-o', '--output', help="Output file. Omit to print to STDOUT")
@pass_ctx
def generate_tool_json(ctx, output=None):
    '''
    Return one big list of ocrd tools
    '''
    ret = {}
    _check_cloned(ctx)
    for repo in ctx.repos:
        ret = {**ret, **repo.get_ocrd_tools()}
    json_str = json.dumps(ret, indent=4, sort_keys=True)
    if output:
        Path(output).write_text(json_str)
    else:
        print(json_str)
