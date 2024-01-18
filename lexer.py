import re

def read_tokens(filename):
    tokens = {}
    with open(filename) as f:
        for line in f:
            token_name, token_regex = line.split()
            pattern = re.compile(r'^%s$' % token_regex)
            tokens[pattern] = token_name

    tokens[re.compile(r'^ $')] = "SPACE" # whitespace
    return tokens

token_d = read_tokens('tokens.txt')

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"<{self.type}: '{self.value}'>"

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
        for pattern in token_d.keys():
            if pattern.match(''.join(self.buf)):
                return pattern, True
        return pattern, False

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
            raise Exception(f"{self.text[self.i:].split()[0]}")

        while True:
            pattern, found = self._is_match()
            if not found:
                break
            else:
                prev_pattern = pattern
                if not self._peek():
                    break
        
        token_type = token_d[prev_pattern]
        token_value = self.text[self.i:self.j]
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
            if token != "SPACE":
                tokens.append(token)
        except Exception as e:
            tokens.append(Token("ERROR", str(e)))
            break

    return tokens

test_cases = [
    "4.1*5",
    "1* 5",
    "1+2 - 3/4 * 5",
    "1.+0.02-3.4 / 4.567*5",
    ".3",
    "1+.3",
]

if __name__=='__main__':
    for case in test_cases:
        print(lex(case))