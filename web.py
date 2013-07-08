"""
 Module provides web interface to ongoing semantic web research by Jeremy 
 Nelson

"""
__author__ = "Jeremy Nelson"

from bottle import template, request, route, run, static_file
import datetime
import markdown
import os

PROJECT_ROOT = os.path.split(os.path.abspath(__name__))[0]
# Assumes wiki git repository resides at the same directory level as the
# project
WIKI_ROOT = os.path.join(os.path.split(PROJECT_ROOT)[0],
                         'automatic-bibframe-classification.wiki')
MD_FILENAMES = []
if not os.path.exists(WIKI_ROOT):
    raise ValueError("WIKI ROOT {0} does not exists".format(WIKI_ROOT))
else:
    MD_WALKER = next(os.walk(WIKI_ROOT))
    for filename in MD_WALKER[2]:
        if filename.endswith(".md"):
            MD_FILENAMES.append(filename)

@route("/article/<filename:path>")
def markdown_display(filename):
    "Displays markdown html"
    md_loader = markdown.Markdown()
    raw_html = md_loader.convert(open(os.path.join(WIKI_ROOT, filename),
                                      'rb').read())
    return raw_html

@route("/")
def index():
    record_sets = {}
    
    return template('index', md_files=MD_FILENAMES)

run(host='localhost',
    port=8042,
    reloader=True)
