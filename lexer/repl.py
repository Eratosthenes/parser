import sys
from typing import List, Tuple, Optional
from lexer.lexer import Lexer, Token
from parser.parser import RuleSet, Ast
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

    def eval_stack():
        print("eval stack:")
        print(itr.eval_stack())

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
        '\\es': eval_stack,
        '\\eval_stack': eval_stack,
    }

    line = input(">").lower().strip()
    if not line:
        return ast, itr
    if line[0] != '\\':
        ast.reset()
        ast.parse(lexer.set(line).lex())
        return ast, Interpreter(ast.root)

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
    itr = None
    while True:
        ast, itr = ast_repl(lexer, ast, itr)
        print(f"-> {itr.eval()}")