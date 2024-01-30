import sys
from typing import List
from lexer.lexer import Lexer, Token
from parser.parser import Rule, StateMachine, Ast

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

def repl_bnf(lexer: Lexer, rules: List[Rule]):
    line = input(">")
    if line.lower() == '\q':
        sys.exit(0)
    elif line.lower() == '\h':
        print(lexer)
        return []
    else:
        return lexer.set(line).lex()

def parse_bnf(lexer: Lexer, tokens: List[Token]):
    """ inputs: language lexer, tokenized .bnf file """
    print(lexer)

    rules: List[Rule] = []
    sm = StateMachine()
    for token in tokens:
        rule = sm.next(token)
        if rule:
            rules.append(rule)
        
    print("Rules:")
    for rule in rules:
        print(rule)

    print("Enter an expression ('\q' to quit):")
    while True:
        tokens = repl_bnf(lexer, rules)
        print("tokens:", tokens)
        ast = make_ast(rules, tokens)
        print("ast:") 
        ast.print()
        print("stack:")
        ast.stack_history()

def make_ast(rules: List[Rule], tokens: List[Token]) -> Ast:
    ast = Ast(rules)
    for token in tokens:
        ast.process(token)

    return ast
