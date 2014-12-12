#!/bin/bash

# Recreate the reports comparing the latest nimrodel
# results against various reference systems and the
# last nimrodel

DZERO=$(dirname "$0")
pushd "$DZERO" > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

TTT_DIR="$SCRIPT_DIR"/..
DATA_DIR="$TTT_DIR"/GOLD/latest
source "$SCRIPT_DIR/lib"

NEW=nimrodel-"$NIMRODEL_MODEL"
OLD=nimrodel-old

for dataset in $DATASETS; do
    dataset_dir="$DATA_DIR/$dataset"
    old="$dataset_dir/json-$OLD"
    new="$dataset_dir/json-$NEW"
    if [ ! -e "$new" ]; then
        echo >&2 "There doesn't seem to be any new data."
        echo >&2 "Have you run nimrodel?"
        exit 1
    fi
    rm -rf "$old"
    cp -R "$new" "$old"
done
