#!/bin/bash

DZERO=$(dirname "$0")
cd "$DZERO"
cd ..
TTT_DIR=$PWD
TTT_BNAME=$(basename "$TTT_DIR")
TODAY=$(date +%Y-%m-%d)

if [ "$#" -eq 0 ]; then
    TAG=$TODAY
elif [ "$#" -eq 1 ]; then
    TAG=$1
else
    echo >&2 "Usage: $0 [tag]"
    exit 1
fi

WHITELIST="\
    README.md\
    converters\
    devel\
    nimrodel\
    oneoff\
    requirements.txt\
    setup.py\
    ttt\
    "

git tag $TAG

# above the ttt directory
cd ..
TARFILE=${TTT_BNAME}-${TAG}.tar
tar cf "${TARFILE}"
for item in $WHITELIST; do
    tar rvf "${TARFILE}"\
        --exclude "*.pyc"\
        --exclude ".git"\
        "${TTT_BNAME}/$item"
done
bzip2 "${TARFILE}"
mv "${TARFILE}.bz2" "${TTT_BNAME}"
