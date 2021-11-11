import json
import sys
from . import specs, v1
from .utils import ensure, lookup
import yaml

def valid(schema, data):
    try:
        schema.validate(data)
        return True
    except Exception as e:
        print(e)
        return False

def parse_all_project_data(global_defaults, project_map):
    dispatch_map = {
        1: v1,
    }
    default_version = 1
    project_version = lookup(global_defaults, 'spec.version', default_version)
    supported_versions = ', '.join(sorted(map(str, dispatch_map.keys())))
    ensure(project_version in dispatch_map, 'unsupported project data version %r. Supported versions: %s' % (project_version, supported_versions))
    project_parser = dispatch_map[project_version]
    return project_parser.parse_all_project_data(global_defaults, project_map)
    
# ---

def read_project_file(path):
    """reads the project file data at `path` and validates the 'defaults' section, returning a pair of (defaults, raw_project_data_list)).
    individual project data along with the defaults can then be parsed into a full project map."""
    with open(path, 'r') as fh:
        project_file_data = yaml.load(fh, Loader=yaml.Loader)
        ensure('defaults' in project_file_data, "'defaults' section is missing.")
        defaults = project_file_data.pop('defaults')
        ensure(valid(specs.project_schema, defaults), "'defaults' section is invalid.")
        return (defaults, project_file_data)

#

if __name__ == '__main__':
    args = sys.argv[1:]
    data = parse_all_project_data(*read_project_file(args[0]))
    if len(args) >= 2:
        project = args[1]
        print(json.dumps(data.get(project), indent=4))
