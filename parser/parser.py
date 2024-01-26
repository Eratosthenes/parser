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
        self.literal: bool = self.is_literal() if self.rule else False
        self.tokens: List[Token] = []
        self.children: List[AstNode] = []
    
    def __repr__(self):
        s = ""
        if self.rule:
            s+=f" rule: {self.rule} "
        if self.literal:
            s+=f" LITERAL "
        if len(self.tokens) > 0:
            s+=f" tokens: {self.tokens} "
        return "{" + s.strip() + "}"
    
    def is_literal(self) -> bool:
        length_is_one = self.rule and len(self.rule.elements) == 1
        if not length_is_one:
            return False
        
        if self.rule:
            element = self.rule.elements[0]
        else:
            return False
        return element.upper() == element
    
    def add(self, token: Token):
        self.tokens.append(token)
        return self
    
"""
AstNode:
    rule = statement # not strictly necessary
    literal = bool
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

class Ast:
    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self.stack: List[str] = []
        self.ast_stack: List[AstNode] = []
        self.root: Optional[AstNode] = None

    def traverse(self, ast_node: Optional[AstNode]=None, depth: int=0):
        if not ast_node:
            ast_node = self.ast_stack[0]

        print("\t"*depth + "node:", ast_node)
        for child in ast_node.children:
            self.traverse(child, depth+1)
    
    def process(self, token: Token):
        # shift
        self.stack.append(token.type)
        
        # handle initial AstNode
        rule = self._matches_rule(self.stack)
        if rule:
            self.ast_stack.append(AstNode(rule).add(token))
        else:
            self.ast_stack[-1].add(token)

        # reduce
        print("stack before:", self.stack)
        is_reduced = self._reduce_stack(token)
        while is_reduced:
            is_reduced = self._reduce_stack(token)

        print("stack after:", self.stack)
        return
    
    def _reduce_stack(self, token: Token) -> bool:
        for i in range(len(self.stack))[::-1]:
            rule = self._matches_rule(self.stack[i:])
            if rule:
                print("rule match:", rule)
                self.stack[i:] = [rule.lhs]
                # rule, token, children
                new_ast = AstNode(rule)
                if new_ast.literal:
                    new_ast.add(token)

                new_ast.children = self.ast_stack[i:]
                self.ast_stack[i:] = [new_ast]
                return True

        return False
    
    def _matches_rule(self, token_types: List[str]) -> Optional[Rule]:
        def is_match(token_types: List[str], elements: List[str]) -> bool:
            for token_type, element in zip(token_types, elements):
                if token_type != element:
                    return False                

            return True

        for rule in self.rules:
            if len(token_types) == len(rule.elements):
                if is_match(token_types, rule.elements):
                    return rule
        
        return None
    
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
        ast.traverse()

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