#!/bin/bash

ROOT=$PWD
WORKFLOW_DIR="$ROOT"/workflows
OCRD_WORKFLOW_DIR="$WORKFLOW_DIR"/ocrd_workflows
WORKSPACE_DIR="$WORKFLOW_DIR"/workspaces

set -euo pipefail

adjust_workflow_settings() {
    # $1: $WORKFLOW
    # $2: $DIR_NAME
    sed -i "s INPUT_DIR . g" "$1"
    sed -i "s OUTPUT_DIR result g" "$1"
    sed -i "s CURRENT $2 g" "$1"
}

rename_and_move_nextflow_result() {
    # rename NextFlow results in order to properly match them to the workflows
    # $1: $WORKFLOW
    # $2: $DIR_NAME
    WORKFLOW_NAME=$(basename -s .txt.nf "$1")
    rm "$WORKFLOW_DIR"/nf-results/*process_completed.json
    mv "$WORKFLOW_DIR"/nf-results/*_completed.json "$WORKFLOW_DIR"/results/"$2"_"$WORKFLOW_NAME"_completed.json
}

run() {
    # $1: $WORKFLOW
    # $2: $DIR_NAME
    # $3: $WS_DIR
    adjust_workflow_settings "$1" "$2"
    nextflow run "$1" -with-weblog http://127.0.0.1:8000/nextflow/
    rename_and_move_nextflow_result "$1" "$2"
    save_workspaces "$3" "$2" "$1"
}

save_workspaces() {
    # $1: $WS_DIR
    # $2: $DIR_NAME
    # $3: $WORKFLOW
    echo "Zipping workspace $1"
    ocrd zip bag -d $1 -i $1 $1
    WORKFLOW_NAME=$(basename -s .txt.nf "$3")
    mv "$WORKSPACE_DIR"/"$2".zip "$WORKFLOW_DIR"/results/"$2"_"$WORKFLOW_NAME".zip
}

source "$ROOT"/venv/bin/activate

echo "Initialize submodules …"
git -C submodules/quiver-data submodule update --init
git -C submodules/oton submodule update --init

echo "Update quiver-data if necessary …"
git -C submodules/quiver-data pull origin main

echo "Installing OtoN …"
pushd submodules/oton
pip install .
popd
echo "OtoN installation done."

echo "Installing quiver-ocrd"
pip install .
echo "quiver-ocrd installation done."

which quiver-ocrd || {
    echo "quiver-ocrd not installed"
    exit 1
    }
oton || {
    echo "quiver-ocrd not installed"
    exit 1
    }

cd "$ROOT" || exit

# convert a ocrd process workflow to a NextFlow workflow with the OtoN converter
echo "Update OtoN converter if necessary …"
git submodule update --init submodules/oton
git -C submodules/oton checkout -- oton/config.toml
git -C submodules/oton merge origin master

echo "Adjust OtoN settings …"
sed -i "s \$projectDir/ocrd-workspace/ $WORKSPACE_DIR/CURRENT/ g" submodules/oton/oton/config.toml
sed -i "s venv37-ocrd/bin/activate git/ocrd_all/venv/bin/activate g" submodules/oton/oton/config.toml
sed -i 's \\\\$HOME/ocrd_models $ROOT/models g' submodules/oton/oton/config.toml
echo "Done."

cd "$OCRD_WORKFLOW_DIR" || exit

echo "Convert OCR-D workflows to NextFlow …"

mkdir -p "$WORKFLOW_DIR/nf-results"

for FILE in *.txt
do
    oton convert -I $FILE -O $FILE.nf --dockerized
done

# download the necessary models if not available
echo "Download the necessary models if not available"
if [[ ! -f $ROOT/models/ocrd-tesserocr-recognize/Fraktur_GT4HistOCR.traineddata ]]
then
    mkdir -p "$ROOT"/models
    docker run --volume "$ROOT"/models:/usr/local/share/ocrd-resources -- ocrd/all:maximum \
        ocrd resmgr download ocrd-tesserocr-recognize Fraktur_GT4HistOCR.traineddata
fi
if [[ ! -d $ROOT/models/ocrd-calamari-recognize/qurator-gt4histocr-1.0 ]]
then
    mkdir -p "$ROOT"/models
    docker run --volume "$ROOT"/models:/usr/local/share/ocrd-resources -- ocrd/all:maximum ocrd resmgr download ocrd-calamari-recognize qurator-gt4histocr-1.0
fi
if [[ ! -d $ROOT/models/ocrd-calamari-recognize/qurator-gt4histocr-1.0 ]]
then
    mkdir -p "$ROOT"/models
    docker run --volume "$ROOT"/models:/usr/local/share/ocrd-resources -- ocrd/all:maximum ocrd resmgr download ocrd-calamari-recognize qurator-gt4histocr-1.0
fi

# execute this workflow on the existing data (incl. evaluation)
mkdir -p "$WORKSPACE_DIR"/tmp
cd "$WORKSPACE_DIR" || exit

# create workspace for all OCR workflows.
# each workflow has a separate workspace to work with.




echo "Restore OCR-D workspaces from BagIts and create workflow specific workspaces …"
for BAGIT in "$ROOT"/submodules/quiver-data/*.zip
do
    BAGIT_NAME=$(basename -s .ocrd.zip "$BAGIT")
    ocrd zip spill "$BAGIT" -d "$WORKSPACE_DIR"/tmp > "$WORKSPACE_DIR"/log.log
    unzip "$BAGIT" METADATA.yml -d "$WORKSPACE_DIR"/tmp/"$BAGIT_NAME"

    for WORKFLOW in "$OCRD_WORKFLOW_DIR"/*ocr.txt.nf
    do
        WF_NAME=$(basename -s .txt.nf "$WORKFLOW")
        cp -r "$WORKSPACE_DIR"/tmp/"$BAGIT_NAME" "$WORKSPACE_DIR"/tmp/"$BAGIT_NAME"_"$WF_NAME"
        cp "$WORKFLOW" "$WORKSPACE_DIR"/tmp/"$BAGIT_NAME"_"$WF_NAME"/
    done
    rm -r "$WORKSPACE_DIR"/tmp/"$BAGIT_NAME"
done

echo "Clean up intermediate dirs …"
for DIR in "$WORKSPACE_DIR"/tmp/*
do
    DIR_NAME=$(basename "$DIR")
    mv "$DIR" "$WORKSPACE_DIR"/"$DIR_NAME"
    cp "$OCRD_WORKFLOW_DIR"/*eval.txt.nf "$WORKSPACE_DIR"/"$DIR_NAME"
done

rm -rf "$WORKSPACE_DIR"/tmp
rm "$WORKSPACE_DIR"/log.log

# start webserver for evaluation
uvicorn api:app --app-dir "$ROOT"/quiver &

# for all data sets…
for WS_DIR in "$WORKSPACE_DIR"/*
do
    echo "Switching to $WS_DIR."

    DIR_NAME=$(basename $WS_DIR)

    run "$WS_DIR"/*ocr.txt.nf "$DIR_NAME" "$WS_DIR"
    run "$WS_DIR"/*eval.txt.nf "$DIR_NAME" "$WS_DIR"

    # create a result JSON according to the specs          
    echo "Get Benchmark JSON …"
    quiver-ocrd benchmarks-extraction "$WS_DIR" "$WORKFLOW"
    echo "Done."

    # move data to results dir
    mv "$WS_DIR"/*.json "$WORKFLOW_DIR"/results
done

cd "$ROOT" || exit

# shut down server
JOB_NO=$(jobs -l | grep -E -o "[0-9]{4,}")
kill "$JOB_NO"


# summarize JSONs
echo "Summarize JSONs to one file …"
quiver-ocrd summarize-benchmarks
echo "Done."

# clean up
rm -rf "$WORKSPACE_DIR"
rm -rf "$ROOT"/work
rm -rf "$WORKFLOW_DIR"/nf-results
rm "$WORKFLOW_DIR"/results/*.json

## push results to the quiver-back-end repo
git add data/workflows.json
git commit -m "update evaluation results"
