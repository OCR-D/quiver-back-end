#!/bin/bash

if [ -f '$2/update_tmp.txt' ]; then
    rm $2/update_tmp.txt
fi

if [ -f 'setup.py' ]; then
    echo $1 >> $2/update_tmp.txt
    md5sum setup.py >> $2/update_tmp.txt
    echo "\n" >> $2/update_tmp.txt
fi