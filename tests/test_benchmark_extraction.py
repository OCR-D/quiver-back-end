import json
from quiver.benchmark_extraction import get_page_id
from quiver.benchmark_extraction import get_eval_dirs
from quiver.benchmark_extraction import get_eval_jsons
from quiver.benchmark_extraction import get_metrics_for_page

def test_get_eval_dirs():
    root_dir = 'tests/assets/benchmarking/16_ant_complex'
    result = get_eval_dirs(root_dir)
    expected = ['tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-PAGE',
        'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-LINE',
        'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK']

    assert result == expected

def test_get_eval_jsons():
    root_dir = 'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK'
    result = get_eval_jsons(root_dir)
    expected = [
        'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0008.json',
        'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json',
        'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0009.json'
    ]

    assert result ==expected

def test_get_page_id():
    json_file_path = 'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json'
    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
    result = get_page_id(json_file_path, mets_path)
    expected = 'phys_0007'

    assert result == expected

#def test_get_metrics_by_page():
#    expected = {"by_page": 
#    [
#        {
#            "page_id": "PHYS_0001",
#            "cer": 0.9,
#            "processing_time": 2.0
#        },
#        {
#            "page_id": "PHYS_0001",
#            "cer": 0.9,
#            "processing_time": 2.0
#        }
#    ]}
#
#    json_files = [
#        "tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json", 
#        "tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0008.json"
#    ]
#
#    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
#    result = []
#    for file in json_files:
#        result.append(get_metrics_by_page(file, mets_path))
#
#    assert result == expected
#
def test_get_metrics_for_page():
    expected = {
            "page_id": "phys_0007",
            "cer": 0.07124352331606218,
            "processing_time": 2.0
        }

    json_file = "tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json"
    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
    result = get_metrics_for_page(json_file, mets_path)

    assert result == expected
