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

def ast_repl(lexer: Lexer, ast: Ast) -> Ast:
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

    def print_lexer():
        print(lexer)

    def print_tokens():
        print(ast.tokens)

    def print_rules():
        print("Rules:")
        for rule in ast.rules:
            print(rule)
        
    def print_ast():
        print("ast:") 
        ast.print()

    def stack_history():
        print("stack:")
        ast.stack_history()

    OPTIONS = {
        '\\h': help,
        '\\help': help,
        '\\q': quit,
        '\\quit': quit,
        '\\l': print_lexer,
        '\\lexer': print_lexer,
        '\\t': print_tokens,
        '\\tokens': print_tokens,
        '\\r': print_rules,
        '\\rules': print_rules,
        '\\a': print_ast,
        '\\ast': print_ast,
        '\\hist': stack_history,
        '\\history': stack_history,
    }

    line = input(">").lower().strip()
    if not line:
        return ast
    if line[0] != '\\':
        ast.parse(lexer.set(line).lex())
        # itr = Interpreter(ast.root)
        # print("eval stack:")
        # print(itr.eval_stack())
        return ast

    if not OPTIONS.get(line):
        print(f"unrecognized option: '{line}'")
        return ast

    OPTIONS[line]()
    return ast

def repl(lexer: Lexer, bnf_tokens: List[Token]):
    """ 
    REPL for programming language
    inputs: language lexer, tokenized .bnf file 
    """
    print("Enter an expression ('\h' for help or '\q' to quit):")
    rules = RuleSet(bnf_tokens).rules
    ast = Ast(rules)
    while True:
        ast = ast_repl(lexer, ast)