import re
from typing import Any

class Token:
    def __init__(self, type: str, value: Any):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"<{self.type}: {repr(self.value)}>"
    
    def __eq__(self, token) -> bool:
        return isinstance(token, Token) and \
            self.type == token.type and \
            self.value == token.value
    
    def __hash__(self) -> int:
        return hash((self.type, self.value))

class TokenTable:
    """ 
    processes a .tok file into fixed and variable-length tokens
    """
    def __init__(self, filename):
        self.fixed_tokens = {}
        self.variable_tokens = {}
    
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
                        self._make_partial_tokens(tok_rx)

                    pattern = re.compile(r'^%s$' % re.escape(tok_rx))
                    self.fixed_tokens[tok_rx] = token_name, pattern
                # process variable length tokens
                elif ch == "\"":
                    pattern = re.compile(r'^%s$' % tok_rx)
                    self.variable_tokens[pattern] = token_name
                else:
                    raise Exception(f"cannot parse: '{line}'")

    def _make_partial_tokens(self, tok_rx):
        for i in range(0, len(tok_rx)):
            partial_tok_rx = tok_rx[0:i+1]
            
            # don't overwrite other tokens here
            if self.fixed_tokens.get(partial_tok_rx) != None:
                continue

            pattern = re.compile(r'^%s$' % re.escape(partial_tok_rx))
            self.fixed_tokens[partial_tok_rx] = "ERROR", pattern