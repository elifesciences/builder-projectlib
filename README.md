# builder-projectlib

A library for parsing, expanding and validating the 'projects' file used in the [builder](https://github.com/elifesciences/builder) project.

## installation

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements

## usage

    python -m projectlib.core <project-file> [project-name]
    
for example:

    wget https://raw.githubusercontent.com/elifesciences/builder/master/projects/elife.yaml
    python -m projectlib.core elife.yaml journal | jq
