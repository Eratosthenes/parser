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
