Scripts for the nimrodel development loop:

## Getting started

1. Create the directory GOLD
2. Extract the most recent ttt-gold-YYYY-MM-DD.tar.bz file in it
   (you should thus have GOLD/ttt-gold-YYYY-MM-DD)
3. Rename that GOLD/ttt-gold-YYYY-MM-DD directory to GOLD/working

## Introduction

As background, we have a small amount of sample manually annotated data
(not distributed with this repository alas), so we work in a sort of
loop:

1. hack on nimrodel a bit (don't forget to git commit)
2. run nimrodel again (./run-nimrodel.sh)

   - this will run nimrodel and save the results in
     working/DATASET/json-nimrodel-new (for a variety of different
     datasets)
   - it will also generate a before and after report comparing the
     results with the reference manual annotations and the latest
     blessed results from nimrodel
3. if satisfied save the latest batch of results (./bless-results.sh)
