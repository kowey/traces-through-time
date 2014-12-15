#!/bin/bash

# Run me if you ever change the annotations

DZERO=$(dirname "$0")
pushd "$DZERO" > /dev/null
SCRIPT_DIR=$PWD
cd ..
TTT_DIR=$PWD
popd > /dev/null

source "$SCRIPT_DIR/lib"
DATA_DIR="$TTT_DIR"/GOLD/latest

for dataset in $DATASETS; do
    dataset_dir="$DATA_DIR/$dataset"
    human_json_dir="$dataset_dir/json-$ANNOTATOR"

    # convert annotations to json
    python "$TTT_DIR/oneoff/annotations-to-json.py"\
        "$dataset_dir/annotations-$ANNOTATOR"\
        "$human_json_dir"

    # convenient entities list
    print-entities.py\
        "$human_json_dir"\
        "$dataset_dir/entities-$ANNOTATOR"
    cat "$dataset_dir/entities-$ANNOTATOR"/*\
        | sort | uniq\
        > "$dataset_dir/entities-${ANNOTATOR}.txt"
done
