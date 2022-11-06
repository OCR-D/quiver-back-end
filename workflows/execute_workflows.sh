#!/bin/bash

ROOT=$PWD
WORKFLOW_DIR="$ROOT"/workflows/ocrd_workflows
WORKSPACE_DIR="$ROOT"/workflows/workspaces


# the following code block is for local development only.

for DATA in "$WORKSPACE_DIR"/*
do
    rm -rf "$DATA"
done


# update the data from quiver-data repository if necessary
echo "Update quiver-data if necessary …"
cd submodules/quiver-data || exit
git fetch
git merge origin/main

echo "Restore OCR-D workspaces from BagIts …"
for BAGIT in *.zip
do
    ocrd zip spill "$BAGIT" -d "$WORKSPACE_DIR" > log.log
done
echo "BagIt extraction completed."

cd "$ROOT" || exit

# convert a ocrd process workflow to a NextFlow workflow with the OtoN converter
echo "Update OtoN converter if necessary …"
cd submodules/oton || exit
git fetch
git checkout -- oton/config.toml
git checkout -- oton/converter.py
git merge origin/master

echo "Adjust OtoN settings …"
sed -i "s \$projectDir/ocrd-workspace/ $WORKSPACE_DIR/CURRENT/ g" oton/config.toml
sed -i "s venv37-ocrd/bin/activate git/ocrd_all/venv/bin/activate g" oton/config.toml
echo "Done."

echo "Installing OtoN …"
VENV=$ROOT'/venv/bin/python'
CMD="-m pip install $ROOT/submodules/oton"
$VENV $CMD
echo "OtoN installation done."

cd "$WORKFLOW_DIR" || exit

echo "Convert OCR-D workflows to NextFlow …"

source $ROOT'/venv/bin/activate'

for FILE in *.txt
do
    oton convert -I $FILE -O $FILE.nf --dockerized
done


#cd "$ROOT" || exit

# download the necessary models if not available

echo "Download the necessary models if not available"
if [[ ! -f $ROOT/models/ocrd-tesserocr-recognize/Fraktur_GT4HistOCR.traineddata ]]
then
    mkdir -p "$ROOT"/models
    docker run --volume "$PWD"/models:/usr/local/share/ocrd-resources -- ocrd/all:maximum ocrd resmgr download ocrd-tesserocr-recognize Fraktur_GT4HistOCR.traineddata
fi

# execute this workflow on the existing data (incl. evaluation)

cd "$WORKSPACE_DIR" || exit

# start webserver for evaluation
uvicorn api:app --app-dir "$ROOT"/quiver &

# for all data sets…
for WS_DIR in "$WORKSPACE_DIR"/*/
do
    echo "Switching to $WS_DIR."
    # … copy all workflows in the right place …
    for WORKFLOW in "$WORKFLOW_DIR"/*.nf
    do
        cp "$WORKFLOW" "$WS_DIR"
    done

    # … adjust workflow files to corpus and run workflows.
    for WORKFLOW in "$WS_DIR"/*.nf
    do
        sed -i "s INPUT_DIR . g" "$WORKFLOW"
        sed -i "s OUTPUT_DIR result g" "$WORKFLOW"
        DIR_NAME=$(echo $WS_DIR | rev | cut -d'/' -f 2 | rev)
        sed -i "s CURRENT $DIR_NAME g" "$WORKFLOW"
        nextflow run "$WORKFLOW" -with-weblog https://127.0.0.1:8000
    done   
    # create a result JSON according to the specs
    touch "$WORKFLOW"_benchmarks.json
        
    echo "Get Benchmark JSON …"
    VENV=$ROOT'/venv/bin/python'
    CMD="$ROOT/quiver/benchmark_extraction.py $WS_DIR"
    $VENV $CMD
    echo "Done."
done

cd "$ROOT" || exit

# shut down server
JOB_NO=$(jobs -l | grep -E -o "[0-9]{4,}")
kill $JOB_NO

# create a result JSON according to the specs
# push this JSON to the quiver-back-end repo