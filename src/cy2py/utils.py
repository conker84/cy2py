import networkx as nx
import ipycytoscape
from IPython.core.display import display

node_centered = {
    'selector': 'node',
    'style': {
        'font-size': '10',
        'label': 'data(label)',
        'height': '60',
        'width': '60',
        'text-max-width': '60',
        'text-wrap': 'wrap',
        'text-valign': 'center',
        'background-color': 'data(color)',
        'background-opacity': 0.6,
        'border-width': 3,
        'border-color': '#D3D3D3'
    }
}
edge_directed_named = {
    'selector': 'edge',
    'style': {
        'font-size': '8',
        'label': 'data(label)',
        'line-color': '#D3D3D3',
        'text-rotation': 'autorotate',
        'target-arrow-shape': 'triangle',
        'target-arrow-color': '#D3D3D3',
        'curve-style': 'bezier',
        'text-background-color': "#FCFCFC",
        'text-background-opacity': 0.8,
        'text-background-shape': 'rectangle',
        'width': 'data(weight)'
    }
}
my_style = [node_centered, edge_directed_named]

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse


def to_nextworkx(graph, colors, captions, mappings=None):
    networkx_graph = nx.MultiDiGraph()

    def add_node(node):
        label = ':' + ':'.join(node.labels)
        props = dict(node.items())
        color = ''
        if label in colors:
            color = colors[label]
        if label in captions and captions[label] in props:
            props['labels'] = label
            label = props[captions[label]]

        networkx_graph.add_node(node.id, label=label, color=color, properties=props, title=label, tooltip=str(props))

    def add_edge(edge):
        props = dict(edge.items())
        weight = props.get('weight', 1)
        networkx_graph.add_edge(edge.start_node.id, edge.end_node.id, weight=weight, label=edge.type, tooltip=str(props))

    for node in graph._nodes.values():
        add_node(node)

    for rel in graph._relationships.values():
        add_edge(rel)

    return networkx_graph


default_display_config = {'layout': 'dagre', 'padding': 0,
                          'nodeSpacing': 10, 'edgeLengthVal': 10,
                          'animate': True, 'randomize': True,
                          'maxSimulations': 1500}


def display_graph(networkx_graph, config):
    w = ipycytoscape.CytoscapeWidget()
    w.graph.add_graph_from_networkx(networkx_graph)
    w.set_style(my_style)
    w.set_layout(name=config['layout'] if 'layout' in config else default_display_config['layout'],
                 padding=config['padding'] if 'padding' in config else default_display_config['padding'],
                 nodeSpacing=config['nodeSpacing'] if 'nodeSpacing' in config else default_display_config[
                     'nodeSpacing'],
                 edgeLengthVal=config['edgeLengthVal'] if 'edgeLengthVal' in config else default_display_config[
                     'edgeLengthVal'],
                 animate=config['animate'] if 'animate' in config else default_display_config['animate'],
                 randomize=config['randomize'] if 'randomize' in config else default_display_config['randomize'],
                 maxSimulations=config['maxSimulations'] if 'maxSimulations' in config else default_display_config[
                     'maxSimulations'])
    w.set_tooltip_source('tooltip')
    display(w)


def run_query(driver, query, cfg, is_inline, params=None):
    # we return only the last one
    config = cfg['config']
    with driver.session(database=cfg['database']) as session:
        result = None
        for sub_query in query.split(';'):
            sub_query = sub_query.strip()
            if sub_query != '':
                result = session.run(sub_query, **params) if params else session.run(sub_query)

        graph = result.graph()
        if len(graph._nodes) > 0:
            nx_graph = to_nextworkx(graph, config['colors'], config['captions'])
            return nx_graph if is_inline else display_graph(nx_graph, config['layout'])
        else:
            return result.to_df()


def parse_arguments(args):
    parsed_uri = urlparse.urlparse(args.uri)

    uri = ''
    if parsed_uri.hostname and parsed_uri.scheme:
        uri = f'{parsed_uri.scheme}://{parsed_uri.hostname}'

    if parsed_uri.port:
        uri = f'{uri}:{parsed_uri.port}'

    auth = None
    if parsed_uri.username and parsed_uri.password:
        auth = (parsed_uri.username, parsed_uri.password)
    elif args.username and args.password:
        auth = (args.username, args.password)

    alias = args.alias if args.alias else 'default'

    db = parsed_uri.path[1:] if len(parsed_uri.path) > 0 != '' else None
    return {'uri': uri, 'auth': auth, 'alias': alias, 'database': db}


