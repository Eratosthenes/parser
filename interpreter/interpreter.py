from typing import List, Dict, Callable
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

def op_assignment(env: dict, x: Token, y: Token):
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
    FUNCS: Dict[str, Callable] = {
        'ASSIGNMENT': op_assignment,
        'ADD': op_add,
        'SUBTRACT': op_subtract,
        'DIVIDE': op_divide,
        'MULTIPLY': op_multiply,
    }

    def __init__(self, token: Token):
        self.operation = token.type # eg ADD, ASSIGNMENT etc
        self.func: Callable = self.FUNCS[token.type]
    
    def eval(self, env: Dict[Token, Token], operands: List[Token]):
        if self.operation == 'ASSIGNMENT':
            operands[:1] = self._resolve(env, operands[:1])
            return self._assign(env, *operands)

        operands = self._resolve(env, operands)
        return self._apply(*operands)
    
    def _resolve(self, env: Dict[Token, Token], operands: List[Token]) -> List[Token]:
        """ resolve any operands from environment """
        for i in range(len(operands)):
            token = env.get(operands[i])
            if token:
                operands[i] = token

        return operands

    def _apply(self, op1: Token, op2: Token) -> Token:
        """ apply an operation to a list of operands """
        # type checking
        if op1.type != op2.type:
            s1 = f"{op1.value} (type {op1.type.lower()})"
            s2 = f"{op2.value} (type {op2.type.lower()})"
            raise Exception(f"type error: {s1} does not match {s2}")

        op_type = TYPES[op1.type] # eg str, int, float
        values = [op_type(tok.value) for tok in [op1, op2]]
        return Token(op1.type, op_type(self.func(*values)))

    def _assign(self, env: Dict[Token, Token], expr: Token, name: Token) -> Token:
        """ assign an expression to a value """
        return self.func(env, expr, name)

class Interpreter:
    def __init__(self, root: AstNode):
        self.root = root
        self.env: Dict[Token, Token] = {}
    
    def set(self, root: AstNode):
        self.root = root

    def eval(self) -> str:
        def _eval(node: AstNode) -> Token:
            if node.token:
                env_tok = self.env.get(node.token)
                if env_tok:
                    return env_tok
                return node.token
            
            operands: List[Token] = []
            for child in node.children:
                if not child.token:
                    operands.append(_eval(child))
                    continue

                tok = child.token
                if TYPES.get(tok.type):
                    operands.append(tok)
                else:
                    op = Operation(tok)

            if len(operands) == 0:
                raise Exception("no operands")
            elif len(operands) == 1:
                return operands[0]
            else:
                return op.eval(self.env, operands)

        try:
            value = _eval(self.root).value
            return f"-> {value}"
        except Exception as e:
            return f"{e}"