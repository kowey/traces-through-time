#!/bin/bash

DZERO=$(dirname "$0")
pushd "$DZERO" > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

source "$SCRIPT_DIR/lib"

TTT_DIR="$SCRIPT_DIR/.."
DATA_DIR="$TTT_DIR/GOLD/latest"

for dataset in $DATASETS; do
    dataset_dir="$DATA_DIR/$dataset"
    bash "$NIMRODEL_DIR/bin/nimrodel-on-dir"\
        -model "$NIMRODEL_MODEL"\
        "$dataset_dir/unannotated"\
        "$dataset_dir/json-$NEW_ROBOT"
done

bash "$SCRIPT_DIR/create-reports.sh"

echo >&2 ""
echo >&2 "Have a look at the reports in $DATA_DIR"
echo >&2 "If you're happy, run $SCRIPT_DIR/mark-latest.sh"
echo >&2 "So that these results will be used as the next baseline"
