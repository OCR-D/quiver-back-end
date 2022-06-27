import json

def test_core_deps():
    with open('core_deps.txt', 'r') as file:
        expected = ['atomicwrites==1.4.0',
                    'attrs==21.4.0',
                    'bagit==1.8.1',
                    'bagit-profile==1.3.1',
                    'certifi==2022.6.15',
                    'charset-normalizer==2.0.12',
                    'click==8.1.3',
                    'Deprecated==1.2.0',
                    'Flask==2.1.2',
                    'idna==3.3',
                    'importlib-metadata==4.12.0',
                    'importlib-resources==5.8.0',
                    'itsdangerous==2.1.2',
                    'Jinja2==3.1.2',
                    'jsonschema==4.6.0',
                    'lxml==4.9.0',
                    'MarkupSafe==2.1.1',
                    'numpy==1.21.6',
                    'ocrd==2.35.0',
                    'ocrd-modelfactory==2.35.0',
                    'ocrd-models==2.35.0',
                    'ocrd-utils==2.35.0',
                    'ocrd-validators==2.35.0',
                    'opencv-python-headless==4.6.0.66',
                    'Pillow==9.1.1',
                    'pyrsistent==0.18.1',
                    'PyYAML==6.0',
                    'requests==2.28.0',
                    'Shapely==1.8.2',
                    'typing_extensions==4.2.0',
                    'urllib3==1.26.9',
                    'Werkzeug==2.1.2',
                    'wrapt==1.14.1',
                    'zipp==3.8.0']
        result = file.read().splitlines()
        assert result == expected

def test_filtering():
    #ocrd_olahd_client has only very few deps apart from ocrd
    expected = [{'importlib-metadata': '4.11.4'}, {'ocrd-olahd-client': '0.0.1'}, {'requests-toolbelt': '0.9.1'}]
    f = open('deps.json')
    json_file = json.load(f)
    olahd_client = json_file[25]['ocrd_olahd_client']

    assert olahd_client == expected

def test_filtering_empty_result():
    # core will naturally be empty because we filter against it
    expected = []
    f = open('deps.json')
    json_file = json.load(f)
    olahd_client = json_file[1]['core']

    assert olahd_client == expected
