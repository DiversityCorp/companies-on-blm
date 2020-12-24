# Building a local database

This project does not require serving data from a live database because our data source of truth are the Markdown files that live in the repo. This structure allows our data and source control to be public and for contributors to help us directly through Github.

This guide will demonstrate how to create a sqlite database locally, and use [datasette](https://github.com/simonw/datasette) to explore the database on a local server.

## Pre-reqs

Install [sqlite](https://www.tutorialspoint.com/sqlite/sqlite_installation.htm)
Install [Python3](https://www.python.org/downloads/)

Run the following commands to get the database running locally:

Note: please open an Issue on Github if these instructions don't work for you, or there are extra steps you had to take. We want to make this better!

```bash
cd db
source venv/bin/activate
pip install
markdown-to-sqlite ../companies/*.md companies-on-blm.db companies
datasette serve companies-on-blm.db
```
