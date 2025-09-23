"""
Contains helper functions to be used within templates.
All functions and imports defined in here, are accessible from within Jinja2 templates.

Example:

    {% for parentpath, parentname in templatehelper.getparents(path) %}
    <a class="powerline__component" href="{{ parentpath }}">
        <i class="fas fa-folder"></i> {{ parentname }}
    </a>
    {% endfor %}
"""

import fnmatch
import hashlib
import json
import locale
import mimetypes
import os
import pickle
# pylint: disable=unused-import
import re
# pylint: disable=unused-import
import urllib
from datetime import datetime, timezone, tzinfo

# pylint: disable=unused-import
import markdown
# pylint: disable=unused-import
import orgpython
import regex
import yaml

try:
    import anthropic
except ImportError:
    anthropic = None

# pylint: disable=invalid-name
config = None

with open("../config.yaml", encoding=locale.getpreferredencoding()) as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)


# paths sent by flask are relative to the "public" directory. This prefix should be added to get
# paths relative to the pages root directory.
# pylint: disable=invalid-name
pathprefix = ''

def get_cache_dir():
    """Get the cache directory from config or use default."""
    if config and 'claude' in config and 'cache_dir' in config['claude']:
        return config['claude']['cache_dir']
    return os.path.join('.', 'cache', 'translations')

def ensure_cache_dir():
    """Ensure the cache directory exists."""
    cache_dir = get_cache_dir()
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

def get_cache_key(content_hash, target_lang):
    """Generate a cache key from content hash and target language."""
    return f"{content_hash}_{target_lang}.pkl"

def get_cached_translation(content_hash, target_lang):
    """Retrieve a translation from cache if it exists."""
    ensure_cache_dir()
    cache_dir = get_cache_dir()
    cache_file = os.path.join(cache_dir, get_cache_key(content_hash, target_lang))
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except (IOError, pickle.PickleError):
            pass
    return None

def cache_translation(content_hash, target_lang, translation):
    """Store a translation in cache."""
    ensure_cache_dir()
    cache_dir = get_cache_dir()
    cache_file = os.path.join(cache_dir, get_cache_key(content_hash, target_lang))
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(translation, f)
    except (IOError, pickle.PickleError):
        pass

def translate_claude(content, target_lang):
    """
    Translate content using Claude API.
    """
    if not anthropic:
        raise ImportError(
            "anthropic package not installed. Please install with: pip install anthropic"
        )

    if not config or 'claude' not in config:
        raise ValueError("Claude configuration not found in config.yaml")

    claude_config = config['claude']
    api_key = claude_config.get('api_key')
    if not api_key or api_key == "your_anthropic_api_key_here":
        raise ValueError("Valid Claude API key not configured")

    client = anthropic.Anthropic(
        api_key=api_key,
        base_url=claude_config.get('base_url', 'https://api.anthropic.com')
    )

    # Language code to language name mapping (ISO 639-3)
    lang_names = {
        'deu': 'German', 'fra': 'French', 'ita': 'Italian', 'ell': 'Greek',
        'hun': 'Hungarian', 'por': 'Portuguese', 'ces': 'Czech', 'slk': 'Slovak',
        'slv': 'Slovenian', 'hrv': 'Croatian', 'gsw': 'Swiss German',
        'nld': 'Dutch', 'bul': 'Bulgarian', 'mnk': 'Mandinka',
        'jpn': 'Japanese', 'rus': 'Russian', 'gla': 'Scottish Gaelic'
    }

    target_language = lang_names.get(target_lang, target_lang)

    try:
        message = client.messages.create(
            model=claude_config.get('model', 'claude-3-5-sonnet-20241022'),
            max_tokens=claude_config.get('max_tokens', 4096),
            temperature=claude_config.get('temperature', 0.7),
            system=claude_config.get(
                'system_prompt', 'You translate org-mode, markdown and HTML '
                'documents from english to other languages. You maintain the '
                'original formatting and tone. You only translate the text, not '
                'the code blocks or HTML tags. You do not add any additional '
                'text, except for a note at the top that this text has been '
                'translated by an AI. If you do not know the target language, '
                'you simply return the original text. You output only the '
                'resulting text, nothing else.'
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Translate this webpage content from English to {target_language}:\n\n"
                    + content
                )
            }]
        )
        return message.content[0].text
    except Exception as e:
        raise RuntimeError(f"Translation failed: {str(e)}") from e

def get_content_hash(content):
    """Generate SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def is_claude_available():
    """Check if Claude translation is available and properly configured."""
    if not anthropic:
        return False

    if not config or 'claude' not in config:
        return False

    claude_config = config['claude']
    api_key = claude_config.get('api_key')

    return api_key and api_key != "your_anthropic_api_key_here"

# List of official MIME Types: http://www.iana.org/assignments/media-types/media-types.xhtml
# If you want additional mimetypes to be covered, add them to this list.
# The types map to FontAwesome identifiers. Check out https://fontawesome.com/icons?d=gallery
# for a list of available images.
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

    You can also ignore additional files by creating a file called ".scmsignore" in the current
    folder.
    All files listed in there will not be listed.

    If a file named "index" is present, it is supposed to be rendered as the main content of the
    page and thus it will be ommited from the list as well.
    """
    ignorelist = ['index', 'index.html', 'index.md', 'index.org', '*.scmsfasicon', '*.scmstarget']
    if os.path.exists(os.path.join(pathprefix, path, '.scmsignore')):
        with open(
                os.path.join(pathprefix, path, '.scmsignore'),
                encoding=locale.getpreferredencoding()) as scsmignore:
            ignorelist.extend([line.strip('\n') for line in scsmignore.readlines()])
    dirlist = [
            os.path.basename(f)
            for f in os.listdir(os.path.join(pathprefix, path))
            if regex.match('^(?!\\.).*(?<!~)$', f) and not f in ignorelist
        ]
    removeitems = []
    for directory in dirlist:
        for ignore in ignorelist:
            if fnmatch.fnmatch(directory, ignore):
                removeitems.append(directory)
    for removeitem in removeitems:
        dirlist.remove(removeitem)
    dirlist.sort()
    return dirlist

def listchildren(path):
    """
    List all child-elements of the specified path.
    Hidden files and, files ending in ".scmsfasicon" and files ending with a "~" are ignored.

    You can also ignore additional files by creating a file called ".scmsignore" in the current
    folder.
    All files listed in there will not be listed.

    If a file named "index" is present, it is supposed to be rendered as the main content of the
    page and thus it will be ommited from the list as well.
    """
    ignorelist = ['index', 'index.html', 'index.md', 'index.org', '*.scmsfasicon', '*.scmstarget']
    if os.path.exists(os.path.join(pathprefix, path, '.scmsignore')):
        with open(
                os.path.join(pathprefix, path, '.scmsignore'),
                encoding=locale.getpreferredencoding()) as scmsignore:
            ignorelist.extend([line.strip('\n') for line in scmsignore.readlines()])
    dirlist = [
            [os.path.basename(f), os.path.basename(f)]
            for f in os.listdir(os.path.join(pathprefix, path))
            if regex.match('^(?!\\.).*(?<!~)$', f) and not f in ignorelist
        ]
    if os.path.exists(os.path.join(pathprefix, path, '.scmslinks')):
        with open(
                os.path.join(pathprefix, path, '.scmslinks'),
                encoding=locale.getpreferredencoding()) as scmslinks:
            additional_links = json.load(scmslinks)
        dirlist.extend(additional_links)
    removeitems = []
    for directory in [item[0] for item in dirlist]:
        for ignore in ignorelist:
            if fnmatch.fnmatch(directory, ignore):
                removeitems.append(directory)
    dirlist = [item for item in dirlist if item[0] not in removeitems]
    dirlist.sort()
    return dirlist


def getparents(path):
    """
    Return a list of tupels with all parent elements.
    Tupels have the format
    (path, basename)
        path: the full path relative to the "public" folder, leading to the parent, including the
            basename
        basename: only the basename of the parent
    """
    pathelements = path.split(os.path.sep)[:-1]
    parents = []
    i = 0
    # pylint: disable=consider-using-enumerate
    for i in range(0, len(pathelements)):
        parents.append(('/' + '/'.join(pathelements[:i+1]), pathelements[i]))
    return parents

def readfile(path, default=None):
    """
    Read a file into a bytestring and return it's content.
    """
    if not os.path.exists(path) and default:
        return default
    with open(path, 'r', encoding=locale.getpreferredencoding()) as requested_file:
        return requested_file.read()

def getfasicon(path):
    """
    Check if a file named basename(path) + '.scmfasicon' exists, and return it's content.
    If not, handover to getfastype(path)
    """
    if os.path.isfile(os.path.join(pathprefix, path) + '.scmsfasicon'):
        return readfile(os.path.join(pathprefix, path) + '.scmsfasicon')
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
    if not mimetype is None:
        if mimetype in mimetype_fas_mapping:
            return mimetype_fas_mapping[mimetype]
        if mimetype.split('/')[0] in mimetype_fas_mapping:
            return mimetype_fas_mapping[mimetype.split('/')[0]]
    return 'fa-file'

def getlastmodifiedfile(path):
    """
    Recursively search for the newest file in the specified directory.
    """

    path = os.path.join('.', path)
    assert os.path.isdir(path), f'{path} is not a directory!'
    newest = {"file": path, "timestamp": os.path.getmtime(path)}
    for root, dirs, files in os.walk(path):
        for directory in dirs:
            timestamp = os.path.getmtime(os.path.join(root, directory))
            if timestamp > newest['timestamp']:
                newest['file'] = os.path.join(root, directory)
                newest['timestamp'] = timestamp
        for directory in files:
            timestamp = os.path.getmtime(os.path.join(root, directory))
            if timestamp > newest['timestamp']:
                newest['file'] = os.path.join(root, directory)
                newest['timestamp'] = timestamp
    return newest

def renderIndexFile(path, lang='en'):
    """
    Search for index files in order of priority (index.org, index.md, index.html, index)
    and render the appropriate content. Returns rendered HTML content or default header.
    If lang is not 'en', attempts to translate source content using Claude API with caching,
    then renders the translated source.
    """
    full_path = os.path.join(pathprefix, path)
    source_content = None
    file_type = None

    # Check for index.org file
    org_path = os.path.join(full_path, 'index.org')
    if os.path.isfile(org_path):
        source_content = readfile(org_path)
        file_type = 'org'
    else:
        # Check for index.md file
        md_path = os.path.join(full_path, 'index.md')
        if os.path.isfile(md_path):
            source_content = readfile(md_path)
            file_type = 'md'
        else:
            # Check for index.html file
            html_path = os.path.join(full_path, 'index.html')
            if os.path.isfile(html_path):
                source_content = readfile(html_path)
                file_type = 'html'
            else:
                # Check for plain index file
                index_path = os.path.join(full_path, 'index')
                if os.path.isfile(index_path):
                    source_content = readfile(index_path)
                    file_type = 'plain'
                else:
                    # Default fallback - return directory header
                    return f'<h1>/{path}</h1>'

    # Generate content hash for caching (based on source content)
    content_hash = get_content_hash(source_content)

    # Get the source content in the target language (translate if needed)
    if lang == 'eng':
        # Use original source content for English
        translated_source = source_content
        # Cache original English source
        cache_translation(content_hash, 'eng', source_content)
    else:
        # Check if translation is already cached
        cached_translation = get_cached_translation(content_hash, lang)
        if cached_translation:
            translated_source = cached_translation
        else:
            # Cache the original English source
            cache_translation(content_hash, 'eng', source_content)

            # Translate source content using Claude
            try:
                translated_source = translate_claude(source_content, lang)
                # Cache the translated source
                cache_translation(content_hash, lang, translated_source)
            except (ImportError, ValueError, RuntimeError) as e:
                # If translation fails, use original content with error comment
                translated_source = f"<!-- Translation error: {str(e)} -->\n{source_content}"

    # Now render the (possibly translated) source content based on file type
    if file_type == 'org':
        return orgpython.to_html(translated_source)
    elif file_type == 'md':
        return markdown.markdown(
            translated_source, extensions=['fenced_code', 'toc', 'tables']
        )
    elif file_type == 'html':
        return translated_source
    elif file_type == 'plain':
        return translated_source
    else:
        return f'<h1>/{path}</h1>'
