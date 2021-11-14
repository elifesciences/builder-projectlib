import json
import sys
from . import specs, v1
from .utils import ensure, lookup
import yaml

# this approach to global mutable state feels a bit new nad weird to me.
# there is a means to set a bunch of values initially with **kwargs, but thereafter all
# mutation must go via `set_config`. config can be reset to nothing with `reset_config`.

CONFIG_WHITELIST = ['project_path']

def config(**kwargs):
    "accepts key+vals and sets attributes on *itself* but only if they haven't already been set."
    for key, val in kwargs.items():
        ensure(key in CONFIG_WHITELIST, "key not in CONFIG_WHITELIST, refusing to set: %s" % (key,))
        ensure(not hasattr(config, key), "config has already initialised %r with %r and cannot be modified." % (key, val))
        setattr(config, key, val)
    return config.__dict__

def set_config(key, val=0xDEADBEEF):
    ensure(key in CONFIG_WHITELIST, "key not in CONFIG_WHITELIST, refusing to set: %s" % (key,))
    if val == 0xDEADBEEF:
        delattr(config, key)
    else:
        setattr(config, key, val)
    return config()

def reset_config():
    for key in CONFIG_WHITELIST:
        delattr(config, key)
    return config()

# ---
        
def valid(schema, data):
    try:
        schema.validate(data)
        return True
    except Exception as e:
        print(e)
        return False

def backend(global_defaults):
    dispatch_map = {
        1: v1,
    }
    default_version = 1
    project_version = lookup(global_defaults, 'spec.version', default_version)
    supported_versions = ', '.join(sorted(map(str, dispatch_map.keys())))
    ensure(project_version in dispatch_map, 'unsupported project data version %r. Supported versions: %s' % (project_version, supported_versions))
    return dispatch_map[project_version]

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

def all_project_data():
    "returns a map of *all* project data, properly parsed and expanded."
    global_defaults, raw_project_data = read_project_file(config.project_path)
    api = backend(global_defaults)
    return api.parse_all_project_data(global_defaults, raw_project_data)

def project_data(project_name, alt_config=None):
    """returns the project data of a specific project, properly parsed and expanded.
    optionally sets the alt-config if a known `alt_config` is provided."""
    global_defaults, raw_project_data = read_project_file(config.project_path)
    api = backend(global_defaults)
    ensure(project_name in raw_project_data, "unknown project %r" % project_name)
    pdata = api.parse_project_data(global_defaults, raw_project_data[project_name])
    if alt_config:
        pdata = api.set_project_alt(pdata, alt_config)
    return pdata

def project_data_for_stackname(stackname):
    """convenience. extracts the instance ID from the given `stackname` and uses it to update
    the project with an alt-config - but only if the alt-config key exists. 
    Otherwise you just get the project defaults."""
    (project_name, instance_id) = str(stackname).split('--', 1)[:2]
    alt_config = instance_id
    return project_data(project_name, alt_config)

# ---

def main(project_path, project_name=None, alt_config=None):
    config(project_path=project_path)
    if project_name:
        return project_data(project_name, alt_config)
    return all_project_data()

if __name__ == '__main__':
    args = sys.argv[1:]
    print(json.dumps(main(*args), indent=4))
    exit(0)
