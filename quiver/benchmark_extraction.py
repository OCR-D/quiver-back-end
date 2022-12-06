"""This module is responsible for creating the resulting JSON file of the
benchmarking. It extracts the relevant information from the NextFlow processes. """

import json
import sys
import xml.etree.ElementTree as ET
from os import listdir, scandir
import re
from typing import Any, Dict, List, Union

from .constants import *

#{
 #   "metadata": {
 #     "eval_workflow_url": "https://example.org/workflow/eval1",
 #     "eval_data": "https://example.org/workspace/345",
 #     "data_properties": {
 #       "fonts": ["antiqua", "fraktur"],
 #       "publication_year": "19. century",
 #       "number_of_pages": "100",
 #       "layout": "simple"
 #     }
 #   }
 # }

def make_result_json(workspace_path: str, mets_path: str) -> Dict[str, Union[str, Dict]]:
    data_name = get_workspace_name(workspace_path)
    return {
        'eval_workflow_id': 'wf-data'+ data_name + '-eval',
        'label': 'Workflow on data ' + data_name,
        'metadata': make_metadata(workspace_path, mets_path),
        'evaluation_results': extract_benchmarks(workspace_path, mets_path)
    }

def get_workspace_name(workspace_path: str) -> str:
    return workspace_path.split('/')[-2]

def make_metadata(workspace_path: str, mets_path: str) -> Dict[str, Union[str, Dict]]:
    return {
            'ocr_workflow': get_workflow(workspace_path, 'ocr'),
            'eval_workflow': get_workflow(workspace_path, 'eval'),
            'gt_workspace': get_gt_workspace(workspace_path),
            'ocr_workspace': get_workspace(workspace_path, 'ocr'),
            'eval_workspace': get_workspace(workspace_path, 'evaluation'),
            'workflow_steps': get_workflow_steps(mets_path),
            'workflow_model': get_workflow_model(mets_path),
            'document_metadata': ''
        }

def get_workflow(workspace_path: str, wf_type: str) -> Dict[str, str]:
    if wf_type == 'eval':
        pattern = r'eval.txt.nf'
    else:
        pattern = r'ocr.txt.nf'

    for file in listdir(workspace_path):
        result = re.search(pattern, file)
        if result:
            workflow = file.split('.')[0]
    url = f'{QUIVER_MAIN}/workflows/ocrd_workflows/{workflow}.txt'
    if wf_type == 'ocr':
        wf_name = 'OCR'
    else:
        wf_name = 'Evaluation'
    label = f'{wf_name} Workflow {workflow}'
    return {'@id': url,
        'label': label
    }

def get_workspace(workspace_path: str, ws_type: str) -> Dict[str, str]:
    workspace = get_workspace_name(workspace_path)
    url = f'{QUIVER_MAIN}/workflows/results/{workspace}_{ws_type}.zip'
    if ws_type == 'ocr':
        ws_name = 'OCR'
    else:
        ws_name = 'Evaluation'
    label = f'{ws_name} workspace for {workspace}'
    return {
        '@id': url,
        'label': label
    }

def get_element_from_mets(mets_path: str, xpath: str) -> List[str]:
    with open(mets_path, 'r', encoding='utf-8') as f:
        tree = ET.parse(f)
        return tree.findall(xpath)

def get_workflow_steps(mets_path: str) -> List[str]:
    xpath =f'.//{METS}agent[@ROLE="OTHER"]/{METS}name'
    name_elements = get_element_from_mets(mets_path, xpath)
    formatted_names = []
    for e in name_elements:
        formatted_names.append(e.text.split(' ')[0])

    return formatted_names

def get_workflow_model(mets_path: str) -> str:
    xpath = f'.//{METS}agent[@OTHERROLE="layout/segmentation/region"]/{METS}note[@{OCRD}option="parameter"]'
    parameters = get_element_from_mets(mets_path, xpath)[0].text
    params_json = json.loads(parameters)
    return params_json['model']

def get_eval_tool(mets_path: str) -> str:
    xpath = f'.//{METS}agent[@OTHERROLE="recognition/text-recognition"]/{METS}name'
    return get_element_from_mets(mets_path, xpath)[0].text

def get_gt_workspace(workspace_path: str) -> Dict[str, str]:
    current_workspace = get_workspace_name(workspace_path)
    url = f'{QUIVER_MAIN}/{current_workspace}.ocrd.zip'
    label = 'TODO'
    return {
        '@id': url,
        'label': label
    }

def extract_benchmarks(workspace_path: str, mets_path: str) -> Dict[str, Dict[str, Any]]:
    json_dirs = get_eval_jsons(workspace_path)

    return {
        'document_wide': make_document_wide_eval_results(workspace_path),
        'by_page': make_eval_results_by_page(json_dirs, mets_path)
    }

def make_document_wide_eval_results(workspace_path: str) -> Dict[str, Union[float, List[float]]]:
    return {
        'wall_time': get_nf_completed_stats(workspace_path),
        'cer': get_mean_cer(workspace_path, 'SEG-LINE'),
        'cer_min_max': get_cer_min_max(workspace_path, 'SEG-LINE')
    }

def get_nf_completed_stats(workspace_path: str) -> float:
    result_path = workspace_path + RESULTS
    workspace_name = get_workspace_name(workspace_path)

    for file_name in listdir(result_path):
        if 'ocr_completed' in file_name and workspace_name in file_name:
            completed_file = file_name

    with open(result_path + completed_file, 'r', encoding='utf-8') as f:
        file = json.load(f)
        duration = file['metadata']['workflow']['duration']
    return duration


def get_mean_cer(workspace_path: str, gt_type: str) -> float:
    cers = get_cers_for_gt_type(workspace_path, gt_type)
    return sum(cers) / len(cers)

def get_cers_for_gt_type(workspace_path: str, gt_type: str) -> List[float]:
    eval_jsons = []
    eval_dir_path = workspace_path + '/OCR-D-EVAL-' + gt_type + '/'
    for file_name in listdir(eval_dir_path):
        if 'json' in file_name:
            eval_jsons.append(file_name)
    cers = []
    for eval_json in eval_jsons:
        with open(eval_dir_path + eval_json, 'r', encoding='utf-8') as f:
            json_file = json.load(f)
            cers.append(json_file['cer'])
    return cers

def get_cer_min_max(workspace_path: str, gt_type: str) -> List[float]:
    cers = get_cers_for_gt_type(workspace_path, gt_type)
    return [min(cers), max(cers)]

def make_eval_results_by_page(json_dirs: str, mets_path: str) -> List[object]:
    result = []
    for d in json_dirs:
        for file_path in json_dirs[d]:
            result.append(get_metrics_for_page(file_path, mets_path))

    return result

def get_eval_dirs(workspace_dir: str) -> List[str]:
    list_subfolders_with_paths = [f.path for f in scandir(workspace_dir) if f.is_dir()]
    eval_dirs = [name for name in list_subfolders_with_paths if re.search('EVAL', name)]
    return eval_dirs


def get_eval_jsons(workspace_dir: str) -> Dict[str, List[str]]:
    eval_dirs = get_eval_dirs(workspace_dir)
    result = {}
    for eval_dir in eval_dirs:
        files_in_dir = [f.path for f in scandir(eval_dir) if f.is_file()]
        json_files = [name for name in files_in_dir if re.search('json', name)]
        result[eval_dir] = sorted(json_files)
    return result


def get_page_id(json_file_path: str, mets_path: str) -> str:
    json_file_name = get_file_name_from_path(json_file_path)
    gt_file_name = json_file_name.replace('EVAL', 'GT')
    xpath = f'.//{METS}fptr[@FILEID="{gt_file_name}"]/..'
    return get_element_from_mets(mets_path, xpath)[0].attrib['ID']


def get_file_name_from_path(json_file_path: str) -> str:
    json_file_name = json_file_path.split('/')[-1]
    name_wo_ext = json_file_name.split('.')[0]
    return name_wo_ext


def get_metrics_for_page(json_file_path: str, mets_path: str) -> Dict[str, Union[str, float]]:
    with open(json_file_path, 'r', encoding='utf-8') as file:
        eval_file = json.load(file)

    return {
        'page_id': get_page_id(json_file_path, mets_path),
        'cer': eval_file['cer']
    }
