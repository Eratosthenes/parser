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
    def __init__(self, lhs):
        self.lhs = lhs
        self.rules = [] 
    
    def __repr__(self):
        return f"<{self.lhs}: {self.rules}>"
    
    def add(self, element):
        self.rules.append(element)
    
    def reduce(self):
        rule = Rule(self.lhs)
        new_rules = []
        for r in self.rules:
            if type(r) == str:
                rule.add(r)
            else:
                new_rules.append(r)
        
        new_rules.append(rule)
        self.rules = new_rules


class StateMachine:
    SET_LHS = "SET_LHS"
    ADD_ELEMENT = "ADD_ELEMENT"

    def __init__(self, state=SET_LHS):
        self.state = state # TODO: change to SET_LHS

    """
    re-write as follows:
    def next(self, token: Token):
        self.state, rule = self.handlers[self.state](token)
        return rule

    and have a function for registering handlers:
    def register(self, state, handler):
        self.handlers[state] = handler
    """
    def next(self, token: Token):
        if token.type == "BNF_NAME":

            if self.state == self.SET_LHS:
                self.rule = Rule(token.value)
                return

            elif self.state == self.ADD_ELEMENT:
                self.rule.add(token.value)
                return

        elif token.type == "COLON":
            self.state = self.ADD_ELEMENT
            return
        
        elif token.type == "TERMINAL":
            self.state = self.ADD_ELEMENT
            self.rule.add(token.value)
            return

        elif token.type == "PIPE":
            self.rule.reduce()
            self.state = self.ADD_ELEMENT
            return

        elif token.type == "SEMICOLON":
            self.rule.reduce()
            self.state = self.SET_LHS
            return self.rule