#!/bin/bash

DZERO=$(dirname "$0")
pushd "$DZERO" > /dev/null
SCRIPT_DIR=$PWD
cd ..
TTT_DIR=$PWD
popd > /dev/null

DATA_DIR="$TTT_DIR/GOLD/latest"
source "$SCRIPT_DIR/lib"

bash "$NIMRODEL_DIR/bin/nimrodel" selftest > "$DATA_DIR/unit-tests-${NEW_ROBOT}.txt"

for dataset in $DATASETS; do
    dataset_dir="$DATA_DIR/$dataset"
    time bash "$NIMRODEL_DIR/bin/nimrodel" dir\
        -model "$NIMRODEL_MODEL"\
        "$dataset_dir/unannotated"\
        "$dataset_dir/json-$NEW_ROBOT"
done

bash "$SCRIPT_DIR/create-reports.sh"

echo >&2 ""
echo >&2 "Have a look at the reports in $DATA_DIR"
echo >&2 "If you're happy, run $SCRIPT_DIR/mark-latest.sh"
echo >&2 "So that these results will be used as the next baseline"
