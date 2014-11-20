These are mostly auxiliary scripts for converting source data (from some
sort of TEI representation) to text, and for summarising the entity
extraction results.

## Installation

It'd be a good idea to use a virtual environment :

    virtualenv $HOME/.virtualenvs/ttt
    source $HOME/.virtualenvs/bin/activate
    pip install -r requirements.txt

Note that when you want to run one of these scripts, you will need
to activate your virtual environment first:

    source $HOME/.virtualenvs/bin/activate


## Scripts

### Input to text

Note that in data distributions, you may see the names 'kleanthi'
and 'calendar' floating around.  Files with such names should have
been renamed to 'state-papers' and 'fine-rolls' respectively

* state-papers-to-text.py
* fine-rolls-to-text.py
* petitions-to-text.py


### Post-processing results

* mk-report.py (needs html package) - note that if you have two
  directories of results, you can pass one in with the '--before'
  flag to get a sort of informal regression report

### Miscellaneous

* fix-json.py
* filter-names.py - narrow done a list of candidate names to those
  that look relatively likely to actually be names

## See also

* the [Henry III Fine Rolls][finerolls] project - where some of this
  data comes from
* [nimrodel][nimrodel] - our [DATR][datr]/ELF based entity extractor

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


[finerolls]: http://www.finerollshenry3.org.uk/home.html
[nimrodel]: https://github.com/kowey/nimrodel
[datr]: http://www.datr.org.uk
