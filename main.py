from lexer.lexer import Lexer
from lexer.tokens import TokenTable
from lexer.repl import repl

def main():
    lang_lexer = Lexer(TokenTable('language.tok'))
    bnf_lexer = Lexer(TokenTable('bnf.tok'))

    grammar_bnf = open('grammar.bnf').read()
    grammar_tokens = bnf_lexer.set(grammar_bnf).emit() 

    repl(lang_lexer, grammar_tokens)

if __name__=='__main__':
    main()