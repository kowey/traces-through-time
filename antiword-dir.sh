#!/bin/bash

# convert directory of word documents to docbook-like xml format

if [ $# -ne 2 ]; then
    echo >&2 "Usage: $0 inputdir outputdir"
    exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2

mkdir -p "$OUTPUT_DIR"
for i in "$INPUT_DIR"/*.doc; do
    bname=$(basename "$i" .doc)
    antiword -x db "$i" > "$OUTPUT_DIR"/"$bname.xml"
done
