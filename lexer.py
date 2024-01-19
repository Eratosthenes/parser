import sys
import re

def read_tokens(filename):
    variable_tokens = {}
    fixed_tokens = {}
    with open(filename) as f:
        for line in f:
            token_name, _, token_regex = line.strip("\n").partition(" ")
            ch = token_regex[0]

            # process fixed tokens
            if ch == "'":
                tok_rx = token_regex.removeprefix(ch).removesuffix(ch)
                pattern = re.compile(r'^%s$' % re.escape(tok_rx))
                fixed_tokens[tok_rx] = {}
                fixed_tokens[tok_rx] = token_name, pattern
            # process variable length tokens
            elif ch == "\"":
                tok_rx = token_regex.removeprefix(ch).removesuffix(ch)
                pattern = re.compile(r'^%s$' % tok_rx)
                variable_tokens[pattern] = token_name
            else:
                raise Exception("cannot scan line")

    return fixed_tokens, variable_tokens

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"<{self.type}: {repr(self.value)}>"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.i = 0
        self.j = -1 # peek index
        self.buf = []

    def _flush(self):
        self.buf = []
        self.j = self.i-1
    
    def _is_match(self):
        test_str = ''.join(self.buf)

        # try fixed_tokens
        if fixed_tokens.get(test_str) != None:
            _, pattern = fixed_tokens[test_str]
            return pattern, True

        # try variable_tokens
        for pattern in variable_tokens.keys():
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
        if fixed_tokens.get(token_value) != None:
            token_type, _ = fixed_tokens[token_value]
        else:
            token_type = variable_tokens[prev_pattern]

        self.i += self.j - self.i
        self._flush()
        return Token(token_type, token_value)

def lex(line):
    tokens = []
    text = Lexer(line)
    while True:
        try:
            token = text.next()
            if not token:
                break
            if token.type not in {"SPACE", "NEWLINE"}:
                tokens.append(token)
        except Exception as e:
            tokens.append(Token("ERROR", str(e)))
            break

    return tokens

def repl():
    print("Enter an expression ('q' to quit):")
    while True:
        line = input(">")
        if line.lower() == 'q':
            break
        if line.lower() == 'help':
            print("Fixed tokens:")
            print(fixed_tokens)
            print("\nVariable tokens:")
            print(variable_tokens)
            continue

        for token in lex(line):
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
    "hello \"cruel\" world++",
]

def main():
    if len(sys.argv) > 1 and "test" in sys.argv[1]:
        for case in test_cases:
            print(lex(case))
    else:
        repl()

if __name__=='__main__':
    fixed_tokens, variable_tokens = read_tokens('tokens.txt')
    main()