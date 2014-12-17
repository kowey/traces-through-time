#!/bin/bash

DZERO=$(dirname "$0")
pushd "$DZERO" > /dev/null
SCRIPT_DIR=$PWD
cd ..
TTT_DIR=$PWD
popd > /dev/null

source "$SCRIPT_DIR/env"
DATA_DIR="$TTT_DIR/GOLD/working"

bash "$NIMRODEL_DIR/bin/nimrodel" selftest > "$DATA_DIR/unit-tests-${NEW_ROBOT}.txt"

which parallel
if [ $? -eq 0 ]; then
    NIMRODEL_SUBCMD=parallel-dir
    NIMRODEL_ARGS=$JOBS
else
    NIMRODEL_SUBCMD=dir
    NIMRODEL_ARGS=
fi


for dataset in $DATASETS; do
    dataset_dir="$DATA_DIR/$dataset"
    time bash "$NIMRODEL_DIR/bin/nimrodel" "$NIMRODEL_SUBCMD"\
        -model "$NIMRODEL_MODEL"\
        $NIMRODEL_ARGS\
        "$dataset_dir/unannotated"\
        "$dataset_dir/json-$NEW_ROBOT"
done

bash "$SCRIPT_DIR/create-reports.sh"

echo >&2 ""
echo >&2 "Have a look at the reports in $DATA_DIR"
echo >&2 "If you're happy, run $SCRIPT_DIR/bless-results.sh"
echo >&2 "So that these results will be used as the next baseline"
