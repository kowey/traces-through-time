#!/usr/bin/env python

"""
Strip any dateline [no date] elements from a Henry III
fineroll XML file, along metadata and any other boring
elements
"""


from __future__ import print_function
from os import path as fp
import argparse
import codecs
import glob
import os
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


def _empty_out(node):
    """
    Delete all children and text in a node
    """
    for child in node:
        node.remove(child)
    node.text = ''


def _remove_boring_parts(tree):
    """
    Remove unwanted pieces of the input XML tree
    (in place, returns None)
    """
    for node in tree.iter('teiHeader'):
        tree.remove(node)
    for node in tree.iter('note'):
        _empty_out(node)
    for dateline in tree.iter('dateline'):
        text = ''.join(dateline.itertext()).strip()
        if "No date" in text:
            _empty_out(dateline)


def _write_items(tree, oprefix):
    """
    Write out text for individual pieces of the XML tree.
    (nimrodel or opennlp seem to crash and burn on large files,
    so we have to feed it little tiny pieces)
    """
    for node in tree.iter('text'):
        node_id = node.attrib.get("id", "")
        if node_id.startswith("r"):
            continue
        ofilename = "_".join([oprefix, node_id])
        dates = [x.attrib['value'] for x in node.iter('date')]
        body = "\n".join(node.itertext())
        text = "\n\n".join(dates[:1] + [body])
        with codecs.open(ofilename, 'w', 'utf-8') as ofile:
            print(text, file=ofile)


def convert(ifile, odir):
    """
    read XML file, write tweaked XML file
    """
    # Is there a cleaner way to do this?
    parser = ET.XMLParser(encoding='utf-8')
    prefix = fp.splitext(fp.basename(ifile))[0]
    with codecs.open(ifile, 'r', 'utf-8') as fin:
        utext = fin.read().encode('utf-8')
        tree = ET.fromstringlist([utext], parser=parser)
        _remove_boring_parts(tree)
        oprefix = fp.join(odir, prefix)
        if not fp.exists(oprefix):
            os.makedirs(oprefix)
        _write_items(tree, fp.join(oprefix, prefix))
        #ET.ElementTree(tree).write(oprefix + ".xml",
        #                           encoding='utf-8')


def main():
    """
    Read input dir, dump in output dir
    """
    psr = argparse.ArgumentParser(description='TTT converter')
    psr.add_argument('input', metavar='DIR', help='dir with xml files')
    psr.add_argument('output', metavar='DIR', help='output directory')
    args = psr.parse_args()
    for ifile in glob.glob(fp.join(args.input, 'roll*.xml')):
        convert(ifile, args.output)

main()
