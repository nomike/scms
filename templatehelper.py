"""
Contains helper functions to be used within templates.
All functions and imports defined in here, are accessible from within Jinja2 templates.

Example:

    {% for parentpath, parentname in templatehelper.getparents(path) %}
    <a class="powerline__component" href="{{ parentpath }}"><i class="fas fa-folder"></i> {{ parentname }}</a>
    {% endfor %}
"""

import os
import re
import mimetypes
import fnmatch
from datetime import datetime, tzinfo, timezone
import yaml
import markdown
import urllib
import json

config = None
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)


# paths sent by flask are relative to the "public" directory. This prefix should be added to get paths relative to the pages root directory.
#TODO: This is a redundant specification and should be avoided.
pathprefix = 'public'

# List of official MIME Types: http://www.iana.org/assignments/media-types/media-types.xhtml
# If you want additional mimetypes to be covered, add them to this list.
# The types map to FontAwesome identifiers. Check out https://fontawesome.com/icons?d=gallery for a list of available images.
mimetype_fas_mapping = {
# Media
'image': 'fa-file-image',
'audio': 'fa-file-audio',
'video': 'fa-file-video',
# Documents
'application/pdf': 'fa-file-pdf',
'application/msword': 'fa-file-word',
'application/vnd.ms-word': 'fa-file-word',
'application/vnd.oasis.opendocument.text': 'fa-file-word',
'application/vnd.openxmlformatsfficedocument.wordprocessingml': 'fa-file-word',
'application/vnd.ms-excel': 'fa-file-excel',
'application/vnd.openxmlformatsfficedocument.spreadsheetml': 'fa-file-excel',
'application/vnd.oasis.opendocument.spreadsheet': 'fa-file-excel',
'application/vnd.ms-powerpoint': 'fa-file-powerpoint',
'application/vnd.openxmlformatsfficedocument.presentationml': 'fa-file-powerpoint',
'application/vnd.oasis.opendocument.presentation': 'fa-file-powerpoint',
'text/plain': 'fa-file-text',
'text/html': 'fa-file-code',
'application/json': 'fa-file-code',
# Archives
'application/gzip': 'fa-file-archive',
'application/zip': 'fa-file-archive',
}

def listdir(path):
    """
    List all child-elements of the specified path.
    Hidden files and, files ending in ".scmsfasicon" and files ending with a "~" are ignored.

    You can also ignore additional files by creating a file called ".scmsignore" in the current folder.
    All files listed in there will not be listed.

    If a file named "index" is present, it is supposed to be rendered as the main content of the page
    and thus it will be ommited from the list as well.
    """
    ignorelist = ['index', 'index.md', '*.scmsfasicon', '*.scmstarget']
    if os.path.exists(os.path.join(pathprefix, path, '.scmsignore')):
        with open(os.path.join(pathprefix, path, '.scmsignore')) as file:
            ignorelist.extend([line.strip('\n') for line in file.readlines()])
    dirlist = [os.path.basename(f) for f in os.listdir(os.path.join(pathprefix, path)) if re.match(r'^^[^\.].*[^~]$', f) and not f in ignorelist]
    removeitems = []
    for dir in dirlist:
        for ignore in ignorelist:
            if fnmatch.fnmatch(dir, ignore):
                removeitems.append(dir)
    for removeitem in removeitems:
        dirlist.remove(removeitem)
    dirlist.sort()
    return dirlist

def listchildren(path):
    """
    List all child-elements of the specified path.
    Hidden files and, files ending in ".scmsfasicon" and files ending with a "~" are ignored.

    You can also ignore additional files by creating a file called ".scmsignore" in the current folder.
    All files listed in there will not be listed.

    If a file named "index" is present, it is supposed to be rendered as the main content of the page
    and thus it will be ommited from the list as well.
    """
    ignorelist = ['index', '*.scmsfasicon', '*.scmstarget']
    if os.path.exists(os.path.join(pathprefix, path, '.scmsignore')):
        with open(os.path.join(pathprefix, path, '.scmsignore')) as file:
            ignorelist.extend([line.strip('\n') for line in file.readlines()])
    dirlist = [[os.path.basename(f), os.path.basename(f)] for f in os.listdir(os.path.join(pathprefix, path)) if re.match(r'^^[^\.].*[^~]$', f) and not f in ignorelist]
    if os.path.exists(os.path.join(pathprefix, path, '.scmslinks')):
        with open(os.path.join(pathprefix, path, '.scmslinks')) as file:
            additional_links = json.load(file)
        dirlist.extend(additional_links)
    removeitems = []
    for dir in [item[0] for item in dirlist]:
        for ignore in ignorelist:
            if fnmatch.fnmatch(dir, ignore):
                removeitems.append(dir)
    dirlist = [item for item in dirlist if item[0] not in removeitems]
    dirlist.sort()
    return dirlist


def getparents(path):
    """
    Return a list of tupels with all parent elements.
    Tupels have the format
    (path, basename)
        path: the full path relative to the "public" folder, leading to the parent, including the basename
        basename: only the basename of the parent
    """
    pathelements = path.split(os.path.sep)[:-1]
    parents = []
    i = 0
    for i in range(0, len(pathelements)):
        parents.append(('/' + '/'.join(pathelements[:i+1]), pathelements[i]))
    return parents

def readfile(path, default=None):
    """
    Read a file into a bytestring and return it's content.
    """
    if not os.path.exists(path) and default:
        return default
    with open(path, 'r') as file:
        return file.read()

def getfasicon(path):
    """
    Check if a file named basename(path) + '.scmfasicon' exists, and return it's content.
    If not, handover to getfastype(path)
    """
    if os.path.isfile(os.path.join(pathprefix, path) + '.scmsfasicon'):
        return readfile(os.path.join(pathprefix, path) + '.scmsfasicon')
    else:
        return getfastype(path)

def getfastype(path):
    """
    If path refers to a folder, return an appropriate fonteawesome icon.
    If not, determine the mimetype of the file and return an apropriate icon.
    If there is no defintion for the specific mime-type, try with the category
    (the part of the mime-type before the slash).
    If this fails as well, fallback to a default.
    """
    if os.path.isdir(os.path.join(pathprefix, path)):
        return "fa-folder"

    mimetype = mimetypes.guess_type(path)[0]
    if not mimetype == None:
        if mimetype in mimetype_fas_mapping:
            return mimetype_fas_mapping[mimetype]
        if mimetype.split('/')[0] in mimetype_fas_mapping:
            return mimetype_fas_mapping[mimetype.split('/')[0]]
    return 'fa-file'

def getlastmodifiedfile(path):
    assert(os.path.isdir(path))
    newest = {"file": path, "timestamp": os.path.getmtime(path)}
    for root, dirs, files in os.walk(path):
        for path in dirs:
            timestamp = os.path.getmtime(os.path.join(root, path))
            if timestamp > newest['timestamp']:
                newest['file'] = os.path.join(root, path)
                newest['timestamp'] = timestamp
        for path in files:
            timestamp = os.path.getmtime(os.path.join(root, path))
            if timestamp > newest['timestamp']:
                newest['file'] = os.path.join(root, path)
                newest['timestamp'] = timestamp
    return newest
