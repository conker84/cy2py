from unittest import TestCase

from IPython.testing.globalipapp import start_ipython
from testcontainers.neo4j import Neo4jContainer

from src.cy2py.cy2 import Cy2Py


class CypherMagicTest(TestCase):
    neo4j_container = None
    neo4j_version = '4.4.10-enterprise'
    neo4j_url = None
    _ip = None

    @classmethod
    def setUpClass(cls):
        cls.neo4j_container = (Neo4jContainer('neo4j:' + cls.neo4j_version)
                               .with_env("NEO4J_ACCEPT_LICENSE_AGREEMENT", "yes")
                               .with_env("NEO4J_dbms_security_auth__enabled", "false"))
        cls.neo4j_container.start()
        cls.neo4j_url = cls.neo4j_container.get_connection_url()
        with cls.neo4j_container.get_driver().session() as session:
            session.write_transaction(
                lambda tx: tx.run("UNWIND range(1, 10) AS id CREATE (c:Customer{id: id, name: 'Person ' + id })"))

        cls._ip = start_ipython()
        cls._ip.register_magics(Cy2Py)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.neo4j_container.stop()
        except:
            pass

    def test_line_magic(self):
        res = self._ip.run_cell(raw_cell=f'''
            %cypher -l
        ''')
        assert res.success
        self._ip.run_cell(raw_cell=f'''
            neo4j_url = '{self.neo4j_url}'
        ''')
        res = self._ip.run_cell(raw_cell='''
            df = %cypher -u $neo4j_url MATCH (c:Customer) RETURN c.companyName as name
            print([[df['name'][ind] for ind in df.index]])
        ''')

        assert res.success
        self._ip.run_cell(raw_cell=f'''
            query = 'MATCH (c:Customer) RETURN c.companyName as name'
        ''')
        res = self._ip.run_cell(raw_cell='''
            df = %cypher -q "$query"
            print([[df['name'][ind] for ind in df.index]])
        ''')
        assert res.success
        res = self._ip.run_cell(raw_cell='''
            graph_query = 'MATCH (c:Customer) RETURN c'
            nx_graph = %cypher -q $graph_query
            print(nx_graph)
        ''')
        assert res.success
        res = self._ip.run_cell(raw_cell='''
            %cypher -c $neo4j_url
        ''')
        assert res.success

    def test_cell_magic(self):
        self._ip.run_cell(raw_cell='''
            colors = {"Product": "blue"}
        ''')
        self._ip.run_cell(raw_cell=f'''
            neo4j_url = '{self.neo4j_url}'
        ''')
        res = self._ip.run_cell(raw_cell='''
            %%cypher -u $neo4j_url -co "$colors"
            MATCH (c:Customer)
            RETURN c
        ''')
        assert res.success
        # do the second call by leveraging the cache
        res = self._ip.run_cell(raw_cell='''
            %%cypher
            MATCH (c:Customer)
            RETURN c
        ''')
        assert res.success

    def test_cell_magic_non_default_db(self):
        self._ip.run_cell(raw_cell='''
            colors = {"Product": "blue"}
        ''')
        self._ip.run_cell(raw_cell=f'''
            neo4j_url = '{self.neo4j_url}/system'
        ''')
        res = self._ip.run_cell(raw_cell='''
            %%cypher -u $neo4j_url -co "$colors"
            SHOW DATABASES
        ''')
        assert res.success
        # do the second call by leveraging the cache
        res = self._ip.run_cell(raw_cell='''
            %%cypher
            SHOW DATABASES
        ''')
        assert res.success
