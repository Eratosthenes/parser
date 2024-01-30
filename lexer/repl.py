import sys
from typing import List
from lexer.lexer import Lexer, Token
from parser.parser import Rule, RuleSet, Ast
from interpreter.interpreter import Interpreter

def lexer_repl(lexer: Lexer):
    """ prints tokenized input """
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

def repl(lexer: Lexer, bnf_tokens: List[Token]):
    """ 
    REPL for programming language
    inputs: language lexer, tokenized .bnf file """
    print(lexer)

    rules = RuleSet(bnf_tokens).rules
    print("Rules:")
    for rule in rules:
        print(rule)

    print("Enter an expression ('\q' to quit):")
    while True:
        tokens = repl_bnf(lexer, rules)
        print("tokens:", tokens)

        ast = Ast(rules)
        ast.parse(tokens)

        print("stack:")
        ast.stack_history()

        print("ast:") 
        ast.print()

        itr = Interpreter(ast.root)
        print("eval stack:")
        print(itr.eval_stack())