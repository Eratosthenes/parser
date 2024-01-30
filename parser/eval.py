from typing import List
from lexer.lexer import Token

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

"""
node: {rule:<expr: ['term', 'op', 'term']>}
    node.children:
        node: {rule:<term: ['INT']>  tok:<INT: '1'>}
        node: {rule:<op: ['ADD']>  tok:<ADD: '+'>}
        node: {rule:<term: ['INT']>  tok:<INT: '2'>}
"""

def eval_op(nodes: List[Token]):
    return