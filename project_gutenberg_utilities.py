"""
 Project Gutenberg RDF Utilities

"""
__author__ = "Jeremy Nelson"
import datetime
import json
import pymarc
import os
import random
import shutil
import sys
from rdflib import RDF, RDFS
from rdflib import Namespace

DCTERMS = Namespace("http://purl.org/dc/terms/")
PGTERMS = Namespace("http://www.gutenberg.org/2009/pgterms/")

DATA_ROOT = os.path.split(os.getcwd())[0]      

def GeneratePGRDFSets(max_recs=42379):
    """Function generates Project Gutenberg Random testing and training sets


    Keywords:
    max_recs -- Number of RDF records in the epub directory
    """
    pg_root = os.path.join(DATA_ROOT, 
                           "ProjectGutenberg",
                           "epub")
    results = next(os.walk(pg_root))
    counter = 0
    rdf_dirs = results[1]
    for dirname in rdf_dirs:
        src_path = os.path.join(pg_root, dirname)
        item_results = next(os.walk(src_path))
        if len(item_results[2]) == 1:
            src_filename = item_results[2][0] 
        else:
            continue 
        if random.random() >= .5:
            shutil.copy(os.path.join(src_path, 
                                     src_filename),
                        os.path.join("ProjectGutenberg",
                                     "training",
                                     src_filename))
        else:
            shutil.copy(os.path.join(src_path, 
                                     src_filename),
                        os.path.join("ProjectGutenberg",
                                     "testing",
                                     src_filename))
