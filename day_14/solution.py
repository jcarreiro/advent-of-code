#!/usr/bin/env python3

import argparse
import collections
import copy
import math
import random
import string
import time

from collections import deque
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
#        print(f"Got token: {token}")
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
#        print(s)
        tokenizer = Tokenizer(s)
        reactants = parse_reactants(tokenizer)
#        print(reactants)
        token, _ = tokenizer.next_token()
        if token != Token.ARROW:
            raise ValueError("Syntax error in formula!")
        products = parse_products(tokenizer)
#        print(products)
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

    rules = []
    for line in s:
        print(line)
        # Ignore lines starting with '#'.
        line = line.strip()
        if line[0] == "#":
            continue
        rules.append(parse_formula(line))
    return rules

def bfs(rules):
    def can_apply(state, rule):
#        print(f"Checking rule {rule} for state {state}.")
        for reactant in rule.reactants:
            # ORE is special since we have an infinite amount -- we track how
            # much we've used, but we can use as much as want.
            if reactant.name == "ORE":
                continue
            if state.get(reactant.name, 0) < reactant.quantity:
#                print(f"Can't apply rule {rule} to state {state}, don't have enough {reactant.name}.")
                return False
#        print(f"Rule {rule} can apply to state {state}.")
        return True

    def apply_rule(state, rule):
        # To apply a rule, we consume the reactants and add the products.
        # Note that ORE is special -- we have an infinite amount, and we
        # just need to track how much we've used. So instead of consuming
        # ORE, we add the amount used by the rule to the state.
        #
        # Take a copy here since we don't want applying a rule to modify
        # the source state.
        new_state = copy.deepcopy(state)
        for reactant in rule.reactants:
            if reactant.name == "ORE":
                new_state["ORE"] = state["ORE"] + reactant.quantity
            else:
                # In all other cases we consume the reactant.
                new_state[reactant.name] = state[reactant.name] - reactant.quantity
                # It should never be possible to go negative (the rule should
                # not have been applied in this case).
                assert(new_state[reactant.name] >= 0)
        # Now add any products we obtained.
        for product in rule.products:
            # ORE should never be a product.
            assert(product.name != "ORE")
            new_state[product.name] = state.get(product.name, 0) + product.quantity
#        print(f"Applied {rule} to {state}, new state is {new_state}.")
        return new_state

    # Ok, now we have the rules. We're going to try to use graph search for
    # this problem. Our state is whatever chemicals we've got, plus how much
    # ORE we've used so far. Our goal state is any state that has "1 FUEL".
    #
    # To start with we'll try a naive BFS search, but I expect this won't
    # scale and won't always find the min cost to make FUEL (for example
    # consider any set of rules like "1000000 ORE => 1 FUEL" and then a
    # longer, more complex chain of steps that produces 1 FUEL using less
    # than 1000000 ORE).
    #
    # We start having used no ORE and with no other products.
    start = time.monotonic()
    c = 0
    q = deque([{'ORE': 0}])
    while q:
        state = q.popleft()
#        print(f"Considering state {state}.")
        c += 1
        if c % 10000 == 0:
            delta = time.monotonic() - start
            sps = float(c) / float(delta)
            print(f"Checked {c} states in {delta:0.03f} s, {sps:0.03f} states / s. Current state: {state}.")
        # Check for a goal state.
        if 'FUEL' in state:
            # We got FUEL!
            print()
            print(f"Reached goal state: {state}.")
            print(f"ORE cost to create fuel was {state['ORE']}.")
            break
        # Not a goal state; apply production rules.
        for rule in rules:
            if can_apply(state, rule):
                q.append(apply_rule(state, rule))

# Returns an index of chemicals -> rules in which the chemical appears in the
# product list.
def build_product_index(rules):
    index = collections.defaultdict(list)
    for rule in rules:
        for product in rule.products:
            index[product.name].append(rule)
    return index

if __name__ == '__main__':
    # In this problem we're given a set of equations showing how we can combine
    # various chemical feedstocks to get fuel for our ship. We need to figure
    # out how much ORE we need to produce one unit of FUEL, given the set of
    # equations as the input.
    #
    # Here's an easy example from the problem that requires a minimum of 31
    # ORE to create 1 FUEL.
    example_1 = [
        "10 ORE => 10 A",
        "1 ORE => 1 B",
        "7 A, 1 B => 1 C",
        "7 A, 1 C => 1 D",
        "7 A, 1 D => 1 E",
        "7 A, 1 E => 1 FUEL",
    ]

    # This example requires 165 ORE to produce 1 FUEL.
    #
    # The naive BFS search checks over 1e7 states for this example without
    # finding a solution, so either there's a bug in the code, or it's not
    # fast enough to solve this problem.
    #
    # Instead let's try a constraint satisfaction approach.
    example_2 = [
        "9 ORE => 2 A",
        "8 ORE => 3 B",
        "7 ORE => 5 C",
        "3 A, 4 B => 1 AB",
        "5 B, 7 C => 1 BC",
        "4 C, 1 A => 1 CA",
        "2 AB, 3 BC, 4 CA => 1 FUEL",
    ]

    # To start with let's parse the production rules in the grammar.
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()

    # Parse rules from input file.
    rules = parse_rules(open(args.input_file, "r"))

    print("Got rules:")
    for rule in rules:
        print(f"  {rule}")
    print()

    # bfs(rules)

    # To apply the constraints, we need to index the rules by product so that
    # we can quickly find the next set of constraints each time through the
    # loop below.
    product_index = build_product_index(rules)
    print(product_index)

    # The starting constraint is that we need 1 FUEL.
    constraints = {'FUEL': 1}
    # Sometimes when applying a rule we get "too much" of a reactant (ie. we
    # need to apply a rule k times to get enough, and it produces m each time,
    # but k * m > n). This tracks the "surplus" we've produced.
    surplus = {}
    # The total amount of ORE we've spent.
    ore_needed = 0
    while constraints:
        # We're going to assume that each rule only has a single product, and
        # that each product is only produced by one rule, for now. To update
        # our state, we'll pop the "first" item from the constraints, find
        # the rule that produces it, and apply it.
        product_name, product_quantity = constraints.popitem()

        # Apply any surplus units we already have (possibly from expanding
        # a different rule) to the constraint.
        if surplus.get(product_name, 0) > 0:
            c = min(product_quantity, surplus[product_name])
            product_quantity -= c
            surplus[product_name] -= c
            print(f"Applied {c} units of {product_name} from surplus, still need {product_quantity} units.")

        # Did we have enough units already? If not expand a rule to update
        # our constraints.
        if product_quantity > 0:
            # Get the rule that produces this chemical.
            print(f"Expanding product {product_name}.")
            product_rules = product_index[product_name]
            assert(len(product_rules) == 1)
            rule = product_rules[0]
            assert(len(rule.products) == 1)

            # Apply the rule to our state. We need to apply the rule k times to
            # get enough of the inputs, but this may produce more than we
            # actually need (see note about surplus above).
            q = rule.products[0].quantity
            k = math.ceil(float(product_quantity) / float(q))
            print(f"Applying rule {rule} to constraints {k} times.")

            # "Store" any extra units.
            extra_units = q * k - product_quantity
            if extra_units > 0:
                # "Store" the surplus
                surplus[product_name] = extra_units

            # We need enough of the reactants to run this rule k times, so add
            # those to our constraints.
            for reactant in rule.reactants:
                if reactant.name != 'ORE':
                    constraints[reactant.name] = constraints.get(reactant.name, 0) + reactant.quantity * k
                else:
                    # ORE is special; it's not a constraint, we just track how
                    # much we used.
                    ore_needed += reactant.quantity * k
        print(f"New constraints are {constraints}, surplus is {surplus}, ORE needed is {ore_needed}.")

    print(f"{ore_needed} ORE needed to produce 1 FUEL.")
