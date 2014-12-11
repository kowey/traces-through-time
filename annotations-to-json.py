#!/usr/bin/env python
# pylint: disable=invalid-name
# (invalid module name ok because script)
# pylint: enable=invalid-name

"""
Given a directory of annotated texts (where interesting
text spans are surrounded by <>), generate a json file
for each text in the style of nimrodel
"""


from __future__ import print_function
from os import path as fp
import codecs
import json
import re

from ttt.cli import CliConfig, iodir_argparser, generic_main


_BRACKET_RE = re.compile(r'men')


def mk_converter(input_format):
    """
    Return a function which given input and output dirs,
    and a subpath within the input dir, read annotations,
    and save as json records with just an 'origOccurrence'
    member ::


        InputFormat -> (FilePath, FilePath, FilePath)
                    -> IO ()
    """
    person_re = re.compile(r'<Person>(.*?)</Person>'
                           if input_format == 'gate' else
                           r'<(.*?)>')
    def inner(input_dir, output_dir, subpath):
        """
        ::

            (FilePath, FilePath, FilePath) -> IO ()
        """
        ifilename = fp.join(input_dir, subpath)
        ofilename = fp.join(output_dir, subpath)
        with codecs.open(ifilename, 'r', 'utf-8') as istream:
            txt = istream.read()
            matches = person_re.findall(txt)
            jdicts = [{'origOccurrence': x} for x in matches]
            with open(ofilename, 'wb') as ostream:
                json.dump(jdicts, ostream)
    return inner


def main():
    "read cli args, loop on dir"
    cfg = CliConfig(description='annotations converter',
                    input_description='annotated text files',
                    glob='*')
    psr = iodir_argparser(cfg)
    psr.add_argument('--format', choices=['human', 'gate'],
                     default='human',
                     help='input markup format')
    args = psr.parse_args()
    generic_main(cfg, mk_converter(args.format), args)

if __name__ == '__main__':
    main()
