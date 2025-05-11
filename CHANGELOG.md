# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.1.1](https://github.com/nomike/scms/releases/tag/1.1.1) - 2025-05-11

<small>[Compare with v1.1.0](https://github.com/nomike/scms/compare/v1.1.0...1.1.1)</small>

### Fixed

- Fix detection and rendering of plain 'index' files ([3a3edd6](https://github.com/nomike/scms/commit/3a3edd6122d3a0ba5e92a270fb3f887b1fd180ce) by nomike).

## [1.1.0](https://github.com/nomike/scms/releases/tag/1.1.0) - 2025-05-11

<small>[Compare with 1.0.0](https://github.com/nomike/scms/compare/1.0.0...1.1.0)</small>

This release adds support for org-files, which are a popular format for notes and task management.
So instead of 'index' or 'index.md' files, you can now also use 'index.org'.

This release adds `org-python` as a requirement. Be sure to run
`pip install -r requirements.txt --upgrade` in your virtual environment to install the new
dependency.

Depending on your setup, you might also want to `killall scms.fcgi` to force the webserver to
reload the application.

### Added

- Add support for org-files. ([fd9cc8b](https://github.com/nomike/scms/commit/fd9cc8bc55ec40677fea707ba6773eb2d5eaea07) by nomike).

## [1.0.0](https://github.com/nomike/scms/releases/tag/1.0.0) - 2025-05-11

<small>[Compare with first commit](https://github.com/nomike/scms/compare/a880905b6acb03a98f817cde20d1dc552536e7e1...1.0.0)</small>

### Added

- Add changelog ([a880905](https://github.com/nomike/scms/commit/a880905b6acb03a98f817cde20d1dc552536e7e1) by nomike).
