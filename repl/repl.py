import sys
from lexer.lexer import Lexer

def repl_bnf(lexer: Lexer, rules):
    line = input(">")
    if line.lower() == '\q':
        sys.exit(0)
    elif line.lower() == '\h':
        print(lexer)
        return []
    else:
        return lexer.set(line).lex()

def repl(lexer: Lexer):
    print("Enter an expression ('\q' to quit):")
    while True:
        line = input(">")
        if line.lower() == '\q':
            break
        if line.lower() == '\h':
            print(lexer)
            continue

        for token in lexer.set(line).lex():
            print(token)
