#!/usr/bin/python3.2 -tt

# Copyright (c) 2014, Adel Qodmani
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, 
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF 
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys

# Bugs:
# 1- Cannot handle hex numbers
# 2- the reserved words should NOT be case sensitive

# To do:
# 1- Add quote 
# 2- Add function calls (done!) 
#    (define test (lambda (x) (if (equal? x 0) 0 (+ x (test (- x 1))))))

def main():
  read_eval_print()

def read_eval_print():
  table = SymbolTable()
  table = build_table(table)
  try:
    while True:
      expr = input("=>")
      tokens = lex(expr)
      parsed = parse(tokens)
      val = lisp_eval(parsed, table)
      if val is None:
        continue
      else:
        print(val)
  except EOFError:
    print("")
    print("End of file reached")
    print("Moriturus te saluto.")
    sys.exit(0)

def lisp_eval(expr, table):
  ''' Evaluates an expression in a given table and returns the result '''
  # We should check first if the thing is a variable or function
  if isinstance(expr, str):
    # Could be either a function name or a var name
    correct_table = table.lex_locate(expr)
    return correct_table[expr]
  elif not isinstance(expr, list): # not list & not var/func => literal
    return expr
  elif expr[0] == "quote":
    return expr[1:]
  elif expr[0] == "define": # (define var expr)
    table[expr[1]] = lisp_eval(expr[2], table)
  elif expr[0] == "if": # (if test then else)
    res = None
    if lisp_eval(expr[1], table):
      res = lisp_eval(expr[2], table)
    else:
      res = lisp_eval(expr[3], table)
    return res
  elif expr[0] == "lambda": # (lambda (var*) expr)
    # return a function that takes a set of arguments and returns the
    # evaluation of the expr while executing in a new table that has the current
    # one as 'outer' and it contains all the arguments given to the function
    # as values (expr[2]) and all the names of parameters it takes (args)
    return lambda *args: lisp_eval(expr[2], SymbolTable(expr[1], args, table))
  else: # must be a function call 
    # Build a list of the evaluation of every part of expr
    tmp = []
    for x in expr:
      tmp.append(lisp_eval(x, table))
    # remove the first term of the expr which is the function object
    func = tmp.pop(0)
    # expand the list into separate arguments and call the func
    return func(*tmp)

def parse(tokens):
  ''' Given a list of tokens, it returns a list representation of the
  program (nested lists of expressions) '''
  if len(tokens) == 0:
    SyntaxError("Unexpected EOF")
  token = tokens.pop(0)
  if token == ")":
    SyntaxError("Unexpected )")
  elif token == "(":
    expr_list = []
    # While we have tokens to read
    # parse them and add their list to our list
    while tokens[0] != ")":
      expr_list.append(parse(tokens))
    tokens.pop(0) # pop the final )
    return expr_list
  else:
    # if the token we hit is not a new expression or an error
    # it has to be either an int, float or Lisp symbol
    try: 
      return int(token)
    except ValueError:
      try:
        return float(token)
      except ValueError:
        return str(token)

def SyntaxError(err):
  print(err)
  sys.exit(1)

def lex(prog):
  ''' Takes a program and returns all the tokens in it as a list of strings '''
  # We should replace add spaces around parenthesis for split to work
  prog = prog.replace("(", " ( ")
  prog = prog.replace(")", " ) ")
  tokens = prog.split()
  return tokens

class SymbolTable(dict):
  ''' Represents a runtime table, technically the symbol table of a given 
  scope and it has an outer attribute that's also an table '''
  def __init__(self, parms=(), args=(), outer=None):
    self.update(zip(parms,args))
    self.outer = outer

  def lex_locate(self, var):
    ''' Find the innermost SymbolTable where var appears. '''
    if var in self:
      return self
    elif self.outer is None:
      return None
    else:
      return self.outer.lex_locate(var)

def build_table(table):
  ''' Returns an table filled with the most common Lisp functions '''
  import math, operator
  table.update(vars(math)) # sin, sqrt, ...
  table.update( {
    'and': lambda x,y: x & y,
    'or': lambda x,y: x | y,
    'xor': lambda x,y: x ^ y,
    })
  table.update( {
    '+': operator.add, 
    '-': operator.sub, 
    '*': operator.mul, 
    '/': operator.truediv, 
    'not': operator.not_,
    '>': operator.gt, 
    '<': operator.lt, 
    '>=': operator.ge, 
    '<=': operator.le, 
    '=': operator.eq, 
    'equal?': operator.eq, 
    'length': len, 
    'cons': lambda x,y:[x]+y,
    'car': lambda x:x[0],
    'cdr': lambda x:x[1:], 
    'append':operator.add,  
    'list': lambda *x:list(x), 
    'list?': lambda x:isinstance(x,list), 
    'null?': lambda x:x==[], 
    'symbol?': lambda x: isinstance(x, str)
    })
  return table

if __name__ == "__main__":
  main()
