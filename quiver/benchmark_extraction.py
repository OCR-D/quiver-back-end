"""This module is responsible for creating the resulting JSON file of the
benchmarking. It extracts the relevant information from the NextFlow processes. """

import json
import sys
from os import scandir, listdir
from re import search
import xml.etree.ElementTree as ET


#{
 #   "eval_workflow_id": "wf2-data345-eval1",
 #   "label": "Workflow 2 on Data 345",
 #   "metadata": {
 #     "data_creation_workflow": "https://example.org/workflow/2",
 #     "workflow_steps": {
 #       "0": "Processor A",
 #       "1": "Processor B"
 #     },
 #     "workflow_model": "Fraktur_GT4HistOCR",
 #     "eval_workflow_url": "https://example.org/workflow/eval1",
 #     "eval_data": "https://example.org/workspace/345",
 #     "eval_tool": "dinglehopper",
 #     "gt_data": "https://gt.ocr-d.de/workspace/789",
 #     "data_properties": {
 #       "fonts": ["antiqua", "fraktur"],
 #       "publication_year": "19. century",
 #       "number_of_pages": "100",
 #       "layout": "simple"
 #     }
 #   },
 #   "evaluation_results": {
 #     "document_wide": {
 #       "wall_time": 1234,
 #       "cer": 0.88,
 #       "cer_min_max": [0.2, 0.57]
 #     },
 #     "by_page": [
 #       {
 #         "page_id": "PHYS_0001",
 #         "cer": 0.9,
 #         "processing_time": 2.0
 #       }
 #     ]
 #   }
 # }

def extract_benchmarks(workspace_path, mets_path):
    json_dirs = get_eval_jsons(workspace_path)

    result = {"evaluation_results":
    [
        make_document_wide_eval_results(json_dirs, workspace_path),
        {"by_page": make_eval_results_by_page(json_dirs, mets_path)}
    ]}

    return result

def make_document_wide_eval_results(json_dirs, workspace_path):
    return {'document_wide':
        {
            'wall_time': get_nf_completed_stats(workspace_path),
            'cer': get_mean_cer(workspace_path, 'SEG-LINE'),
            'cer_min_max': get_cer_min_max(workspace_path, 'SEG-LINE')
        }
    }

def get_nf_completed_stats(workspace_path):
    result_path = workspace_path + '/../../results/'

    for f in listdir(workspace_path + '/../../results'):
        if "process" not in f and "completed" in f:
            completed_file = f

    with open(result_path + completed_file, 'r', encoding='utf-8') as f:
        file = json.load(f)
        duration = file['metadata']['workflow']['duration']
    return duration


def get_mean_cer(workspace_path, gt_type):
    cers = get_cers_for_gt_type(workspace_path, gt_type)
    return sum(cers) / len(cers)

def get_cers_for_gt_type(workspace_path, gt_type):
    eval_jsons = []
    eval_dir_path = workspace_path + '/OCR-D-EVAL-' + gt_type + '/'
    for f in listdir(eval_dir_path):
        if "json" in f:
            eval_jsons.append(f)
    cers = []
    for eval_json in eval_jsons:
        with open(eval_dir_path + eval_json, 'r', encoding='utf-8') as f:
            json_file = json.load(f)
            cers.append(json_file['cer'])
    return cers

def get_cer_min_max(workspace_path, gt_type):
    cers = get_cers_for_gt_type(workspace_path, gt_type)
    return [min(cers), max(cers)]

def make_eval_results_by_page(json_dirs, mets_path):
    result = []
    for d in json_dirs:
        for file_path in json_dirs[d]:
            result.append(get_metrics_for_page(file_path, mets_path))

    return result

def get_eval_dirs(workspace_dir):
    list_subfolders_with_paths = [f.path for f in scandir(workspace_dir) if f.is_dir()]
    eval_dirs = [name for name in list_subfolders_with_paths if search('EVAL', name)]
    return eval_dirs


def get_eval_jsons(workspace_dir):
    eval_dirs = get_eval_dirs(workspace_dir)
    result = {}
    for eval_dir in eval_dirs:
        files_in_dir = [f.path for f in scandir(eval_dir) if f.is_file()]
        json_files = [name for name in files_in_dir if search('json', name)]
        result[eval_dir] = sorted(json_files)
    return result


def get_page_id(json_file_path, mets_path):
    json_file_name = get_file_name_from_path(json_file_path)
    gt_file_name = json_file_name.replace('EVAL', 'GT')
    with open(mets_path, 'r', encoding='utf-8') as f:
        tree = ET.parse(f)
        namespace = "{http://www.loc.gov/METS/}"
        e = tree.findall('//{0}fptr[@FILEID="{1}"]/..'.format(namespace, gt_file_name))

    return e[0].attrib['ID']


def get_file_name_from_path(json_file_path):
    json_file_name = json_file_path.split('/')[-1]
    name_wo_ext = json_file_name.split('.')[0]
    return name_wo_ext


def get_metrics_for_page(json_file_path, mets_path):
    page_id = get_page_id(json_file_path, mets_path)
    with open(json_file_path, 'r', encoding='utf-8') as file:
        eval_file = json.load(file)

        cer = eval_file["cer"]
    metrics = {
        "page_id": page_id,
        "cer": cer
    }

    return metrics

if __name__ == '__main__':
    workspace_path = sys.argv[1]
    workflow = sys.argv[2].split('/')[-1].split('.')[0]
    mets_path = workspace_path + 'mets.xml'

    dictionary = extract_benchmarks(workspace_path, mets_path)

    
    json_object = json.dumps(dictionary, indent=4)
    
    # Writing to sample.json
    with open(workspace_path + '/eval_result_' + workflow + '.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json_object)