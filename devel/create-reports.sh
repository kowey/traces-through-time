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

source "$SCRIPT_DIR/env"
DATA_DIR="$TTT_DIR"/GOLD/working

mk_report () {
    dataset=$1
    before=$2
    after=$3
    dataset_dir="$DATA_DIR/$dataset"
    mk-report.py\
        --before "$dataset_dir/json-$before"\
        "$dataset_dir/json-$after"\
        "$dataset_dir/report-$before-v-$after"
}


for dataset in $DATASETS; do
    # compare all ref systems (eg. gate) against the human
    for ref in $REF_SYSTEMS $OLD_ROBOT; do
        if [ "$ref" != "$ANNOTATOR" ]; then
            mk_report "$dataset" "$ANNOTATOR" "$ref"
        fi
    done

    # compare all robots against all ref systems
    for robot in $ROBOTS; do
        for ref in $REF_SYSTEMS; do
            mk_report "$dataset" "$ref" "$robot"
        done
    done

    # compare new robot against the old robot
    mk_report "$dataset" "$OLD_ROBOT" "$NEW_ROBOT"
done
