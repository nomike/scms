# scms Copyright (C) 2020 - nomike <nomike@nomike.com>
# This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE.
# This is free software, and you are welcome to redistribute it
# under certain conditions

"""
Creates a Flask application which serves the scms.
"""

import os
import urllib.parse
from io import StringIO

import flask
from flask import Flask

from . import templatehelper


def create_application():
    """
    Factory for creating a Flask application.
    """
    application = Flask(
            __name__,
            instance_relative_config=True,
            static_folder=f"templates/{templatehelper.config['template']}/static")
    # paths sent by flask are relative to the "public" directory. This prefix should be added to
    # get paths relative to the pages root directory.
    pathprefix = ''

    @application.route('/<path:path>')
    def serve_directory_or_file(path):
        """
        Main handler for all paths
        """
        path = urllib.parse.unquote(path)
        fullpath = os.path.join(pathprefix, path)
        if not os.path.exists(fullpath):
            return serve_error(404, "File not found...")
        if os.path.isdir(fullpath):
            return serve_directory(path)

        # If a specified path exists, dreamhost seems to serve the file directly without
        # invoking this Flask application.
        # As nonexistent paths are taken care of above, this else-branch is not expected to
        # ever be called. It is left in as a
        # stub though, in case this ever changes.
        return serve_file(path)

    def serve_directory(path):
        """
        Serve a directory.
        """
        if not path.endswith('/') and len(path) > 1:
            # Ensure paths always end with a "/"
            return flask.redirect('/' + path + '/')
        return flask.render_template(
                os.path.join(templatehelper.config['template'], 'directory.html'),
                pathprefix = pathprefix,
                path = path,
                templatehelper = templatehelper)

    @application.route('/')
    def serve_root():
        """
        `@application.route('/<path:path>')` doesn't match '/' and thus this convenience function
            is needed.
        """
        return serve_directory_or_file(os.path.curdir)

    def serve_error(code, message=None):
        if os.path.exists(
                os.path.join(
                        __name__,
                        'templates',
                        templatehelper.config['template'],
                        f'{code}.html')):
            template = f'{code}.html'
        else:
            template = 'error.html'
        return flask.make_response((
                flask.render_template(
                        os.path.join(templatehelper.config['template'], template),
                        code=code,
                        message=message,
                        templatehelper=templatehelper,
                        pathprefix=pathprefix,
                        path=''),
                code,
                None))

    def serve_file(path):
        """
        Left as just a stub as it is unlikely to be called anytime soon.
        """
        return flask.send_file(os.path.join('..', 'public', path))

    return application

# Create an instance of the scms application.
app = create_application()
