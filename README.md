# scms - The Shitty Content Management System

scms is a very simple and leightweight content management system based on Flask.
It uses Jinja2 based templates and is intended to show the directory structure of the public folder. It's goal is to have a minimal feature set while allowing for some flexibility in template design.

## A word on security

scms is designed to serve static websites. No user supplied parameters, form-uploads, databases, etc. are supported. Thus the security precautions are quite minimal. So be careful what to serve on the public internet.

## Installation

### Dreamhost shared server

scms is designed to run on shared webservers from dreamhost.
A few things need to be prepared though.

#### Install custom python3

Install a custom python3 version (scms was tested on v. 3.9 but should be running older 3.x versions too) as per these instructions: <https://help.dreamhost.com/hc/en-us/articles/115000702772-Installing-a-custom-version-of-Python-3>

#### Install a python3 venv

Install a python3 venv as per these instructions:
<https://help.dreamhost.com/hc/en-us/articles/115000695551-Installing-and-using-virtualenv-with-Python-3>

### Install scms

1. Clone this git repository to your websites directory (e.g. `/home/<dreamhostuser>/<domainname>/scms/`).
2. Copy the example wsgi script to `/home/<dreamhostuser>/<domainname>/passenger_wsgi.py`.

__Note:__ You have to put in your dreamhost username at the shebang of this script.

### Add content

Create the `public` folder (`/home/<dreamhostuser>/<domainname>/public`) and fill it with files, subfolders or whatever content you desire. You can find more information on that below.

### Setup fast-cgi

Copy scms.fcgi.example to your website's 'public' folder and rename it to 'scms.fcgi'. Make sure the shebang points to your custom python3 venv.

### Setup .htaccess

Add the following lines to your .htaccess file in your website's 'public' folder:

```apache
RewriteEngine On
AddHandler fcgid-script .fcgi
RewriteRule ^(scms\.fcgi)$ 404.h4ml [L]
RewriteRule ^(scms\.fcgi/.*)$ - [L]
RewriteRule ^(.*)$ scms.fcgi/$1 [L]
```

### Troubleshooting

If you're getting HTTP/500 errors when trying to open your website, check the error logs. They can be found in `~/logs/<domainname>/https/error.log`.

## The public directory

__Note:__ This describes the behaviour of the default template, shipped with scms.

scms is designed to render directories. If a path points to a file existing in the public folder, dreamhost will serve that file directlu and will not invoke scms.

If the path doesn't point to a file, scms is invoked, leaving only two options: The path is invalid or it is a directory.

For invalid paths, a HTTP/404 response is served.
For directories, scms renders it using it's templates.

The rendered page usually contains a filelist and some content.

### content

If a file named `index` exists in a folder, it is rendered in the main section of the page. If not, a single `<h1>` block containing the page title is served.

### .scmsnotemplate

If a file named `.scmsnotemplate` is present in a directory, the contents of `index` are served directly, without any template around.

### .scmsnonavigation

If a file named `.scmsnonavigation` is present in a directory, the navigation pane is not rendered.

### *.scmstarget

If a file `something.scmstarget` exists, the `target="_blank"` attribute is added to the links in the directory listing. The contents of the file are used as attribute-value. This allows you to open links in a new tab by creating this file and inserting `_blank` in it (without trailing newline!).

### *.scmsfasicon

Similar to *.scmstarget, this allows you to change the icon of a directory entry. See the section on FontAwesome below for more info.

## FontAwesome

The default template uses fontawesome to render icons in the directory list. The `templatehelper` module contains a mapping of common mimetypes to icons from the FontAwesome free tier.
If you want to override the icon for a specific file, create a *.scmsfasicon file (as outlined above) and put the desired FontAwesome identifier (see `templatehelper.py` for examples).

## Templatehelper

In addition to the path and the pathprefix, the `templatehelper` module is passed to the templates. Every function defined in there and every import can be used inside the templates.

For example:

```jinja2
{% if templatehelper.os.path.isfile(templatehelper.os.path.join(pathprefix, path, 'index')) %}
{{ templatehelper.readfile(templatehelper.os.path.join(pathprefix, path, 'index')) | safe }}
{% endif %}
```

__Note:__ Please look at `templatehelper.py` for a documentation of the available functions.

## The default template

SCMS ships with a default template.
__Note:__ It is now possible to add your own template. Just enable it in 'config.yaml'. More on template structures below,
This section describes some quirks of that template.

### Image galleries

If a folder contains a subfolder "image", an image gallery is created using all the files within that "image"-subfolder. The images are not downsized, no thumbnails are being generated.
The images are displayed in a responsive grid and can be enlarged to a modal image brosser when being clicked.

## Writing templates

sscm is a flask application and thus relies on it's template engine. If you want to add your own template, just add a folder to the 'templates/custom/' folder and set it in config.yaml.

The minimum content of a template is:
static/
directory.html
error.html

### Mandatory elements

#### static/

A folder intended to use static files. You can put css, javscript and images files there which are supposed to be used by the template.

#### directory.html

This template is called for rendering directories. It can of course include other directories. See the default template for examples.

#### error.html

This template is used to render error pages (e.g. HTTP/404).

### Specific error template

Optionally you could create templates for specific erro codes. The name has
to be [errorcode].html (e.g. '404.html'). If no specific error template is
found, sscm falls back to 'error.html'.

## Development

### Versioning

This project uses [EffVer](https://jacobtomlinson.dev/effver/).

Version numbers are comprised of three parts: Macro, Meso, Micro.

If the macro version is incremented, expect a lare effort when upgrading.
Meso version increments are usually small changes, but may require some effort.
Micro version increments are usually bugfixes or small changes, which should not require any effort when upgrading.
