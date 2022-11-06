from fastapi import FastAPI
import json
from typing import Union
from typing import Dict
from pathlib import Path

app = FastAPI()


@app.post("/nextflow/")
def save_workflow(item: Dict[str, Union[str, float,Dict]]):
    filtered = filter_result(item)
    json_str = json.dumps(filtered, indent=4, sort_keys=True)
    event = filtered['event']
    output_name = filtered['runName'] + filtered['runId']
    output = 'workflows/results/' + output_name + '_' + event + '.json'
    Path(output).write_text(json_str, encoding='utf-8')

def filter_result(item: Dict[str, Union[str, float,Dict]]):
    return item
