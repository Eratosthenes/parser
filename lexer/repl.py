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
    def help():
        print("Options:")
        opts = list(OPTIONS.keys())
        pairs = []
        for i in range(len(opts)):
            if i%2==0:
                pairs.append(opts[i:i+2])            
        for pair in pairs:
            short, long = pair
            print(f"{short} {long}")

    def quit():
        sys.exit(0)

    def tokens():
        print(lexer)

    def print_rules():
        print("Rules:")
        for rule in rules:
            print(rule)

    OPTIONS = {
        '\\h': help,
        '\\help': help,
        '\\q': quit,
        '\\quit': quit,
        '\\t': tokens,
        '\\tokens': tokens,
        '\\r': print_rules,
        '\\rules': print_rules,
    }

    line = input(">").lower().strip()
    if not line:
        return
    if line[0] == '\\':
        if OPTIONS.get(line):
            return OPTIONS[line]()
        else:
            print(f"unrecognized option: '{line}'")
            return []
    else:
        return lexer.set(line).lex()

def repl(lexer: Lexer, bnf_tokens: List[Token]):
    """ 
    REPL for programming language
    inputs: language lexer, tokenized .bnf file """

    rules = RuleSet(bnf_tokens).rules
    print("Enter an expression ('\h' for help or '\q' to quit):")
    while True:
        tokens = repl_bnf(lexer, rules)
        if not tokens:
            continue

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
