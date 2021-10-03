import sys
from . import specs
import yaml

def parse_project_data(pdata):
    return specs.project_schema.validate(pdata['defaults'])

def parse_project_file(path):
    """opens file, parses it's contents as a project file, returns the project data.
    `path` must have a `.yaml` extension.
    project files that are not well-formed raise an error.
    project files that are invalid raise an `InvalidProjectFileError`."""

    with open(path, 'r') as fh:
        return parse_project_data(yaml.load(fh, Loader=yaml.Loader))
    


if __name__ == '__main__':
    args = sys.argv[1:]
    parse_project_file(args[0])
