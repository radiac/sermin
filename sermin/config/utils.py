"""
Sermin utils
"""
from collections import defaultdict


def parse_args(args):
    """
    Parse command line arguments

        unnamed
        --arg
        --no-arg
        --arg=value
        --namespace:arg
        --no-namespace:arg
        --namespace:arg=value

    Returns a tuple of (unnamed, named), where:
        unnamed     List of unnamed arguments
        named       Dictionary of namespaces
                    Each value is a dictionary of named arguments and values
    """
    unnamed = []
    named = defaultdict(dict)

    if not args:
        return unnamed, named

    # Process state
    for arg in args:
        # Args not starting with -- aren't named
        if not arg.startswith('--'):
            unnamed.append(arg)
            continue

        # Find key and value
        if '=' in arg:
            key, val = arg[2:].split('=', 1)
        elif arg.startswith('--no-'):
            key = arg[5:]
            val = False
        else:
            key = arg[2:]
            val = True

        # Find namespace
        if ':' not in key:
            # Core setting - namespace into sermin
            namespace = 'sermin'
        else:
            namespace, key = key.split(':', 1)

        # Store key and value
        named[namespace][key] = val

    return unnamed, named
