These are mostly auxiliary scripts for converting source data (from some
sort of TEI representation) to text, and for summarising the entity
extraction results.

## Installation

1. Fetch this repository

        git clone --recursive https://github.com/kowey/traces-through-time.git

2. If you forgot to use the `--recursive` flag above, initialise the
   submodules

        git submodule update --init --recursive

3. Set up nimrodel (see nimrodel/README.md)


4. Set up a Python virtual environment:

        virtualenv $HOME/.virtualenvs/ttt
        source $HOME/.virtualenvs/ttt/bin/activate
        pip install -r requirements.txt

Note that when you want to run one of these scripts, you will need
to activate your virtual environment first:

    source $HOME/.virtualenvs/ttt/bin/activate


## Installed Scripts

The following scripts are installed in your virtual environment
when you run the above.

### Input to text (converters)

There is a number of scripts in the converters directory that
will be installed by the setup procedure above, for example:

* state-papers-to-text.py
* fine-rolls-to-text.py
* petitions-to-text.py

These all operate on the same principle: they read some input
directory of files in various formats, and output a similarly
structured directory with mostly plain text files that can be
processed by nimrodel.

Note that in data distributions, you may see the names 'kleanthi' and
'calendar' floating around.  Files with such names should have been
renamed to 'state-papers' and 'fine-rolls' respectively

### Post-processing results (evaluation)

* mk-report.py (needs html package) - note that if you have two
  directories of results, you can pass one in with the '--before'
  flag to get a sort of informal regression report
* print-entities.py - just dump out occurrences from json dir

## One-off scripts

Scripts in these directory were used for various one-off tasks
that we don't think are that repeatable

* annotations-to-json.py - convert manual annotation to json
* fix-json.py
* filter-names.py - narrow done a list of candidate names to those
  that look relatively likely to actually be names


## Annotation campaign notes

These notes are for a short-lived annotation campaign around 2014-11.
We were marking up a small sample of texts for interesting spans

* convert annotations to something comparable with nimrodel (takes text
  with angle brackets, spits out json):

      python annotation/annotations-to-json.py ANNOTATED-DIR HUMAN-JSON-DIR

* see just the refs (takes json, spits out just entities)

      print-entities.py SOME-JSON-DIR SOME-TEXT-DIR

* run nimrodel, save the json output
* generate report/scoring:

      mk-report.py --before HUMAN-JSONDIR NIMRODEL-JSON-DIR REPORT-DIR


## Tips

If you have access to a beefy multicore server, you can use the
parallel-nimrodel-on-dir script to run nimrodel on several inputs
at the same time.

You should group the files into buckets of roughly equal size (choosing
the right number of buckets can be tricky; smaller is probably better,
but not so small that you're wasting time starting nimrodel up
repeatedly)

It may help to have a script like the below that you can run mindlessly.

```bash
#/bin/bash

DATASET=traces-through-time/data/snippet-2014-11-14

rm -f nohup.out
mkdir -p "${DATASET}"/json
nohup nimrodel/bin/parallel-nimrodel-on-dir 8\
        "${DATASET}"/text\
        "${DATASET}"/json &
```

In the above script, we also use the `nohup` command to make it so that
you can log out of the terminal session and check on the progress by
logging back in and looking at the `nohup.out` file from time to time.
You can get a sense of the progress by counting the number of occurences
of "^walking" that file, ie. the number of buckets processed.

## See also

* the [Henry III Fine Rolls][finerolls] project - where some of this
  data comes from

[finerolls]: http://www.finerollshenry3.org.uk/home.html
[datr]: http://www.datr.org.uk
