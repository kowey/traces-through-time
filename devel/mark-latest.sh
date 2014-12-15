#!/bin/bash

# Recreate the reports comparing the latest nimrodel
# results against various reference systems and the
# last nimrodel

DZERO=$(dirname "$0")
pushd "$DZERO" > /dev/null
SCRIPT_DIR=$PWD
cd ..
TTT_DIR=$PWD
popd > /dev/null

DATA_DIR="$TTT_DIR"/GOLD/latest
source "$SCRIPT_DIR/lib"

#bash "$SCRIPT_DIR/create-ttt-gold-tarball.sh"

for dataset in $DATASETS; do
    dataset_dir="$DATA_DIR/$dataset"
    old="$dataset_dir/json-$OLD_ROBOT"
    new="$dataset_dir/json-$NEW_ROBOT"

    if [ ! -e "$new" ]; then
        echo >&2 "There doesn't seem to be any new data."
        echo >&2 "Have you run nimrodel?"
        exit 1
    fi
    rm -rf "$old"
    mv "$new" "$old"
done

mv "$DATA_DIR/unit-tests-${NEW_ROBOT}.txt" "$DATA_DIR/unit-tests-${OLD_ROBOT}.txt"
