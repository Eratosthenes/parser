from typing import List, Any, Optional

class Token:
    def __init__(self, type: str, value: Any):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"<{self.type}: {repr(self.value)}>"

class TokenTable:
    def __init__(self, fixed_tokens, variable_tokens):
        self.fixed_tokens = fixed_tokens
        self.variable_tokens = variable_tokens

class Lexer:
    def __init__(self, token_table: TokenTable):
        self.i = 0
        self.j = -1 # peek index
        self.buf: List[str] = []
        self.fixed_tokens = token_table.fixed_tokens
        self.variable_tokens = token_table.variable_tokens

    def __str__(self):
        s = "Fixed tokens:\n"
        for key, value in self.fixed_tokens.items():
            val_type, _ = value
            s += f"'{key}': {val_type}\n"

        s += "\nVariable tokens:\n"
        for key, value in self.variable_tokens.items():
            s += f"\"{key.pattern}\": {value}\n"
        
        return s[:-1]

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

    def next(self) -> Optional[Token]:
        if not self._peek():
            return None

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

    def emit(self) -> List[Token]:
        """ return tokens """
        tokens = []
        while True:
            try:
                token = self.next()
                if not token:
                    break
                if token.type not in {"SPACE"}:
                    tokens.append(token)
            except Exception as e:
                tokens.append(Token("ERROR", str(e)))
                break

        return tokens