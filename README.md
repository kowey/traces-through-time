These are mostly auxiliary scripts for converting source data (from some
sort of TEI representation) to text, and for summarising the entity
extraction results.

## Scripts

### Input to text

* table-to-text.py
* fine-rolls-to-text.py

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

[finerolls]: http://www.finerollshenry3.org.uk/home.html
[nimrodel]: https://github.com/kowey/nimrodel
[datr]: http://www.datr.org.uk
