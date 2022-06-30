#!/bin/bash
# $1 should be 'update' or not set. Use 'update' in case all submodules should be updated.


# get submodules
SM_CONFIG=$(cat submodules/ocrd_all/.gitmodules)

SUBMODULE_NAMES=$(
    for LINE in $SM_CONFIG
    do
        echo $LINE | grep -oE '"(.+?)"' | cut -d'"' -f2
    done
)

CURRENT_DIR=$PWD

#if [ $1 == "update" ]; then
#    echo "Update ocrd_all and submodules."
#    #cd submodules/ocrd_all || exit
#    git submodule update submodules/ocrd_all
#
#    # we save the output of the submodule update and then check, if something in the requirements/
#    # dependencies has changed. we need this information to update our deps.json later.
#    #git submodule foreach --quiet 'bash ../../../submodule_update.sh $name $CURRENT_DIR'
#    cd $CURRENT_DIR || exit
#fi


# get the main OCR-D dependencies which stem from core and that most processors have in common
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
    if [ $NAME != 'tesseract' ] && [ $NAME != 'opencv-python' ]; then
        DIR='/submodules/ocrd_all/'$NAME
        echo "Currently processing " $NAME " ..."
        cd $CURRENT_DIR$DIR || exit
        python -m venv venv
        VENV=$PWD'/venv/bin/python'

        # install pkgs
        if [ -f 'requirements.txt' ]; then
            CMD_INSTALL=$(echo '-m pip install -r requirements.txt .')
            $VENV $CMD_INSTALL
        elif [ -f 'setup.py' ]; then
            CMD_INSTALL=$(echo '-m pip install .')
            $VENV $CMD_INSTALL
        fi

        # get deps and save them to JSON
        CMD_FREZE=$(echo '-m pip freeze -l')
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
                echo -n '"'$PKG'": "'$VER'",' >> $CURRENT_DIR'/deps.json'
            fi
        done
        echo -n '},' >> $CURRENT_DIR'/deps.json'
    fi
done

echo '}' >> $CURRENT_DIR'/deps.json'

cd $CURRENT_DIR || exit

# make JSON valid
sed -i 's/},}/}}/g' deps.json
sed -i 's/,}/}/g' deps.json
