from argparse import Namespace

from .annotation_utils import get_decorators
from .utils import run_query, parse_arguments
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
from neo4j import GraphDatabase
from IPython.core.magic import (
    Magics,
    cell_magic,
    line_magic,
    magics_class,
    needs_local_scope, no_var_expand
)
from IPython.core.magic_arguments import argument, magic_arguments
import json
import re
import ast

@magics_class
class Cy2Py(Magics):
    cypher_connections = {}
    config_cache = {}
    default_uri = 'bolt://localhost:7687'
    magic_args = None

    def __init__(self, shell):
        Magics.__init__(self, shell=shell)
        decorators = get_decorators(Cy2Py, 'argument')
        method_decorators = decorators['cypher']
        self.magic_args = dict([
            (decorator.args[0].s, (decorator.args[1].s, 'bool' if isinstance(decorator.keywords[0].value, ast.Str) else decorator.keywords[0].value.id))
            for decorator in method_decorators
        ])
        try:
            from google.colab import output
            output.enable_custom_widget_manager()
        except:
            None

    def __parse_args(self, line, local_ns):
        splitted = re.findall(r'[^"\s]\S*|".+?"', line)
        args = dict([(key[2:], None) for key in dict(self.magic_args.values()).keys()])
        inner_args = dict(self.magic_args.values())
        i = 0
        to_remove = []
        while i < len(splitted):
            arg = splitted[i]
            var_name = None

            arg_type = None
            arg_key = None
            if self.magic_args.__contains__(arg):
                arg_key, arg_type = self.magic_args[arg]
            elif inner_args.__contains__(arg):
                arg_type = inner_args[arg]
                arg_key = arg

            if not arg_key:
                i += 1
                continue

            arg_key = arg_key.replace('-', '')

            if 'bool' != arg_type:
                to_remove.append(splitted.pop(i))
                var_name = splitted[i]
                to_remove.append(splitted.pop(i))
            else:
                args[arg_key] = True
                to_remove.append(splitted.pop(i))
                continue

            var_name = var_name.strip()
            if var_name.startswith('"'):
                var_name = var_name[1:var_name.rfind('"')]
            elif var_name.startswith('\''):
                var_name = var_name[1:var_name.rfind('\'')]

            if var_name.startswith('$'):
                var_name = var_name[1:]
            elif var_name.startswith('{'):
                var_name = var_name[1:var_name.rfind('}')]

            if local_ns.__contains__(var_name):
                args[arg_key] = local_ns[var_name]
            else:
                args[arg_key] = var_name

        # we try to reconstruct the query
        if not args['query'] and len(to_remove) > 0:
            args['query'] = line
            for remove in to_remove:
                args['query'] = args['query'].replace(remove, '', 1)
            args['query'] = args['query'].strip()

        return Namespace(**args)

    def __manage_config(self, args, alias, parsed_args):
        if alias not in self.config_cache:
            self.config_cache[alias] = {'config': {
                'colors': {},
                'captions': {},
                'layout': {
                    'layout': 'dagre', 'padding': 0,
                    'nodeSpacing': 10, 'edgeLengthVal': 10,
                    'animate': True, 'randomize': True
                }
            }}

        config = self.config_cache[alias]['config']

        if args.colors:
            config['colors'] = args.colors if isinstance(args.colors, dict) else json.loads(json.loads(args.colors).replace('\'', '"'))

        if args.captions:
            config['captions'] = args.captions if isinstance(args.captions, dict) else json.loads(json.loads(args.captions).replace('\'', '"'))

        if args.layout:
            config['layout'] = args.layout if isinstance(args.layout, dict) else json.loads(json.loads(args.layout).replace('\'', '"'))

        self.config_cache[alias]['config'] = config

        if 'database' not in self.config_cache[alias]:
            self.config_cache[alias]['database'] = None
        if args.database:
            self.config_cache[alias]['database'] = args.database
        elif parsed_args['database'] and not self.config_cache[alias]['database']:
            self.config_cache[alias]['database'] = parsed_args['database']

        if parsed_args['uri'] != '':
            self.config_cache[alias]['uri'] = parsed_args['uri']

    @cell_magic
    @line_magic
    @needs_local_scope
    @magic_arguments()
    @argument("-a", "--alias", type=str, help="""
        The Neo4j connection configuration alias.
        You after you defined it the first time in combination with the other arguments
        you can use only it to connect to the Neo4j instance
        without repassing the arguments each time.
        If you don't specify it the first time you'll pass the config
        it'll became the default for each connection 
    """)
    @argument("-u", "--uri", type=str, help="""
        The Neo4j URI. You can use this kind of URI in order to define
        a specific database to query: neo4j://localhost:7687/my-db
    """)
    @argument("-us", "--username", type=str, help="The Neo4j User")
    @argument("-pw", "--password", type=str, help="The Neo4j Password")
    @argument("-db", "--database", type=str, help="The Neo4j Database, if not provided we use the default")
    @argument("-q", "--query", type=str, help="Pass the Cypher query as argument. Valid only when you use line magic.")
    @argument("-p", "--params", type=str, help="A map of Cypher query parameters")
    @argument("-c", "--close", type=str, help="Close a Driver connection by alias or URI")
    @argument("-co", "--colors", type=str, help="A map label/color")
    @argument("-ca", "--captions", type=str, help="A map label/caption")
    @argument("-la", "--layout", type=str, help="A map for layout configuration")
    @argument("-l", "--list", action='store_true', help="List active configurations")
    @no_var_expand
    def cypher(self, line, cell='', local_ns=None):
        # manage arguments
        is_inline = False
        args = self.__parse_args(line, local_ns)
        if cell == '' and args.query:
            cell = args.query
            is_inline = True
        if 'uri' not in args and 'list' not in args and 'close' not in args:
            return 'Pass --uri, --list or --close'

        if args.list:
            return self.cypher_connections.keys()
        elif args.close:
            driver = None
            if args.close in self.cypher_connections:
                driver = self.cypher_connections.pop(args.close)
            elif args.close in self.config_cache:
                driver = self.cypher_connections.pop(self.config_cache[args.close]['uri'], None)

            if driver:
                driver.close()
                return 'Driver closed successfully'
            else:
                return f'Connection not defined for {args.close}'

        parsed_args = parse_arguments(args)
        alias = parsed_args['alias']
        auth = parsed_args['auth']
        self.__manage_config(args, alias, parsed_args)
        uri = self.config_cache[alias]['uri']

        if uri not in self.cypher_connections:
            self.cypher_connections[uri] = GraphDatabase.driver(uri, auth=auth)

        return run_query(self.cypher_connections[uri], cell, self.config_cache[alias], is_inline, args.params)


def load_ipython_extension(ip):
    ip.register_magics(Cy2Py)
