import sys
from typing import List, Tuple, Optional
from lexer.lexer import Lexer, Token
from parser.parser import RuleSet, Ast
from interpreter.interpreter import Interpreter

# TODO: get rid of this function
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

        for token in lexer.set(line).emit():
            print(token)

def ast_repl(lexer: Lexer, ast: Ast, itr: Optional[Interpreter]) -> Tuple[Ast, Optional[Interpreter]]:
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
        '\\hist': stack_history,
        '\\history': stack_history,
    }

    line = input(">").lower().strip()
    if not line:
        return ast, itr
    if line[0] != '\\':
        ast.reset()
        ast.parse(lexer.set(line).emit())
        itr.set(ast.root)
        print(f"-> {itr.eval()}")
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