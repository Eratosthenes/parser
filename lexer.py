import sys
import re

def read_tokens(filename):
    """ returns: TokenTable """
    variable_tokens = {}
    fixed_tokens = {}
    with open(filename) as f:
        for line in f:
            if line[0] in {"#", "\n"}:
                continue

            token_name, _, token_regex = line.strip("\n").partition(" ")
            if "#" in token_regex:
                token_regex = token_regex[token_regex.index("#")]

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
                raise Exception("cannot scan line")

    return TokenTable(fixed_tokens, variable_tokens)

def make_partial_tokens(tok_rx, fixed_tokens):
    for i in range(0, len(tok_rx)):
        partial_tok_rx = tok_rx[0:i+1]
        
        # don't overwrite other tokens here
        if fixed_tokens.get(partial_tok_rx) != None:
            continue

        pattern = re.compile(r'^%s$' % re.escape(partial_tok_rx))
        fixed_tokens[partial_tok_rx] = "ERROR", pattern

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"<{self.type}: {repr(self.value)}>"

class TokenTable:
    def __init__(self, fixed_tokens, variable_tokens):
        self.fixed_tokens = fixed_tokens
        self.variable_tokens = variable_tokens

class Lexer:
    def __init__(self, token_table):
        self.i = 0
        self.j = -1 # peek index
        self.buf = []
        self.fixed_tokens = token_table.fixed_tokens
        self.variable_tokens = token_table.variable_tokens

    def _flush(self):
        self.buf = []
        self.j = self.i-1
    
    def _is_match(self):
        test_str = ''.join(self.buf)

        # try fixed_tokens
        if self.fixed_tokens.get(test_str) != None:
            _, pattern = self.fixed_tokens[test_str]
            return pattern, True

        # try variable_tokens
        for pattern in self.variable_tokens.keys():
            pmatch = pattern.match(test_str)
            if pmatch and pmatch.end() == pmatch.endpos:
                return pattern, True

        return None, False

    def _peek(self):
        self.j += 1
        if self.j == len(self.text):
            return False
        self.buf.append(self.text[self.j])
        return True
    
    def set(self, text):
        """ set text to tokenize and reset internal state """
        self.text = text
        self.i = 0
        self._flush()
        return self

    def next(self):
        if not self._peek():
            return

        prev_pattern, found = self._is_match()
        if not found:
            raise Exception(self.text[self.i:].partition(" ")[0])

        while True:
            pattern, found = self._is_match()
            if not found:
                break
            else:
                prev_pattern = pattern
                if not self._peek():
                    break
        
        token_value = self.text[self.i:self.j]
        if self.fixed_tokens.get(token_value) != None:
            token_type, _ = self.fixed_tokens[token_value]
        else:
            token_type = self.variable_tokens[prev_pattern]

        self.i += self.j - self.i
        self._flush()
        return Token(token_type, token_value)

    def lex(self):
        """ return tokens """
        tokens = []
        while True:
            try:
                token = self.next()
                if not token:
                    break
                if token.type not in {"SPACE", "NEWLINE"}:
                    tokens.append(token)
            except Exception as e:
                tokens.append(Token("ERROR", str(e)))
                break

        return tokens

def repl(lexer):
    print("Enter an expression ('q' to quit):")
    while True:
        line = input(">")
        if line.lower() == 'q':
            break
        if line.lower() == 'help':
            print("Fixed tokens:")
            for key, value in lexer.fixed_tokens.items():
                print(f"'{key}': {value}")
            print("\nVariable tokens:")
            for key, value in lexer.variable_tokens.items():
                print(f"{key}: {value}")
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

def main():
    # lexer.py
    if len(sys.argv) == 1: 
        repl(Lexer(read_tokens('bnf.tok')))

    # lexer.py test
    elif "test" in sys.argv[1]: 
        lexer = Lexer(read_tokens('bnf.tok'))
        for case in test_cases:
            print(lexer.set(case).lex())

    # lexer.py input=x.tok
    elif "input" in sys.argv[1]:
        _, _, filename = sys.argv[1].partition("=")
        lexer = Lexer(read_tokens('bnf.tok'))
        text = open(filename).read()
        for token in lexer.set(text).lex():
            print(token)

if __name__=='__main__':
    main()