#!/bin/bash

# Recreate the reports comparing the latest nimrodel
# results against various reference systems and the
# last nimrodel

set -e
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
rm -rf "$TARBALL_BNAME"
mv latest "$TARBALL_BNAME"
tar cjvf "${TARBALL_BNAME}.tar.bz" "$TARBALL_BNAME"
mv "$TARBALL_BNAME" latest
popd > /dev/null
