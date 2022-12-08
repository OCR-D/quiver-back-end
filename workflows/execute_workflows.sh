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
    WORKFLOW_NAME=$(basename -s .txt.nf "$1")
    mv "$WORKSPACE_DIR"/"$2".zip "$WORKFLOW_DIR"/results/"$2"_"$WORKFLOW_NAME".zip
}

source "$ROOT"/venv/bin/activate

echo "Initialize submodules …"
git -C submodules/quiver-data submodule update --init
git -C submodules/oton submodule update --init

# update the data from quiver-data repository if necessary
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

quiver-ocrd || { echo "quiver-ocrd not installed"; exit 1 }
oton || { echo "quiver-ocrd not installed"; exit 1 }

echo "Restore OCR-D workspaces from BagIts …"
for BAGIT in submodules/quiver-data/*.zip
do
    ocrd zip spill "$BAGIT" -d "$WORKSPACE_DIR" > log.log
done
echo "BagIt extraction completed."

cd "$ROOT" || exit

# convert a ocrd process workflow to a NextFlow workflow with the OtoN converter
echo "Update OtoN converter if necessary …"
git submodule update --init submodules/oton
git -C submodules/oton checkout -- oton/config.toml
git -C submodules/oton merge origin master

echo "Adjust OtoN settings …"
sed -i "s \$projectDir/ocrd-workspace/ $WORKSPACE_DIR/CURRENT/ g" submodules/oton/oton/config.toml
sed -i "s venv37-ocrd/bin/activate git/ocrd_all/venv/bin/activate g" submodules/oton/oton/config.toml
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

# execute this workflow on the existing data (incl. evaluation)

cd "$WORKSPACE_DIR" || exit

# create workspace for all OCR workflows.
# each workflow has a separate workspace to work with.
mkdir -p "$WORKSPACE_DIR"/tmp
for WORKFLOW in "$OCRD_WORKFLOW_DIR"/*ocr.txt.nf
do
    WF_NAME=$(echo "$WORKFLOW" | cut -d'.' -f 1 | rev | cut -d'/' -f 1 | rev)
    echo "Restore OCR-D workspaces from BagIts …"
    for BAGIT in "$ROOT"/submodules/quiver-data/*.zip
    do
        BAGIT_NAME=$(echo "$BAGIT" | rev | cut -d'/' -f 1 | rev | cut -d'.' -f 1)
        ocrd zip spill "$BAGIT" -d "$WORKSPACE_DIR"/tmp > "$WORKSPACE_DIR"/log.log
        unzip "$BAGIT" METADATA.yml -d "$WORKSPACE_DIR"/tmp/"$BAGIT_NAME"
        # this is a workaround for a werid behaviour where 16_ant_complex.ocrd.zip is sometimes not
        # correctly extracted (unknown reason)
        if [ "$BAGIT" = "$ROOT"/submodules/quiver-data/16_ant_complex.ocrd.zip ]
        then
            mkdir "$WORKSPACE_DIR"/tmp/16_ant_complex
            mv "$WORKSPACE_DIR"/tmp/OCR-D* "$WORKSPACE_DIR"/tmp/16_ant_complex
            mv "$WORKSPACE_DIR"/tmp/mets.xml "$WORKSPACE_DIR"/tmp/16_ant_complex
            mv "$WORKSPACE_DIR"/tmp/log.log "$WORKSPACE_DIR"/tmp/16_ant_complex
        fi
    done
    for WS_DIR in "$WORKSPACE_DIR"/tmp/*
    do
        cp "$WORKFLOW" "$WS_DIR"
        cp "$OCRD_WORKFLOW_DIR"/*eval.txt.nf "$WS_DIR"
        mv "$WS_DIR" "$WS_DIR"_"$WF_NAME"
        cp -r "$WS_DIR"_"$WF_NAME" "$WORKSPACE_DIR"
    done
    echo "BagIt extraction completed."
    rm -rf "$WORKSPACE_DIR"/tmp
done

# start webserver for evaluation
uvicorn api:app --app-dir "$ROOT"/quiver &

# for all data sets…
for WS_DIR in "$WORKSPACE_DIR"/*/
do
    echo "Switching to $WS_DIR."
    # … copy all workflows in the right place …
    for WORKFLOW in "$OCRD_WORKFLOW_DIR"/*.nf
    do
        cp "$WORKFLOW" "$WS_DIR"
    done

    DIR_NAME=$(basename $WS_DIR)

    # … execute workflow …
    run "$WS_DIR"/*ocr.txt.nf "$DIR_NAME" "$WS_DIR"
    # … perform evaluation …
    run "$WS_DIR"/*eval.txt.nf "$DIR_NAME" "$WS_DIR"
    # … and extract relevant metrics

    # create a result JSON according to the specs          
    echo "Get Benchmark JSON …"
    quiver-ocrd benchmarks-extraction "$WS_DIR" "$WORKFLOW"
    echo "Done."

    # move data to results dir
    mv $WS_DIR/*.json "$WORKFLOW_DIR"/results
done

cd "$ROOT" || exit

# shut down server
JOB_NO=$(jobs -l | grep -E -o "[0-9]{4,}")
kill $JOB_NO


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
