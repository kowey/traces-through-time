"""
Helper functions for command-line tools
"""

# author: Eric Kow
# license: Public domain

from collections import namedtuple
from os import path as fp
import argparse
import glob
import os


class CliConfig(namedtuple('CliConfig',
                           ['description',
                            'input_description',
                            'glob'])):
    """
    Configuration for `generic_main`

    :param description: description for the program
    :param input_description: nature of the input files
    :param glob: glob to match on input dir files
    """


def iodir_argparser(cfg):
    """
    A CLI argument parser for a simple program that takes an input
    and output directory
    """
    psr = argparse.ArgumentParser(description=cfg.description)
    psr.add_argument('input', metavar='DIR',
                     help='dir with ' + cfg.input_description)
    psr.add_argument('output', metavar='DIR',
                     help='output directory')
    return psr


def generic_main(cfg, on_file, args):
    """
    A general purpose 'main' function that captures a pattern in the
    CLI scripts we write here.

    Given a glob expression (which files to iterate on, eg. '*.txt') and
    worker function, read all matching files in the input dir and run
    the worker on them. ::

        type Worker = (FilePath, FilePath, FilePath)
                    -- input dir
                    -- output dir
                    -- subpath
                   -> IO ()

        (CliConfig, Worker, argparser.Namespace) -> IO ()
    """
    if not fp.exists(args.output):
        os.makedirs(args.output)
    for filename in glob.glob(fp.join(args.input, cfg.glob)):
        subpath = fp.basename(filename)
        on_file(args.input, args.output, subpath)
