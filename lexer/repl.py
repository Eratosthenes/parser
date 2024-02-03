import sys
from typing import List, Tuple
from lexer.lexer import Lexer, Token
from parser.parser import RuleSet, Ast
from interpreter.interpreter import Interpreter

def ast_repl(lexer: Lexer, ast: Ast, itr: Interpreter) -> Tuple[Ast, Interpreter]:
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

    def print_stack():
        print("stack:")
        ast.print_stack()
    
    def print_env():
        print("env:")
        print(itr.env)

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
        '\\e': print_env,
        '\\env': print_env,
        '\\s': print_stack,
        '\\stack': print_stack,
    }

    line = input(">").lower().strip()
    if not line:
        ast.reset()
        return ast, itr
    if line[0] != '\\':
        ast.reset()
        ast.parse(lexer.set(line).emit())
        if ast.stack and ast.stack[-1]=='ERROR':
            print("syntax error: check \\tokens")
        elif len(ast.stack) > 1:
            print("parse error: check \stack")
        else:
            itr.set(ast.root)
            print(itr.eval())
        return ast, itr

    if not OPTIONS.get(line):
        print(f"unrecognized option: '{line}'")
        return ast, itr

    OPTIONS[line]()
    return ast, itr

def repl(lexer: Lexer, bnf_tokens: List[Token]):
    """ 
    REPL for programming language
    inputs: language lexer, tokenized .bnf file 
    """
    print("Enter an expression ('\h' for help or '\q' to quit):")
    rules = RuleSet(bnf_tokens).rules
    ast = Ast(rules)
    itr = Interpreter(ast.root)
    while True:
        ast, itr = ast_repl(lexer, ast, itr)