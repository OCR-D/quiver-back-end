import json
from pathlib import Path
from sys import exit

import click
from ocrd.decorators import ocrd_loglevel
from ocrd_utils import getLogger
from ocrd_validators.json_validator import JsonValidator
from pkg_resources import resource_filename
from yaml import safe_load
import subprocess

from .filter import filter_release_projects
from .release import get_releases
from .repo import Repo
from .benchmark_extraction import make_result_json
from .summarize_benchmarks import get_json_files, summarize_to_one_file


@click.group()
def cli():
    pass

def _check_cloned(ctx):
    uncloned = []
    for repo in ctx.repos:
        if not repo.is_cloned():
            uncloned.append(repo)
    if uncloned:
        raise Exception("Some repos not yet cloned: %s" % [str(r) for r in uncloned])


class CliCtx():
    def __init__(self, config_file):
        self.log = getLogger('ocrd.quiver')
        with open(config_file, 'r') as f_config_file:
            self.config = safe_load(f_config_file.read())
            self.repos = []
            for repo_desc in self.config['repolist']:
                url = repo_desc['url']
                official = repo_desc.get('official', False)
                compliant_cli = repo_desc.get('compliant_cli', False)
                self.repos.append(Repo(self.config, url, official, compliant_cli))
pass_ctx = click.make_pass_decorator(CliCtx)


@click.group(help="Managing repos and related info")
@click.option('-c', '--config-file', help="", default=resource_filename(__name__, 'config.yml'))
@ocrd_loglevel
@click.pass_context
def repo(ctx, config_file, **kwargs): # pylint: disable=unused-argument
    ctx.obj = CliCtx(config_file)


@repo.command('clone', help='''

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


@repo.command('pull', help='''

        Pull all repos
''')
@pass_ctx
def pull_all(ctx):
    _check_cloned(ctx)
    for repo in ctx.repos:
        ctx.log.info("Pulling %s" % repo)
        repo.pull()


@repo.command('json', help='''

    Generate data/repos.json

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


@repo.command('ocrd-tool')
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


@cli.command("validate", help="Validate created JSON files")
@click.option('-f', '--file',
    type=click.Choice(['data/repos.json', 'data/ocrd_all_releases.json']),
    help="The file to be validated.",
    default="data/repos.json",
    show_default=True)
def json_validate(file):

    with open(file, 'r', encoding='utf-8') as f:
        instance = json.load(f)

    schema_path = resource_filename(__name__, 'schemas/' + file)
    with open(schema_path, 'r', encoding='utf-8') as s:
        schema = json.load(s)

    _inform_of_result(JsonValidator.validate(instance, schema))
    

def _inform_of_result(report):
    if not report.is_valid:
        print(report.to_xml())
        exit(1)


@cli.command("releases", help="Generate JSON for ocrd_all releases")
@click.option('-o', '--output', help="Output file. '-' to print to STDOUT")
def generate_ocrd_all_releases(output=None):
    ret = get_releases()
    filtered = filter_release_projects(ret)
    json_str = json.dumps(filtered, indent=4, sort_keys=True)
    if output:
        Path(output).write_text(json_str, encoding='utf-8')
    else:
        print(json_str)


@cli.command("benchmarks", help="Generate/update JSON for the workflow benchmarks")
def generate_benchmarks():
    subprocess.run(["workflows/execute_workflows.sh"], check=True)

@cli.command('benchmarks-extraction', help="...")
@click.argument('WORKSPACE_PATH')
@click.argument('WORKFLOW_PATH')
def benchmark_extraction_cli(workspace_path, workflow_path):
    workflow_name = Path(workflow_path).stem
    workspace_name = Path(workspace_path).parent.name
    mets_path = Path(workspace_path) / 'mets.xml'
    dictionary = make_result_json(workspace_path, mets_path)
    json_object = json.dumps(dictionary, indent=4)
    output = Path(workspace_path, f'{workspace_name}_{workflow_name}_result.json')
    with open(output, 'w', encoding='utf-8') as outfile:
        outfile.write(json_object)

cli.add_command(repo)

@cli.command('summarize-benchmarks', help="...")
def summarize_benchmarks_cli():
    summarize_to_one_file(get_json_files())
    print("Successfully summarized JSON files!")
