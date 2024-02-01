from typing import List
from lexer.lexer import Token
from parser.parser import AstNode
"""
node: {rule:<expr: ['term', 'op', 'term']>}
    node.children:
        node: {rule:<term: ['INT']>  tok:<INT: '1'>}
        node: {rule:<op: ['ADD']>  tok:<ADD: '+'>}
        node: {rule:<term: ['INT']>  tok:<INT: '2'>}
"""
class Interpreter:
    def __init__(self, root: AstNode):
        self.root = root

    def eval_stack(self) -> List[List[Token]]:
        """ create an evaluation stack """
        def _eval(node: AstNode) -> List[AstNode]:
            r = []
            for child in node.children:
                if child.token:
                    r.append(child.token)
                else: 
                    r.append(_eval(child))
            return r

        return _eval(self.root)

    def eval(self):
        """ evaluate an expression """
        def eval_op(nodes: List[Token]):
            return

        es = self.eval_stack()
        expr = es.pop()
        result = eval_op(expr)
        while es:
            expr = es.pop()
            result = eval_op([result]+expr)

        return result

# NOTE: this is dead code so far
def op_add(x, y):
    return x + y

def op_subtract(x, y):
    return x - y

def op_divide(x, y):
    return x/y

def op_multiply(x, y):
    return x*y

OP_TABLE = {
    'ADD': op_add,
    'SUBTRACT': op_subtract,
    'DIVIDE': op_divide,
    'MULTIPLY': op_multiply,
}
