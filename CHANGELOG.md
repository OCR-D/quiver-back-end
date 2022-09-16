# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0]

### Added

- All information that is required for the ocrd_all projects (i.e. the GitHub repositories of the ocrd_all submodules). Provided in data/repos.json. This encompasses:
  - links to noteworthy files like the Dockerfile
  - unreleased changes
  - the latest tag
  - if the project has been implemented using Python or bashlib
  - if the projects orcd-tool.json complies to the specs, and
  - if the CLI complies to the specs
  - information about dependency conflicts between (transitive) deps
- Information regarding within which ocrd_all release a project has been released recently. Provided in ocrd_all_releases.json.
- This CHANGELOG.
