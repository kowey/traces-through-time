Scripts for the nimrodel development loop:

## Introduction

As background, we have a small amount of sample manually annotated data
(not distributed with this repository alas), so we work in a sort of
loop:

1. hack on nimrodel a bit
2. run nimrodel again (./run-nimrodel.sh)
3. generate a before and after report comparing results not just with
   the reference annotations but also with the latest saved results from
   nimrodel (done by script above)
4. if satisfied save the latest batch of results (./mark-latest.sh)

## Setting this up

1. Create the directory GOLD
2. Extract the latest ttt-gold-YYYY-MM-DD.tar.bz file in it (you should
   thus have GOLD/ttt-gold-YYYY-MM-DD)
3. Copy or rename that directory to GOLD/latest
4. Edit the `lib` file and set the `NIMRODEL_DIR` accordingly (we assume
   here you have already installed nimrodel)
