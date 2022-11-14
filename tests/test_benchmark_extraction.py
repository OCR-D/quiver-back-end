import json
from quiver.benchmark_extraction import get_page_id
from quiver.benchmark_extraction import get_eval_dirs
from quiver.benchmark_extraction import get_eval_jsons
from quiver.benchmark_extraction import get_metrics_for_page
from quiver.benchmark_extraction import get_mean_cer
from quiver.benchmark_extraction import get_cer_min_max
from quiver.benchmark_extraction import get_eval_tool
from quiver.benchmark_extraction import get_workflow_model
from quiver.benchmark_extraction import get_workflow_steps
from quiver.benchmark_extraction import get_gt_data_url

def test_get_eval_dirs():
    workspace_dir = 'tests/assets/benchmarking/16_ant_complex'
    result = get_eval_dirs(workspace_dir)
    expected = ['tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-PAGE',
        'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-LINE',
        'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK']

    assert result == expected

def test_get_eval_jsons():
    workspace_dir = 'tests/assets/benchmarking/16_ant_complex'
    result = get_eval_jsons(workspace_dir)
    expected = {
        "tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK":
            ['tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json',
            'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0008.json',
            'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0009.json'],
        "tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-LINE":
            ['tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0007.json',
            'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0008.json',
            'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0009.json'],
        "tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-PAGE":
            ['tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0007.json',
            'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0008.json',
            'tests/assets/benchmarking/16_ant_complex/OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0009.json']
    }

    assert result ==expected

def test_get_page_id():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    json_file_path = workspace_path + 'OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json'
    mets_path = workspace_path + 'mets.xml'
    result = get_page_id(json_file_path, mets_path)
    expected = 'phys_0007'

    assert result == expected

def test_get_metrics_for_page():
    expected = {
            "page_id": "phys_0007",
            "cer": 0.07124352331606218,
            "processing_time": 2.0
        }

    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    json_file = workspace_path + 'OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json'
    mets_path = workspace_path + 'mets.xml'
    result = get_metrics_for_page(json_file, mets_path)

    assert result == expected

def test_get_mean_cer():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex'
    result = get_mean_cer(workspace_path, 'SEG-LINE')

    assert result == 0.10240852523716282

def test_cer_get_min_max():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex'
    result = get_cer_min_max(workspace_path, 'SEG-LINE')

    assert result == [0.07124352331606218, 0.1306122448979592]

def test_get_eval_tool():
    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
    result = get_eval_tool(mets_path)
    assert result == "ocrd-dinglehopper vNone"

def test_get_workflow_model():
    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
    result = get_workflow_model(mets_path)
    assert result == "Fraktur_GT4HistOCR"

def test_get_workflow_steps():
    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
    result = get_workflow_steps(mets_path)    
    assert result == ['ocrd-tesserocr-recognize',
        'ocrd-dinglehopper',
        'ocrd-dinglehopper',
        'ocrd-dinglehopper']

def test_get_gt_data_url():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_gt_data_url(workspace_path)    
    assert result == "https://github.com/OCR-D/quiver-data/blob/main/16_ant_complex.ocrd.zip"
