"""
Tests for quiver/benchmark_extraction.py
"""

from quiver.benchmark_extraction import get_page_id
from quiver.benchmark_extraction import get_eval_dirs
from quiver.benchmark_extraction import get_eval_jsons
from quiver.benchmark_extraction import get_metrics_for_page
from quiver.benchmark_extraction import get_mean_cer
from quiver.benchmark_extraction import get_cer_min_max
from quiver.benchmark_extraction import get_eval_tool
from quiver.benchmark_extraction import get_workflow_model
from quiver.benchmark_extraction import get_workflow_steps
from quiver.benchmark_extraction import get_gt_workspace
from quiver.benchmark_extraction import get_workflow
from quiver.benchmark_extraction import get_workspace
from quiver.constants import QUIVER_MAIN

WORKSPACE_DIR = 'tests/assets/benchmarking/16_ant_complex/'
METS_PATH = 'tests/assets/benchmarking/16_ant_complex/mets.xml'

def test_get_eval_dirs():
    result = get_eval_dirs(WORKSPACE_DIR)
    expected = [f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-PAGE',
        f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-LINE',
        f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-BLOCK']

    assert result == expected

def test_get_eval_jsons():
    result = get_eval_jsons(WORKSPACE_DIR)
    expected = {
        f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-BLOCK':
            [f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json',
            f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0008.json',
            f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0009.json'],
        f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-LINE':
            [f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0007.json',
            f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0008.json',
            f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0009.json'],
        f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-PAGE':
            [f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0007.json',
            f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0008.json',
            f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0009.json']
    }

    assert result ==expected

def test_get_page_id():
    json_file_path = f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json'
    result = get_page_id(json_file_path, METS_PATH)
    expected = 'phys_0007'

    assert result == expected

def test_get_metrics_for_page():
    expected = {
            'page_id': 'phys_0007',
            'cer': 0.07124352331606218,
            'processing_time': 2.0
        }

    json_file = f'{WORKSPACE_DIR}OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json'
    result = get_metrics_for_page(json_file, METS_PATH)

    assert result == expected

def test_get_mean_cer():
    result = get_mean_cer(WORKSPACE_DIR, 'SEG-LINE')

    assert result == 0.10240852523716282

def test_cer_get_min_max():
    result = get_cer_min_max(WORKSPACE_DIR, 'SEG-LINE')

    assert result == [0.07124352331606218, 0.1306122448979592]

def test_get_eval_tool():
    result = get_eval_tool(METS_PATH)
    assert result == 'ocrd-dinglehopper vNone'

def test_get_workflow_model():
    result = get_workflow_model(METS_PATH)
    assert result == 'Fraktur_GT4HistOCR'

def test_get_workflow_steps():
    result = get_workflow_steps(METS_PATH)
    assert result == ['ocrd-tesserocr-recognize']

def test_get_gt_workspace():
    result = get_gt_workspace(WORKSPACE_DIR) 
    assert result['@id'] == f'{QUIVER_MAIN}/16_ant_complex.ocrd.zip'
    assert result['label'] == 'GT workspace 16th century antiqua'

def test_get_ocr_workflow():
    result = get_workflow(WORKSPACE_DIR, 'ocr')
    assert result['@id'] == f'{QUIVER_MAIN}/workflows/ocrd_workflows/minimal_ocr.txt'
    assert result['label'] == 'OCR Workflow minimal_ocr'

def test_get_eval_workflow():
    result = get_workflow(WORKSPACE_DIR, 'eval')
    assert result['@id'] == f'{QUIVER_MAIN}/workflows/ocrd_workflows/dinglehopper_eval.txt'
    assert result['label'] == 'Evaluation Workflow dinglehopper_eval'

def test_get_eval_workflow():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_workflow(workspace_path, 'eval')
    assert result['@id'] == 'https://github.com/OCR-D/quiver-back-end/blob/main/workflows/ocrd_workflows/dinglehopper_eval.txt'
    assert result['label'] == 'Evaluation Workflow dinglehopper_eval'

def test_get_eval_workspace():
    result = get_workspace(WORKSPACE_DIR, 'evaluation')
    assert result['@id'] == f'{QUIVER_MAIN}/workflows/results/16_ant_complex_evaluation.zip'
    assert result['label'] == 'Evaluation workspace for 16_ant_complex'

def test_get_ocr_workspace():
    result = get_workspace(WORKSPACE_DIR, 'ocr')
    assert result['@id'] == f'{QUIVER_MAIN}/workflows/results/16_ant_complex_ocr.zip'
    assert result['label'] == 'OCR workspace for 16_ant_complex'
