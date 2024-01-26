from typing import List, Optional
from lexer.lexer import Lexer, Token
from repl.repl import repl_bnf

class Rule:
    def __init__(self, lhs: str):
        self.lhs = lhs
        self.elements: List[str] = [] # token.value strings
    
    def __repr__(self):
        return f"<{self.lhs}: {self.elements}>"
    
    def add(self, element):
        self.elements.append(element)
    
class AstNode:
    def __init__(self, rule: Optional[Rule]):
        self.rule = rule
        self.tokens: List[Token] = []
        self.children: List[AstNode] = []
    
    def set_tokens(self, tokens: List[Token]):
        self.tokens = tokens
        return self
    
def parse_bnf(lexer: Lexer, tokens: List[Token]):
    """ inputs: language lexer, tokenized .bnf file """
    print(lexer)

    rules: List[Rule] = []
    sm = StateMachine()
    for token in tokens:
        rule = sm.next(token)
        if rule:
            rules.append(rule)
        
    print("Rules:")
    for rule in rules:
        print(rule)

    print("Enter an expression ('\q' to quit):")
    while True:
        tokens = repl_bnf(lexer, rules)
        print(tokens)
        ast = make_ast(rules, tokens)
        print(ast)

class Ast:
    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self.stack: List[AstNode] = []
        self.root: Optional[AstNode] = None
    
    def process(self, token: Token):
        if len(self.stack) == 0:
            rule = self._matches_rule([token])
            if rule:
                self.root = AstNode(rule)

        ast_node = AstNode(None).set_tokens([token])
        self.stack.insert(0, ast_node)
        print("stack:")
        for i in range(len(self.stack)):
            last_tokens = list(reversed(self.stack[:i+1]))
            print(last_tokens)
            rule = self._matches_rule(last_tokens) # ISSUE here
            if rule:
                print("rule found:", rule)

        print("done processing")
        return
    
    def _matches_rule(self, tokens: List[Token]) -> Optional[Rule]:
        def is_match(tokens: List[Token], elements: List[str]) -> bool:
            for token, element in zip(tokens, elements):
                if token.type == element:
                    return True                

            return False

        for rule in self.rules:
            if len(tokens) == len(rule.elements):
                if is_match(tokens, rule.elements):
                    print("rule match found:", rule)
                    return rule
        
        print("no rule match found")
        return None
    
def make_ast(rules: List[Rule], tokens: List[Token]) -> Ast:
    ast = Ast(rules)
    for token in tokens:
        ast.process(token)

    return ast

"""
example:
rule = <statement: ['VAR_NAME', 'ASSIGNMENT', 'expr']>
- capital letters should match a token type

shift-reduce algo:
stack                           input           rule:
$                               a := b + "hi"$
$a                              := b + "hi"$    
$name                           := b + "hi"$    <name: ['VAR_NAME']>
$term                           := b + "hi"$    <term: ['name']>
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

# state machine states
SET_LHS = "SET_LHS"
ADD_RULE = "ADD_RULE"

class StateMachine:
    def __init__(self):
        self.state = SET_LHS
        self.handlers = {}
        self.register(SET_LHS, self._handle_set_lhs)
        self.register(ADD_RULE, self._handle_add_rule)

    def next(self, token: Token) -> Optional[Rule]:
        self.state, rule = self.handlers[self.state](token)
        if rule:
            return rule
        return None

    def register(self, state, handler):
        self.handlers[state] = handler

    def _handle_set_lhs(self, token: Token) -> tuple[str, Optional[Rule]]:
        """ 
        handles SET_LHS state 
        returns: (state, Rule)
        """
        if token.type == "BNF_NAME":
            self.rule = Rule(token.value)
            return SET_LHS, None

        elif token.type == "COLON":
            return ADD_RULE, None
        
        else: # token.type == "COMMENT"
            return SET_LHS, None
        
    def _handle_add_rule(self, token: Token) -> tuple[str, Optional[Rule]]:
        """ 
        handles ADD_RULE state 
        returns: (state, Rule)
        """
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
        
        else:
            return ADD_RULE, None