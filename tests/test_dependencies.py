import json

def test_core_deps():
    with open('data/core_deps.txt', 'r', encoding='utf-8') as file:
        expected = ['anyio',
            'atomicwrites',
            'attrs',
            'bagit',
            'bagit-profile',
            'bcrypt',
            'beanie',
            'beautifulsoup4',
            'blinker',
            'certifi',
            'cffi',
            'charset-normalizer',
            'click',
            'cryptography',
            'Deprecated',
            'dnspython',
            'docker',
            'fastapi',
            'filelock',
            'filetype',
            'Flask',
            'frozendict',
            'future',
            'gdown',
            'h11',
            'idna',
            'itsdangerous',
            'Jinja2',
            'jsonschema',
            'lazy-model',
            'lxml',
            'MarkupSafe',
            'memory-profiler',
            'motor',
            'numpy',
            'ocrd',
            'ocrd-modelfactory',
            'ocrd-models',
            'ocrd-network',
            'ocrd-utils',
            'ocrd-validators',
            'opencv-python-headless',
            'packaging',
            'paramiko',
            'pika',
            'Pillow',
            'psutil',
            'pycparser',
            'pydantic',
            'pymongo',
            'PyNaCl',
            'pyrsistent',
            'PySocks',
            'PyYAML',
            'requests',
            'shapely',
            'six',
            'sniffio',
            'soupsieve',
            'sparklines',
            'starlette',
            'toml',
            'tqdm',
            'typing_extensions',
            'urllib3',
            'uvicorn',
            'websocket-client',
            'Werkzeug',
            'wrapt']
        contents = file.read().splitlines()
        result_list = []
        for entry in contents:
            result_list.append(entry.split('=')[0])
        assert result_list == expected

def test_filtering():
    #ocrd_olahd_client has only very few deps apart from ocrd core
    expected = ['requests-toolbelt']
    olahd_client = get_processor('ocrd_olahd_client')
    print(list(olahd_client.keys()))

    assert list(olahd_client.keys()) == expected

def test_filtering_empty_result():
    # core will naturally be empty because we filter against it
    expected = {}
    core = get_processor('core')

    assert core == expected

def get_processor(name: str):
    with open('data/deps.json', 'r', encoding='utf-8') as f:
        json_file = json.load(f)
    return json_file[name]
