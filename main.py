import re
import sys
from lexer.lexer import TokenTable, Lexer
from parser.parser import parse

def read_tokfile(filename):
    """ returns: TokenTable """
    variable_tokens = {}
    fixed_tokens = {}
    with open(filename) as f:
        for line in f:
            if line[0] in {"#", "\n"}:
                continue

            token_name, _, token_regex = line.strip("\n").partition(" ")
            if "#" in token_regex:
                token_regex = token_regex[:token_regex.index("#")].strip(" ")

            ch = token_regex[0]
            tok_rx = token_regex.removeprefix(ch).removesuffix(ch)

            # process fixed tokens
            if ch == "'":
                if len(tok_rx) > 1:
                    make_partial_tokens(tok_rx, fixed_tokens)

                pattern = re.compile(r'^%s$' % re.escape(tok_rx))
                fixed_tokens[tok_rx] = token_name, pattern
            # process variable length tokens
            elif ch == "\"":
                pattern = re.compile(r'^%s$' % tok_rx)
                variable_tokens[pattern] = token_name
            else:
                raise Exception(f"cannot parse: '{line}'")

    return TokenTable(fixed_tokens, variable_tokens)

def make_partial_tokens(tok_rx, fixed_tokens):
    for i in range(0, len(tok_rx)):
        partial_tok_rx = tok_rx[0:i+1]
        
        # don't overwrite other tokens here
        if fixed_tokens.get(partial_tok_rx) != None:
            continue

        pattern = re.compile(r'^%s$' % re.escape(partial_tok_rx))
        fixed_tokens[partial_tok_rx] = "ERROR", pattern

def repl(lexer):
    print("Enter an expression ('q' to quit):")
    while True:
        line = input(">")
        if line.lower() == 'q':
            break
        if line.lower() == 'help':
            print(lexer)
            continue

        for token in lexer.set(line).lex():
            print(token)

test_cases = [
    "4.1*5",
    "1* 5",
    "1+2 - 3.1415/4 * 5",
    "1.+0.02-3.4 / 4.567*5",
    ".3",
    "1+.3",
    """1
    -2
    / 3.14159
""", # handle new lines
    "hello \"cruel\" wOrld++",
]

def make_dict(arg_str):
    """ return dictionary of command-line arguments """
    arg_d = {}
    for kv in arg_str.split(' '):
        key, val = kv.split('=')
        while key[0] == "-":
            key = key.removeprefix("-")
        arg_d[key] = val

    return arg_d

def main():
    # main.py
    if len(sys.argv) == 1: 
        repl(Lexer(read_tokfile('language.tok')))
        sys.exit(0)
    else:
        args = ' '.join(sys.argv[1:])

    # main.py test
    if "test" in args: 
        lexer = Lexer(read_tokfile('language.tok'))
        for case in test_cases:
            print(lexer.set(case).lex())

    # main.py -tokens=bnf.tok -input=grammar.bnf
    elif "input" in args:
        arg_d = make_dict(args)
        lexer = Lexer(read_tokfile(arg_d["tokens"]))
        text = open(arg_d["input"]).read()
        tokens = lexer.set(text).lex()
        for token in tokens:
            print(token)
        
    # main.py -tokens=language.tok -lang=grammar.bnf
    elif "lang" in args:
        arg_d = make_dict(args)

        lang_lexer = Lexer(read_tokfile(arg_d["tokens"]))
        bnf_lexer = Lexer(read_tokfile('bnf.tok'))

        grammar_bnf = open(arg_d["lang"]).read()
        grammar_tokens = bnf_lexer.set(grammar_bnf).lex() 

        parse(lang_lexer, grammar_tokens)

if __name__=='__main__':
    main()