from typing import List
from lexer.lexer import Lexer, Token
from repl.repl import repl_bnf

class Rule:
    def __init__(self, lhs):
        self.lhs = lhs
        self.elements: List[str] = [] # token.value strings
    
    def __repr__(self):
        return f"<{self.lhs}: {self.elements}>"
    
    def add(self, element):
        self.elements.append(element)
    
def parse_bnf(lexer: Lexer, tokens: List[Token]):
    """ inputs: language lexer, tokenized .bnf file """
    print(lexer)

    rules = []
    sm = StateMachine()
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
    token = tokens[0]
    for rule in rules:
        pass
    return

"""
example:
rule = <statement: ['VAR_NAME', 'ASSIGNMENT', 'expr']>
- capital letters should match a token type

shift-reduce algo:
stack                           input
$                               a := b + "hi"$
$a                              := b + "hi"$
$name                           := b + "hi"$
$term :=                        b + "hi"$
$term :=                        b + "hi"$
$term := b                      + "hi"$
$term := name                   + "hi"$
$term := term                   + "hi"$
$term := term +                 "hi"$
$term := term op                "hi"$
$term := term op "hi"           $
$term := term op term           $
$term := term expr              $
$term := expr                   $
$statement                      $

NOTE: always reduce as far as possible

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
ADD_RULE = "ADD_RULE"

class StateMachine:
    def __init__(self):
        self.state = SET_LHS
        self.handlers = {}
        self.register(SET_LHS, self._handle_set_lhs)
        self.register(ADD_RULE, self._handle_add_rule)

    def next(self, token: Token):
        self.state, rule = self.handlers[self.state](token)
        if rule:
            return rule

    def register(self, state, handler):
        self.handlers[state] = handler

    def _handle_set_lhs(self, token):
        """ handles SET_LHS state """
        if token.type == "BNF_NAME":
            self.rule = Rule(token.value)
            return SET_LHS, None

        elif token.type == "COLON":
            return ADD_RULE, None
        
        else: # token.type == "COMMENT"
            return SET_LHS, None
        
    def _handle_add_rule(self, token):
        """ handles ADD_RULE state """
        if token.type == "BNF_NAME":
            self.rule.add(token.value)
            return ADD_RULE, None

        elif token.type == "TERMINAL":
            self.rule.add(token.value)
            return ADD_RULE, None

        elif token.type == "PIPE":
            current_rule = self.rule
            self.rule = Rule(self.rule.lhs)
            return ADD_RULE, current_rule

        elif token.type == "SEMICOLON":
            return SET_LHS, self.rule