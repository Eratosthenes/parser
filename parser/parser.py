from typing import List
from lexer.lexer import Lexer, Token

def parse(lexer: Lexer, tokens: List[Token]):
    """ inputs: language lexer, tokenized .bnf file """
    print(lexer)
    print("BNF tokens:") # <type: value>
    for token in tokens:
        print(token)

    rules = []
    sm = StateMachine()
    for token in tokens:
        rule = sm.next(token)
        if rule:
            rules.append(rule)
        
    print("\nRules:")
    for rule in rules:
        print(rule)

class Rule:
    # elements are either a terminal or another rule
    def __init__(self, lhs, elements=[]):
        self.lhs = lhs
        self.elements = elements 
    
    def __repr__(self):
        return f"<{self.lhs}: {self.elements}>"
    
    def add(self, element):
        self.elements.append(element)

class StateMachine:
    def __init__(self, state="SET_LHS"):
        self.state = state
        self.token_stack = []

    def next(self, token: Token):
        if token.type == "BNF_NAME":

            if self.state == "SET_LHS":
                self.rule = Rule(token.value)
                return

            elif self.state == "ADD_ELEMENT":
                self.rule.add(token.value)
                return

        elif token.type == "COLON":
            self.state = "ADD_ELEMENT"
            return

        elif token.type == "PIPE":
            self.state = "ADD_ELEMENT"
            return

        elif token.type == "SEMICOLON":
            self.state = "SET_LHS"
            return self.rule
