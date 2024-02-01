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
    'NAME': any, 
    'ITER_FUNC_NAME': any, 
    'INT': int, 
    'FLOAT': float,
    'STR': str,
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
    
    def eval(self):
        def _eval(node: AstNode) -> Token:
            if node.token:
                return node.token
            
            operands: List[Token] = []
            for child in node.children:
                if not child.token:
                    operands.append(_eval(child))
                    continue

                token = child.token
                if OPERANDS.get(token.type):
                    operands.append(token)
                else:
                    op = OP_TABLE[token.type]

            if len(operands) == 2:
                op1, op2 = operands
                if op1.type != op2.type:
                    s1 = f"{op1.value} (type {op1.type.lower()})"
                    s2 = f"{op2.value} (type {op2.type.lower()})"
                    raise Exception(f"type error: {s1} does not match {s2}")

                op_type = OPERANDS[op1.type]
                value = op(*[op_type(tok.value) for tok in operands])
                return Token(op1.type, value)
            elif len(operands) == 1:
                return operands[0]

        try:
            return _eval(self.root).value
        except Exception as e:
            return str(e)