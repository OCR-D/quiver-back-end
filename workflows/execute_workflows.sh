#!/bin/bash

ROOT=$PWD
WORKFLOW_DIR="$ROOT"/workflows
OCRD_WORKFLOW_DIR="$WORKFLOW_DIR"/ocrd_workflows
WORKSPACE_DIR="$WORKFLOW_DIR"/workspaces

mkdir $WORKSPACE_DIR
mkdir -p "$WORKFLOW_DIR/nf-results"


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

cd "$OCRD_WORKFLOW_DIR" || exit

echo "Convert OCR-D workflows to NextFlow …"

source $ROOT'/venv/bin/activate'

for FILE in *.txt
do
    oton convert -I $FILE -O $FILE.nf --dockerized
done

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
    for WORKFLOW in "$OCRD_WORKFLOW_DIR"/*.nf
    do
        cp "$WORKFLOW" "$WS_DIR"
    done

    DIR_NAME=$(echo $WS_DIR | rev | cut -d'/' -f 2 | rev)

    # … adjust workflow files to corpus and run workflows.
    for WORKFLOW in "$WS_DIR"/*.nf
    do
        sed -i "s INPUT_DIR . g" "$WORKFLOW"
        sed -i "s OUTPUT_DIR result g" "$WORKFLOW"
        sed -i "s CURRENT $DIR_NAME g" "$WORKFLOW"
        nextflow run "$WORKFLOW" -with-weblog http://127.0.0.1:8000/nextflow/

        # package workspace
        echo "Zipping workspace $WS_DIR"
        ocrd zip bag -d $WS_DIR -i $WS_DIR $WS_DIR

        # create a result JSON according to the specs          
        echo "Get Benchmark JSON …"
        VENV=$ROOT'/venv/bin/python'
        CMD="$ROOT/quiver/benchmark_extraction.py $WS_DIR $WORKFLOW"
        $VENV $CMD
        echo "Done."
        for DATA in "$ROOT"/workflows/nf-results/*
        do
            rm -rf "$DATA"
        done
    done

    # move data to results dir
    mv $WS_DIR/*.json "$WORKSPACE_DIR"/../results
    mv "$WORKSPACE_DIR"/*.zip "$WORKSPACE_DIR"/../results
done

cd "$ROOT" || exit

# shut down server
JOB_NO=$(jobs -l | grep -E -o "[0-9]{4,}")
kill $JOB_NO

# clean up
for DATA in "$WORKSPACE_DIR"/*
do
    rm -rf "$DATA"
done

rm -rf "$WORKSPACE_DIR"
rm -rf "$ROOT"/work
rm -rf "$WORKFLOW_DIR"/nf-results

# push results to the quiver-back-end repo
git add workflows/results/*
git commit -m "update evaluation results"
