import rfc3986
import re
#from functools import partial
from schema import Schema, And, Or, Optional

# https://stackoverflow.com/questions/25259134/how-can-i-check-whether-a-url-is-valid-using-urlparse
try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

_domain_name_regex = re.compile("^(?:[a-zA-Z0-9]+(?:\-*[a-zA-Z0-9])*\.)+[a-zA-Z0-9]{2,63}$")

# https://stackoverflow.com/questions/4229235/python-regex-to-match-ip-address-with-cidr#answer-8591470
_ip_address_regex = re.compile(r"(?<!\d\.)(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d|(?:\.\d))")
_ip_address_cidr_regex = re.compile(r"(?<!\d\.)(?<!\d)(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}(?!\d|(?:\.\d))")

def regex_match(regex, x):
    return re.match(regex, x) or False

def domain_name(x):
    """naive domain name test.
1. The domain name should be a-z | A-Z | 0-9 and hyphen(-)
2. The domain name should between 2 and 63 characters long
3. The domain name should not start or end with hyphen (-) (e.g. -google.com or google-.com)
4. The domain name can be a subdomain (e.g. mkyong.blogspot.com)
    """
    # taken from:
    # https://mkyong.com/regular-expressions/domain-name-regular-expression-example/
    # - mkyong, Chirag Katudia
    return regex_match(_domain_name_regex, x)

# https://stackoverflow.com/questions/25259134/how-can-i-check-whether-a-url-is-valid-using-urlparse
def url(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except Exception:
        return False

def uri(x):
    return rfc3986.uri_reference(x).is_valid()

def ip4_address(x):
    return regex_match(_ip_address_regex, x)

def ip4_address_cidr(x):
    return regex_match(_ip_address_cidr_regex, x)

# ---

def nilable(fn):
    "value is allowed to be `None`"
    return Or(None, fn)

def one_of(list_of_values):
    return lambda x: x in list_of_values

# ---

nilable_url = nilable(And(str, url))
nilable_uri = nilable(And(str, uri))
nilable_domain_name = nilable(And(str, domain_name))

# ---

ports_list_schema = [int]
ports_map_schema = {Optional(int): {"cidr-ip": ip4_address_cidr}}
ports_schema = Or(ports_list_schema, ports_map_schema)

ec2_schema = {
    "cluster-size": int,
    "cpu-credits": And(str, one_of(["standard", "unlimited"])),
    "dns-external-primary": bool,
    "dns-internal": bool,
    #"overrides": ...
    "suppressed": [int],
    "ami": str,
    "masterless": bool,
    "master_ip": ip4_address,
    "security-group": ports_schema,
}

aws_schema = {
    "account-id": int,
    Optional("ports"): ports_schema,
    Optional("ec2"): ec2_schema,
}

project_schema = {
    object: object, # so unspecced keys are returned
    
    "description": str,
    "salt": str,
    "domain": nilable_domain_name,
    "intdomain": nilable_domain_name,
    "subdomain": nilable_domain_name,
    "repo": nilable_url,
    "formula-repo": nilable_url,
    "private-repo": nilable_uri,
    "configuration-repo": nilable_uri,
    "default-branch": str,
    "formula-dependencies": [url],
    "aws": aws_schema,
    #"aws-alt": {str: aws_schema}
}
project_schema = Schema(project_schema, ignore_extra_keys=True)
