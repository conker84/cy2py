import ast
import inspect


def get_decorators(cls, *args):
    target = cls
    decorators = {}

    def visit_function_def(node):
        decorators[node.name] = []
        for n in node.decorator_list:
            name = ''
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id

            if len(args) == 0 or args.__contains__(name):
                decorators[node.name].append(n)

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_function_def
    node_iter.visit(ast.parse(inspect.getsource(target)))
    return decorators



