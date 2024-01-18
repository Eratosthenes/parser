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

class Text:
    def __init__(self, text):
        self.text = text
        self.i = 0
        self.peek_idx = -1 
        self.buf = []
    
    def _flush(self):
        self.buf = []
        self.peek_idx = self.i-1
    
    def _is_match(self):
        for pattern in token_d.keys():
            if pattern.match(''.join(self.buf)):
                return pattern, True
        return pattern, False

    def _peek(self):
        self.peek_idx += 1
        if self.peek_idx >= len(self.text):
            return False
        self.buf.append(self.text[self.peek_idx])
        return True

    def next(self):
        if not self._peek():
            return

        prev_pattern, found = self._is_match()
        if not found:
            raise Exception(f"exception encountered on: \"{self.text[self.peek_idx]}\"")

        while True:
            pattern, found = self._is_match()
            if not found:
                break
            else:
                prev_pattern = pattern
                if not self._peek():
                    break
        
        token = token_d[prev_pattern]
        self.i += self.peek_idx - self.i
        self._flush()
        return token

def lex(line):
    tokens = []
    text = Text(line)
    while True:
        try:
            token = text.next()
        except:
            tokens.append(f"parse error: \"{line}\"")
            break
        if not token:
            break
        if not token == "SPACE":
            tokens.append(token)

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