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
from quiver.benchmark_extraction import get_document_metadata

def test_get_eval_dirs():
    workspace_dir = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_eval_dirs(workspace_dir)
    expected = [workspace_dir + 'OCR-D-EVAL-SEG-PAGE',
        workspace_dir + 'OCR-D-EVAL-SEG-LINE',
        workspace_dir + 'OCR-D-EVAL-SEG-BLOCK']

    assert result == expected

def test_get_eval_jsons():
    workspace_dir = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_eval_jsons(workspace_dir)
    expected = {
        workspace_dir + 'OCR-D-EVAL-SEG-BLOCK':
            [workspace_dir + 'OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json',
            workspace_dir + 'OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0008.json',
            workspace_dir + 'OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0009.json'],
        workspace_dir + 'OCR-D-EVAL-SEG-LINE':
            [workspace_dir + 'OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0007.json',
            workspace_dir + 'OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0008.json',
            workspace_dir + 'OCR-D-EVAL-SEG-LINE/OCR-D-EVAL-SEG-LINE_0009.json'],
        workspace_dir + 'OCR-D-EVAL-SEG-PAGE':
            [workspace_dir + 'OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0007.json',
            workspace_dir + 'OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0008.json',
            workspace_dir + 'OCR-D-EVAL-SEG-PAGE/OCR-D-EVAL-SEG-PAGE_0009.json']
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
            'page_id': 'phys_0007',
            'cer': 0.07124352331606218,
            'processing_time': 2.0
        }

    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    json_file = workspace_path + 'OCR-D-EVAL-SEG-BLOCK/OCR-D-EVAL-SEG-BLOCK_0007.json'
    mets_path = workspace_path + 'mets.xml'
    result = get_metrics_for_page(json_file, mets_path)

    assert result == expected

def test_get_mean_cer():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_mean_cer(workspace_path, 'SEG-LINE')

    assert result == 0.10240852523716282

def test_cer_get_min_max():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_cer_min_max(workspace_path, 'SEG-LINE')

    assert result == [0.07124352331606218, 0.1306122448979592]

def test_get_eval_tool():
    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
    result = get_eval_tool(mets_path)
    assert result == 'ocrd-dinglehopper vNone'

def test_get_workflow_model():
    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
    result = get_workflow_model(mets_path)
    assert result == 'Fraktur_GT4HistOCR'

def test_get_workflow_steps():
    mets_path = 'tests/assets/benchmarking/16_ant_complex/mets.xml'
    result = get_workflow_steps(mets_path)    
    assert result == ['ocrd-tesserocr-recognize']

def test_get_gt_workspace():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_gt_workspace(workspace_path)    
    assert result['@id'] == 'https://github.com/OCR-D/quiver-data/blob/main/16_ant_complex.ocrd.zip'
    assert result['label'] == 'GT workspace 16th century antiqua'

def test_get_ocr_workflow():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_workflow(workspace_path, 'ocr')
    assert result['@id'] == 'https://github.com/OCR-D/quiver-back-end/blob/main/workflows/ocrd_workflows/minimal_ocr.txt'
    assert result['label'] == 'OCR Workflow minimal_ocr'

def test_get_eval_workflow():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_workflow(workspace_path, 'eval')
    assert result['@id'] == 'https://github.com/OCR-D/quiver-back-end/blob/main/workflows/ocrd_workflows/dinglehopper_eval.txt'
    assert result['label'] == 'Evaluation Workflow dinglehopper_eval'

def test_get_eval_workspace():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_workspace(workspace_path, 'evaluation')
    assert result['@id'] == 'https://github.com/OCR-D/quiver-back-end/blob/main/workflows/results/16_ant_complex_evaluation.zip'
    assert result['label'] == 'Evaluation workspace for 16_ant_complex'

def test_get_ocr_workspace():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_workspace(workspace_path, 'ocr')
    assert result['@id'] == 'https://github.com/OCR-D/quiver-back-end/blob/main/workflows/results/16_ant_complex_ocr.zip'
    assert result['label'] == 'OCR workspace for 16_ant_complex'

def test_get_document_metadata():
    workspace_path = 'tests/assets/benchmarking/16_ant_complex/'
    result = get_document_metadata(workspace_path)
    assert result['eval_workflow_url'] == 'https://github.com/OCR-D/quiver-back-end/tree/main/workflows/ocrd_workflows/dinglehopper.txt'
    assert result['eval_data'] == 'https://github.com/OCR-D/quiver-back-end/TODO'
    assert result['data_properties']['fonts'] == ['Antiqua']
    assert result['data_properties']['publication_year'] == '16th century'
    #assert result['data_properties']['number_of_pages'] == ''
    assert result['data_properties']['layout'] == 'complex'
