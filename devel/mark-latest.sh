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

TODAY=$(date +%Y-%m-%d)
pushd "$DATA_DIR/.." > /dev/null
TARBALL_BNAME=ttt-gold-$TODAY
mv latest "$TARBALL_BNAME"
tar cjvf "${TARBALL_BNAME}.tar.bz" "$TARBALL_BNAME"
mv "$TARBALL_BNAME" latest
popd > /dev/null

mv "$DATA_DIR/unit-tests-${NEW_ROBOT}.txt" "$DATA_DIR/unit-tests-${OLD_ROBOT}.txt"

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
    cp -R "$new" "$old"
done

