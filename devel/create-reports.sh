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
    dataset_dir="$DATA_DIR/$dataset"
    new="$dataset_dir/json-$NEW_ROBOT"
    if [ ! -e "$new" ]; then
        echo >&2 "There doesn't seem to be any new data."
        echo >&2 "Have you run nimrodel?"
        exit 1
    fi
 
    for sys in $REF_SYSTEMS $ROBOTS; do
        # convenient entities list
        print-entities.py\
            "$dataset_dir/json-$sys"\
            "$dataset_dir/entities-$sys"
        cat "$dataset_dir/entities-$sys"/*\
            | sort | uniq\
            > "$dataset_dir/entities-$sys.txt"
    done

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
