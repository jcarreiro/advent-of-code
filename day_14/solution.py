#!/usr/bin/env python3

import string

from enum import auto, Enum

def solve_part1(g):
    print(g)

class ProdutionRule(object):
    def __init__(self, reactants, products):
        self.reactants = reactants
        self.products = products

    def __repr__(self):
        return f"ProductionRule({self.reactants}, {self.products}"

class Reactant(object):
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

    def __repr__(self):
        return f"Reactant(\"{self.name}\", {self.quantity})"

class Token(Enum):
    ARROW = auto()
    NUMBER = auto()
    NAME = auto()

class Tokenizer(object):
    def __init__(self, s):
        self.s = s
        self.pos = 0
        self.tokens = []

    def push_token(self, token, value):
        self.tokens.append((token, value))
    
    # returns (token, value)
    def next_token(self):
        token = self._next_token()
        print(f"Got token: {token}")
        return token

    def _next_token(self):
        # Check for previous parsed token which was pushed back on stack.
        if self.tokens:
            return self.tokens.pop()

        while self.pos < len(self.s):
            # peek at next character
            if self.s[self.pos] == " " or self.s[self.pos] == ",":
                # ignore space, ","
                self.pos += 1
            if self.s[self.pos] == "=":
                # next char should be '='
                self.pos += 1
                if self.s[self.pos] == ">":
                    self.pos += 1
                    return (Token.ARROW, None)
                else:
                    raise ValueError("Syntax error in formula")
            elif self.s[self.pos] in string.digits:
                # consume all the digits
                end = self.pos
                while end < len(self.s) and self.s[end] in string.digits:
                    end += 1
                token = (Token.NUMBER, int(self.s[self.pos:end]))
                self.pos = end
                return token
            elif self.s[self.pos] in string.ascii_letters:
                # consume all the letters
                end = self.pos
                while end < len(self.s) and self.s[end] in string.ascii_letters:
                    end += 1
                token = (Token.NAME, self.s[self.pos:end])
                self.pos = end
                return token
        return (None, None)

def parse_rules(s):
    # The grammar for production rules looks like this:
    # 
    #   formula       = reactant_list "=>" product_list
    #   reactant_list = reactant[, reactant_list]
    #   reactant      = number name
    #   product_list  = product[, product_list]
    #   product       = numer name

    def parse_formula(s):
        print(s)
        tokenizer = Tokenizer(s)
        reactants = parse_reactants(tokenizer)
        print(reactants)
        token, _ = tokenizer.next_token()
        if token != Token.ARROW:
            raise ValueError("Syntax error in formula!")
        products = parse_products(tokenizer)
        print(products)
        return ProdutionRule(reactants, products)

    def parse_reactants(tokenizer):
        reactants = []

        # lists must start with a reactant
        reactants.append(parse_reactant(tokenizer))

        # peek ahead for another reactant
        while True:
            token, value = tokenizer.next_token()
            if token == Token.NUMBER:
                tokenizer.push_token(token, value)
                reactants.append(parse_reactant(tokenizer))
            elif token == Token.ARROW:
                # the only valid way to end a reactant list is an arrow operator
                tokenizer.push_token(token, value)
                break
            else:
                # wtf
                raise ValueError("Syntax error in formula!")
        return reactants

    # only diff from reactants is that list ends at end of input
    def parse_products(tokenizer):
        products = []

        # lists must start with a reactant
        products.append(parse_reactant(tokenizer))

        # peek ahead for another reactant
        while True:
            token, value = tokenizer.next_token()
            if token == Token.NUMBER:
                tokenizer.push_token(token, value)
                products.append(parse_reactant(tokenizer))
            elif token == None:
                # eof
                break
            else:
                # wtf
                raise ValueError("Syntax error in formula!")
        return products

    def parse_reactant(tokenizer):
        token, value = tokenizer.next_token()
        if token != Token.NUMBER:
            raise ValueError("Syntax error in formula!")
        quantity = value

        token, value = tokenizer.next_token()
        if token != Token.NAME:
            raise ValueError("Syntax error in formula!")
        name = value

        return Reactant(name, quantity)

    for line in s:
        print(parse_formula(line))

if __name__ == '__main__':
    # In this problem we're given a set of equations showing how we can combine
    # various chemical feedstocks to get fuel for our ship. We need to figure
    # out how much ORE we need to produce one unit of FUEL, given the set of
    # equations as the input.
    #
    # Here's an easy example from the problem:
    example_1 = [
        "10 ORE => 10 A",
        "1 ORE => 1 B",
        "7 A, 1 B => 1 C",
        "7 A, 1 C => 1 D",
        "7 A, 1 D => 1 E",
        "7 A, 1 E => 1 FUEL",
    ]

    # To start with let's parse the production rules in the grammar.
    rules = parse_rules(example_1)