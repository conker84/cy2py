# cy2py: seamless Neo4j integration in Python Notebooks 

## Install

To install, run:
`pip install cy2py`

Or clone this repository and run:
`python setup.py install`

## How you can use it

You can use cy2py in two ways:

* as a line magic, it returns a Python dataframe that you can than manipulate as you wish

* as cell magic that will print a graph or dataframe if the result is tabular

## Magic arguments

You can check the listo of accepted arguments by running the following command:

`%cypher?`

```bash
%cypher [-a ALIAS] [-u URI] [-us USERNAME] [-pw PASSWORD] [-db DATABASE]
              [-q QUERY] [-c CLOSE] [-co COLORS] [-ca CAPTIONS] [-la LAYOUT]
              [-l]

optional arguments:
  -a ALIAS, --alias ALIAS
                        The Neo4j connection configuration alias. You after
                        you defined it the first time in combination with the
                        other arguments you can use only it to connect to the
                        Neo4j instance without repassing the arguments each
                        time. If you don't specify it the first time you'll
                        pass the config it'll became the default for each
                        connection
  -u URI, --uri URI     The Neo4j URI. You can use this kind of URI in order
                        to define a specific database to query:
                        neo4j://localhost:7687/my-db
  -us USERNAME, --username USERNAME
                        The Neo4j User
  -pw PASSWORD, --password PASSWORD
                        The Neo4j Password
  -db DATABASE, --database DATABASE
                        The Neo4j Database, if not provided we use the default
  -q QUERY, --query QUERY
                        Pass the Cypher query as argument. Valid only when you
                        use line magic.
  -c CLOSE, --close CLOSE
                        Close a Driver connection by alias or URI
  -co COLORS, --colors COLORS
                        A map label/color
  -ca CAPTIONS, --captions CAPTIONS
                        A map label/caption
  -la LAYOUT, --layout LAYOUT
                        A map for layout configuration
  -l, --list            List active configurations
```

## Example

Under the examples directory you'll find a Google Colab notebook that shows how to use
cy2py in order to dive into a Neo4j crime dataset showing also how is easy 
to seamlessly leverage other visualization libraries such as Ploty.

