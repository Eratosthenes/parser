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

def op_assignment(env: dict, x: any, y: any):
    """ assign x -> y """
    env[y] = x
    return x

TYPES = {
    'NAME': str, 
    'ITER_FUNC_NAME': str, 
    'INT': int, 
    'FLOAT': float,
    'STR': str,
}

class Operation:
    FUNCS = {
        'ASSIGNMENT': op_assignment,
        'ADD': op_add,
        'SUBTRACT': op_subtract,
        'DIVIDE': op_divide,
        'MULTIPLY': op_multiply,
    }

    def __init__(self, token: Token):
        self.name = token.type # e.g. ADD, SUBTRACT, ASSIGNMENT etc
        self.func = self.FUNCS.get(token.type)

class Interpreter:
    def __init__(self, root: AstNode):
        self.root = root
        self.env = {}

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
        def apply(op: Operation, operands: List[Token]) -> Token:
            op1, op2 = operands
            if op1.type != op2.type:
                s1 = f"{op1.value} (type {op1.type.lower()})"
                s2 = f"{op2.value} (type {op2.type.lower()})"
                raise Exception(f"type error: {s1} does not match {s2}")

            op_type = TYPES[op1.type]
            values = [op_type(tok.value) for tok in operands]
            return Token(op1.type, op_type(op.func(*values)))

        def assign(op: Operation, expr_tok: Token, name_tok: Token):
            op_type = TYPES[expr_tok.type]
            expr = op_type(expr_tok.value)
            name = TYPES[name_tok.type](name_tok.value)
            value = op_type(op.func(self.env, expr, name))
            return Token(expr_tok.type, value)

        def _eval(node: AstNode) -> Token:
            if node.token:
                return node.token
            
            operands: List[Token] = []
            for child in node.children:
                if not child.token:
                    operands.append(_eval(child))
                    continue

                token = child.token
                if TYPES.get(token.type):
                    operands.append(token)
                else:
                    op = Operation(token)

            if len(operands) == 0:
                raise Exception("no operands")

            if len(operands) == 1:
                return operands[0]

            # TODO: refactor assign and apply to be part of Operation
            # len(operands) == 2
            # case assignment
            if op.name == 'ASSIGNMENT':
                tok = assign(op, *operands)
                return tok

            # case non-assignment
            return apply(op, operands)

        try:
            result = _eval(self.root).value
            print(self.env)
            return result
        except Exception as e:
            return e.with_traceback().__repr__()

"""
(Pdb) p operands
[<INT: 3>, <NAME: 'a'>]
(Pdb) p op.name
'ASSIGNMENT'
(Pdb) p op.func
<function op_assignment at 0x7f3cb5c3da80>
"""