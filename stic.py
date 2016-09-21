#!/usr/bin/env python

"""
stic
~~~~

stic is a module to generate a static site to works with Gitlab Pages.
"""

import os
import re
import sys
import imp
import errno
import shutil
import argparse

import SimpleHTTPServer
import SocketServer

from datetime import datetime as dt
from distutils.dir_util import copy_tree

try:
    import markdown
except ImportError, e:
    print e
    print "If you have pip, install it by: pip install markdown"
    sys.exit(1)

try:
    import jinja2
except ImportError, e:
    print e
    print "If you have pip, install it by: pip install jinja2"
    sys.exit(1)

__author__ = "Dhruv Kar"
__version__ = "0.0.1"
__license__ = "MIT"


"""
CONFIGURATION VARIABLES.
"""

EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.nl2br',
    'markdown.extensions.codehilite',
    'markdown.extensions.meta',
    'markdown.extensions.sane_lists',
    'markdown.extensions.smarty',
    'markdown.extensions.toc']


EXTENSION_CONFIGS = {
    'markdown.extensions.codehilite': {
        'linenums': 'True'
    },
    'markdown.extensions.toc': {
        'baselevel': '2',
        'anchorlink': 'False'
    }
}

MARKDOWN_EXTENSIONS = ["md", "mkd", "mkdn", "mdwn", "mdown", "markdown"]
HTML_EXTENSIONS = ["html", "htm"]
JINJA_EXTENSION = ["jinja2", "jinja", "j2"]

BASE_FOLDER = "."
TEMPLATE_FOLDERS = ["templates", "template", "layout", "layouts", "_templates", "_layouts"]
ARTICLE_FOLDERS = ["articles", "article", "blog", "blogs", "notes", "note", "posts", "post"]
ASSETS_FOLDERS = ["static", "assets"]
DEPLOY_FOLDERS = ["public"]

ARTICLE_TEMPLATE = "base.jinja2"

INPUT_DATE_FORMATS = ["%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%y", "%m-%d-%Y", "%m.%d.%y", "%m.%d.%Y"]
OUTPUT_DATE_FORMAT = "%b %d, %Y"

METADATA = {
    'author': '',
    'title': '',
    'date':'',
    'updated':'',
    'tags':'',
    'url':'',
    'description':'',
}


TEST_PORT = 8000

"""
END CONFIGURATION
"""



def _find(filetype, path=BASE_FOLDER):
    """
    Returns all files & path of type specified ("html", "markdown" or "jinja") from all folders and sub-folders.

    """

    _files = []
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            if filetype == "markdown":
                if f.lower().endswith(tuple(MARKDOWN_EXTENSIONS)):
                    _files.append({"path": os.path.join(dirpath, f), "name": f})
            elif filetype == "html":
                if f.lower().endswith(tuple(HTML_EXTENSIONS)):
                    _files.append({"path": os.path.join(dirpath, f), "name": f})
            elif filetype == "jinja":
                if f.lower().endswith(tuple(JINJA_EXTENSIONS)):
                    _files.append({"path": os.path.join(dirpath, f), "name": f})
            else:
                pass 
    return _files


def _check_headers(mdfile):
    """
    Return number of characters and number of headers in a markdown file.
    """
    header_pattern = re.compile("#{1,6}\s")
    with open(mdfile) as f:
        data = f.read()
        no_of_characters = len(data)
        no_of_headers = len(re.findall(header_pattern, data))
    
    return no_of_characters, no_of_headers



def _clean_date(dirty_date, output_format=OUTPUT_DATE_FORMAT):
    for ifmt in INPUT_DATE_FORMATS:
        try:
            clean_date = dt.strptime(dirty_date, ifmt).strftime(output_format)
        except ValueError:
            pass
    
    return clean_date 



def _mkdir_p(path):
    try:
        os.makedirs(path)
        return path
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return path
        else:
            raise


def _folder_structure():
    """
    Returns the actual folders, creates them if they don't exist or lets user know if there's a clash.
    """
    
    possible_folders = {'articles': ARTICLE_FOLDERS, 'templates': TEMPLATE_FOLDERS, 'assets': ASSETS_FOLDERS, 'public': DEPLOY_FOLDERS}
    actual_folders = {}

    for k, v in possible_folders.items():
        h = [x for x in os.listdir(".") if x.lower() in v]
        if len(h) == 1 and os.path.isdir(h[0]):
            actual_folders[k] = h[0]
        elif len(h) == 1 and not os.path.isdir(h[0]):
            print "There is a {0} file in this folder, which is clashing with the {0} folder. Rename/remove this file.".format(k)
        elif len(h) == 0:
            os.mkdir(k)
            actual_folders[k] = k
            print "Created '{0}' folder.".format(k)
        else:
            print "There are multiple files/folders with name {0}. Rename/remove these files/folders.".format(k)
    
    return actual_folders


def _inject(template_file, template_vars):
    """
    inject HTML into Jinja template
    """

    try:
        h = _folder_structure()['templates']

        template_loader = jinja2.FileSystemLoader(searchpath=h)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(template_file)
        output = template.render(template_vars)
        return output
    
    except:
        e = sys.exc_info()[0]
        print e



def _clean_meta_data(md_meta_dict):
    """
    tests for existing metadata, and returns it cleanly.
    """
    new_meta_dict = METADATA

    try:
        new_meta_dict['author'] = md_meta_dict['author'][0].encode('utf-8')
    except KeyError:
        pass 
    
    try:
        new_meta_dict['date'] = _clean_date(md_meta_dict['date'][0])
    except KeyError:
        pass
    
    try:
        new_meta_dict['updated'] = _clean_date(md_meta_dict['updated'][0])
    except KeyError:
        pass

    try:
        new_meta_dict['title'] = md_meta_dict['title'][0].encode('utf-8')
    except KeyError:
        pass
    
    try:
        new_meta_dict['tags'] = ", ".join(md_meta_dict['tags'])
    except KeyError:
        pass
    
    try:
        new_meta_dict['url'] = md_meta_dict['url'][0].encode('utf-8')
    except KeyError:
        pass

    try:
        new_meta_dict['description'] = md_meta_dict['description'][0].encode('utf-8')
    except KeyError:
        pass

    return new_meta_dict


    

def _convert_one_markdown(file_path):
    """
    Convert one markdown to html.
    """

    chars, headers = _check_headers(file_path)
    if chars >= 1000 and headers >= 4:
        EXTENSION_CONFIGS['markdown.extensions.toc']['anchorlink'] = True
    
    output_file = os.path.join(os.path.split(file_path)[0], os.path.splitext(os.path.split(file_path)[1])[0] + ".html")
    md = markdown.Markdown(extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS, output_format="html5")
    
    with open(file_path) as f:
        md_text = f.read()
    
    template_vars = {}
    html = md.reset().convert(md_text)
    try:
        template_vars = _clean_meta_data(md.Meta)
    except AttributeError:
        pass
    template_vars['content'] = html

    injected = _inject(ARTICLE_TEMPLATE, template_vars)
    
    with open(output_file, 'w') as g:
        g.write(injected) 
    return template_vars
    

def convert(filetype="markdown"):
    """
    Converts all markdown files into HTML files in the ARTICLE_FOLDERS.
    """
    
    # Only for markdown files currently.
    files = _find(filetype)
    if filetype == "markdown":
        for f in files:
            x = _convert_one_markdown(f['path']) 
         

def deploy_articles():
    """
    Deploy articles with appropriate folder structure.
    """
    folders = _folder_structure()
    articles_folder = folders['articles']
    md_files = _find("html", articles_folder) 
    public_folder = folders['public']
    
    new_paths = []
    for f in md_files:
        article_path = _mkdir_p(os.path.join(public_folder, os.path.splitext(f['name'])[0]))
        dest = os.path.join(article_path, "index.html")
        print dest
        new_paths.append(dest)
        shutil.move(f['path'], dest)
    
    return new_paths


def deploy_assets():
    """
    Copy static assets and copy to deploy to public folder.
    """
    assets_folder = _folder_structure()['assets']
    public_folder = _folder_structure()['public']

    dest = os.path.join(public_folder, assets_folder)

    try:
        x = copy_tree(assets_folder, dest)
        return x
    except:
        e = sys.exc_info()[0]
        print e

#TODO method to deploy all other pages.
def deploy_pages():
    pass
    

def testserve(port=TEST_PORT):
    """
    Serves up the 'public' directory if it exists. Should be the same as what you'd see once live."
    """
 
    if not os.path.exists("public"):
        print "A 'public' directory does not exist. If you haven't deployed, try that before testing."
    else:
        pwd = os.getcwd()
        try:
            os.chdir("public") 
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer(("", port), handler)
            print "Check out your site at http://localhost:{0}".format(port)
            httpd.serve_forever()
        except:
            raise
        finally:
            os.chdir(pwd)

def main(testserver, verbose=False):
    """
    Converts, injects and deploys relevant files.
    """
    f = _folder_structure()
    raw_input("Check to see if all folders have been created.")
    convert()
    raw_input("Check to see if HTML files have been created from the markdown files.")
    x = deploy_articles()
    raw_input("Check to see if the new HTML files have been moved to the public folder.")
    y = deploy_assets()
    raw_input("Check to see if assets folder has been copied.")
    if testserver == True:
        testserve()
    else:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Deploy your site and, optionally, test it locally.")
    parser.add_argument("-t", "--test", action="store_true", default=False, 
        dest='testserver', help="start a server to test out site locally")
    parser.add_argument("-v", "--verbose", action="store_true", 
        default=False, dest='verbose', help="display and ask user to verify each step")
    
    args = parser.parse_args()
    main(args.testserver, args.verbose)
