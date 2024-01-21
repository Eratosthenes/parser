from typing import List
from lexer.lexer import Lexer, Token
from repl.repl import repl_bnf

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

def parse_bnf(lexer: Lexer, tokens: List[Token]):
    """ inputs: language lexer, tokenized .bnf file """
    print(lexer)

    rules = []
    sm = StateMachine()
    sm.register(SET_LHS, handle_set_lhs)
    sm.register(ADD_ELEMENT, handle_add_element)
    for token in tokens:
        rule = sm.next(token)
        if rule:
            rules.append(rule)
        
    print("Rules:")
    for rule in rules:
        print(rule)

    print("Enter an expression ('q' to quit):")
    while True:
        tokens = repl_bnf(lexer, rules)
        print(tokens)
        ast = make_ast(rules, tokens) # TODO: make this a class
        print(ast)

def make_ast(rules: List[Rule], tokens: List[Token]):
    stack = []
    for token in tokens:
        pass
    return

"""
example:
rule = <statement: ['VAR_NAME', 'ASSIGNMENT', 'expr']>

AstNode:
    type = statement # not strictly necessary
    token = None
    children = [
        AstNode{.type=literal, .token=<VAR_NAME, 'a'>}, 
        AstNode{.type-literal, .token=<ASSIGNMENT, ':='>}, 
        AstNode{.type=expr, children=[...]}
    ]

AstNode:
    type = literal
    token = <VAR_NAME, 'a'>
    children = []
"""
class AstNode:
    def __init__(self, rule):
        self.type = rule.lhs # eg, statement, expr, op
        self.tokens = [] # any resolved tokens for rule
        self.children = [] # contains AstNodes
    
# state machine states
SET_LHS = "SET_LHS"
ADD_ELEMENT = "ADD_ELEMENT"

class StateMachine:
    def __init__(self):
        self.state = SET_LHS
        self.handlers = {}

    def next(self, token: Token):
        self.state, rule = self.handlers[self.state](self, token)
        if rule:
            self.rule = rule
        return rule

    def register(self, state, handler):
        self.handlers[state] = handler

"""
state machine handlers
    input: StateMachine, Token
    returns: state, rule
"""

def handle_set_lhs(self, token):
    """ handles SET_LHS state """
    if token.type == "BNF_NAME":
        return SET_LHS, Rule(token.value)

    elif token.type == "COLON":
        return ADD_ELEMENT, None
    
    else:
        return SET_LHS, None
    
def handle_add_element(self, token):
    """ handles ADD_ELEMENT state """
    if token.type == "BNF_NAME":
        self.rule.add(token.value)
        return ADD_ELEMENT, None

    elif token.type == "TERMINAL":
        self.rule.add(token.value)
        return ADD_ELEMENT, None

    elif token.type == "PIPE":
        self.rule.reduce()
        return ADD_ELEMENT, None

    elif token.type == "SEMICOLON":
        self.rule.reduce()
        return SET_LHS, None

    else:
        return ADD_ELEMENT, None
