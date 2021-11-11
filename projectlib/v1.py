from collections import OrderedDict
from .utils import ensure
from functools import wraps
import copy

CLOUD_EXCLUDING_DEFAULTS_IF_NOT_PRESENT = ['rds', 'ext', 'elb', 'alb', 'cloudfront', 'elasticache', 'fastly', 'eks', 'docdb', 'waf']

def complement(pred):
    @wraps(pred)
    def wrapper(*args, **kwargs):
        return not pred(*args, **kwargs)
    return wrapper

def isint(v):
    return str(v).lstrip('-+').isdigit()

def nth(x, n):
    "returns the nth value in x or None"
    ensure(isint(n), "n must be an integer", TypeError)
    try:
        return list(x)[n]
    except (KeyError, IndexError):
        return None
    except TypeError:
        raise

def first(x):
    "returns the first value in x"
    return nth(x, 0)

lfilter = lambda func, *iterable: list(filter(func, *iterable))
    
def splitfilter(func, data):
    return lfilter(func, data), lfilter(complement(func), data)

def deepcopy(data):
    return copy.deepcopy(data)

def deepmerge(into, from_here, excluding=None):
    "destructive deep merge of `into` with values `from_here`"
    if not excluding:
        excluding = []
    child_exclude, exclusions = splitfilter(lambda v: isinstance(v, dict), excluding)
    child_exclude = first(child_exclude) or {}

    for key in exclusions:
        if key in into and key not in from_here:
            del into[key]

    for key, val in from_here.items():
        if key in into and isinstance(into[key], dict) \
                and isinstance(val, dict):
            deepmerge(into[key], from_here[key], child_exclude.get(key, []))
        else:
            into[key] = val

def _project_cloud_alt(project_alt_contents, project_base_cloud, global_cloud):
    cloud_alt = OrderedDict()

    # handle the alternate configurations
    for altname, altdata in project_alt_contents.items():
        # take project's *current cloud state*,
        project_cloud = deepcopy(project_base_cloud)

        # merge in any overrides
        deepmerge(project_cloud, altdata)

        # merge this over top of original cloud defaults
        orig_defaults = deepcopy(global_cloud)

        deepmerge(orig_defaults, project_cloud, CLOUD_EXCLUDING_DEFAULTS_IF_NOT_PRESENT)
        cloud_alt[str(altname)] = orig_defaults

    return cloud_alt

def parse_project_data(global_defaults, project_data):
    "does a deep merge of defaults+project data with a few exceptions"

    # global_defaults, project_list = all_projects(project_file)
    
    # exceptions.
    excluding = [
        'aws',
        'vagrant',
        'aws-alt',
        'gcp-alt',
        {'aws': CLOUD_EXCLUDING_DEFAULTS_IF_NOT_PRESENT},
    ]
    pdata = deepcopy(global_defaults)
    deepmerge(pdata, project_data, excluding)

    # handle the alternate configurations
    pdata['aws-alt'] = _project_cloud_alt(
        pdata.get('aws-alt', {}),
        pdata.get('aws', {}),
        global_defaults['aws']
    )
    pdata['gcp-alt'] = _project_cloud_alt(
        pdata.get('gcp-alt', {}),
        pdata.get('gcp', {}),
        global_defaults['gcp']
    )

    return pdata

def parse_all_project_data(global_defaults, all_project_data):
    return {pname: parse_project_data(global_defaults, project_data) for pname, project_data in all_project_data.items()}
