#!/bin/bash
# $1 MUST be 'init' or 'update'.


# get submodules
SM_CONFIG=$(cat submodules/ocrd_all/.gitmodules)

SUBMODULE_NAMES=$(
    for LINE in $SM_CONFIG
    do
        echo $LINE | grep -oE '"(.+?)"' | cut -d'"' -f2
    done
)

CURRENT_DIR=$PWD

# get the main OCR-D dependencies which stem from core and that most processors have in common.
cd 'submodules/ocrd_all/core' || exit
python -m venv venv
VENV=$PWD'/venv/bin/python'
CMD='-m pip install ocrd'
$VENV $CMD
CMD='-m pip freeze -l'
$VENV $CMD > $CURRENT_DIR'/core_deps.txt'
cd $CURRENT_DIR || exit

echo '{' >> $CURRENT_DIR'/deps.json'

for NAME in $SUBMODULE_NAMES
do
    case $NAME in
    tesseract|opencv-python|ocrd_ocropy) echo "skip $NAME";;
    *)
        DIR='/submodules/ocrd_all/'$NAME
        echo "Currently processing " $NAME " ..."
        cd $CURRENT_DIR$DIR || exit
        python3 -m venv venv
        VENV=$PWD'/venv/bin/python'

        # install pkgs
        if [ -f 'setup.py' ]; then
            CMD_INSTALL='-m pip install .'
            $VENV $CMD_INSTALL
        fi

        # get deps and save them to JSON
        CMD_FREZE='-m pip freeze -l'
        echo '"'$NAME'": {' >> $CURRENT_DIR'/deps.json'
        RESULT=$($VENV $CMD_FREZE)
        for RES in $RESULT
        do
            # check if dependency also occurs in core_deps.txt
            IS_CORE_DEP="false"
            for LINE in $(cat $CURRENT_DIR/core_deps.txt)
            do
                if [ $RES == $LINE ]; then
                    IS_CORE_DEP="true"
                fi
            done

            if [ $IS_CORE_DEP == "false" ]; then
                PKG=$(echo $RES | cut -d'=' -f1)
                VER=$(echo $RES | cut -d'=' -f3)

                # in each venv the project itself is also installed.
                # since it's not a dependency, we omit it.
                PKG_NORMALIZED=$(echo "$PKG" | sed -e 's/-/_/g')
                STARTS_WITH_FILE=$(echo "$PKG" | grep -E '^file')
                IS_AT=$(echo "$PKG" | grep -E '@')
                if [ $PKG_NORMALIZED != $NAME ] && [ ! $IS_AT ] && [ ! $STARTS_WITH_FILE ]; then
                    echo -n '"'$PKG'": "'$VER'",' >> $CURRENT_DIR'/deps.json'
                fi
            fi
        done
        echo -n '},' >> $CURRENT_DIR'/deps.json'
    esac
done

echo '}' >> $CURRENT_DIR'/deps.json'

cd $CURRENT_DIR || exit

# make JSON valid
sed -i 's/},}/}}/g' deps.json
sed -i 's/,}/}/g' deps.json