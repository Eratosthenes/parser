from typing import List
from lexer.lexer import Token
from parser.parser import AstNode

def op_add(x, y):
    return x+y

def op_subtract(x, y):
    return x-y

def op_divide(x, y):
    return x/y

def op_multiply(x, y):
    return x*y

OPERANDS = {
    'NAME': str, 
    'ITER_FUNC_NAME': str, 
    'INT': int, 
    'FLOAT': float,
}

OP_TABLE = {
    'ADD': op_add,
    'SUBTRACT': op_subtract,
    'DIVIDE': op_divide,
    'MULTIPLY': op_multiply,
}

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

    # TODO: handle typing and assignments
    # TODO: attempt to redo tihs function with simpler logic
    def eval(self):
        """ evaluate an expression """
        def _eval(node: AstNode) -> Token:
            if node.token:
                token = node.token
                return OPERANDS[token.type](token.value)

            operands: any = []
            for child in node.children:
                if not child.token:
                    operands.append(_eval(child))
                    continue

                token = child.token
                if token.type in OPERANDS.keys():
                    op_type = OPERANDS[token.type]
                    operands.append(op_type(token.value))
                elif token.type in OP_TABLE.keys():
                    op_func = OP_TABLE[token.type]
                else:
                    operands.append(_eval(child))

            if len(operands) == 2:
                op1, op2 = operands
                t1, t2 = list(map(type, operands))
                if t1 != t2:
                    raise Exception(f"type error: {op1} ({t1}) does not match {op2} ({t2})")
                return op_func(*operands)
            elif len(operands) == 1:
                return operands[0]

        try:
            return _eval(self.root)
        except Exception as e:
            return str(e)