from lexer.lexer import Lexer

def parse(lexer: Lexer, tokens):
    """ inputs: language lexer, tokenized .bnf file """
    print(lexer)

    print("\nbnf tokens:")
    for token in tokens:
        print(token)