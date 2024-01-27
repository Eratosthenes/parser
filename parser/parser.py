from typing import List, Optional
from lexer.lexer import Token

class Rule:
    def __init__(self, lhs: str):
        self.lhs = lhs
        self.elements: List[str] = [] # token.value strings
    
    def __repr__(self):
        return f"<{self.lhs}: {self.elements}>"
    
    def add(self, element):
        self.elements.append(element)

    def is_literal(self) -> bool:
        if len(self.elements) != 1:
            return False

        return self.elements[0].upper() == self.elements
    
class AstNode:
    def __init__(self, rule: Optional[Rule]):
        self.rule = rule
        self.token: Optional[Token] = None
        self.children: List[AstNode] = []
    
    def __repr__(self):
        s = ""
        if self.rule:
            s+=f" rule:{self.rule} "
        if self.token:
            s+=f" tok:{self.token} "
        return "{" + s.strip() + "}"
    
    def set(self, token: Token):
        self.token = token
        return self
    
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
        
        # handle initial AstNode and incoming tokens
        rule = self._matches_rule([self.stack[-1]])
        if rule:
            self.ast_stack.append(AstNode(rule).set(token))
        else:
            self.ast_stack.append(AstNode(None).set(token))

        # reduce
        is_reduced = self._reduce_stack(token)
        while is_reduced:
            is_reduced = self._reduce_stack(token)
    
    def _reduce_stack(self, token: Token) -> bool:
        for i in range(len(self.stack))[::-1]:
            rule = self._matches_rule(self.stack[i:])
            if rule:
                self.stack[i:] = [rule.lhs] # reduce stack
                # reduce ast: rule, token, children
                new_ast = AstNode(rule)
                if rule.is_literal():
                    new_ast.set(token)

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