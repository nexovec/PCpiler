# -*- coding: utf-8 -*-
from os import lseek
import os.path
"""
Spyder Editor

This is a temporary script file.
"""
import sys
class Token:
    def __init__(self, token, data = None):
        self.token = token
        self.data = data or []
    def __str__(self):
        return self.token
class ENUM_TOKENS:
    ENDLINE     = "ENDLINE"
    IDENTIFIER  = "IDENTIFIER"
    NUM_LITERAL = "NUM_LITERAL"
    STR_LITERAL = "STR_LITERAL"
    COLON       = "COLON"
    LPAREN      = "LPAREN"
    RPAREN      = "RPAREN"
    LBRACE      = "LBRACE"
    RBRACE      = "RBRACE"
    OPERATOR    = "OPERATOR"

tokens = []
opList = ['=','+','-','*','/']


def error(msg):
    print(msg, file=sys.stderr)
    exit(-1)

def isWhitespace(text, index):
    if text[index] == ' ' or text[index] == '\n' or text[index] == '\t':
        return True
    else:
        return False


def closeToken(openToken):
    tokens.append(openToken)
    return None

def openNewToken(char: str):
    openToken = None
    if char == '\n':
        openToken = Token(ENUM_TOKENS.ENDLINE)
    elif char.isspace():
        return None
    elif char.isalpha():
        openToken = Token(ENUM_TOKENS.IDENTIFIER)
    elif char.isdigit():
        openToken = Token(ENUM_TOKENS.NUM_LITERAL)
    elif char == '\"':
        openToken = Token(ENUM_TOKENS.STR_LITERAL)
    elif char == '(':
        openToken = Token(ENUM_TOKENS.LPAREN)
    elif char == ')':
        openToken = Token(ENUM_TOKENS.RPAREN)
    elif char == '{':
        openToken = Token(ENUM_TOKENS.LBRACE)
    elif char == '}':
        openToken = Token(ENUM_TOKENS.RBRACE)
    elif opList.__contains__(char):
        openToken = Token(ENUM_TOKENS.OPERATOR)
    return openToken

def tokenize(text, index = 0, openToken = None):
    if index == len(text):
        return
    char = text[index]
    if openToken == None:
        openToken = openNewToken(char)
        if openToken == None:
            return tokenize(text, index + 1, None)
        else:
            tokens.append(openToken)
    tok  = openToken.token
    ts = ENUM_TOKENS()
    if tok   == ts.ENDLINE:
        openToken = None
    elif tok == ts.COLON:
        openToken = None
    elif tok == ts.IDENTIFIER:
        if char.isalpha() or char.isdigit():
            openToken.data.append(char)
        else:
            return tokenize(text, index, None)
    elif tok == ts.STR_LITERAL:
        if char == '\"':
            if len(openToken.data)!=0:
                openToken.data = openToken.data[1:]
                openToken = None
        openToken.data.append(char)
    elif tok == ts.NUM_LITERAL:
        if char.isdigit():
            openToken.data.append(char)
        else:
            openToken = None
    elif tok == ts.OPERATOR:
        if opList.__contains__(char):
            openToken.data.append(char)
        else:
            openToken = None
    elif tok == ts.LPAREN:
        openToken = None
    elif tok == ts.RPAREN:
        openToken = None
    elif tok == ts.LBRACE:
        openToken = None
    elif tok == ts.RBRACE:
        openToken = None
    else:
        print("Parsing error, character not expected")
        exit(-1)
    return tokenize(text, index + 1, openToken)


def hasThisToken(index):
    if index < len(tokens):
        return True
    else:
        return False
    
def hasNextToken(index):
    if index + 1 < len(tokens):
        return True
    else:
        return False
    
def hasNextNTokens(index, n):
    if index + n < len(tokens):
        return True
    else:
        return False

def isValueToken(index):
    if tokens[index].token == ENUM_TOKENS.STR_LITERAL or tokens[index].token == ENUM_TOKENS.NUM_LITERAL or tokens[index].token == ENUM_TOKENS.IDENTIFIER:
        return True
    else:
        return False


class INSTRUCTION_BLOCK:
    ASSIGN     = "ASSIGN"
    ADD        = "ADD"
    
# NOTE: this parses the code into instructions.
def parseBinaryOperator(operatorIndex, leftSideIndex, rightSideIndex):
    error("Not yet implemented")
    
def parseUnaryOperator(operatorIndex, leftSideIndex):
    error("Not yet implemented")

def parseExpression(index):
    if not hasThisToken(index):
        # end of file
        return None
    if not isValueToken(index):
        # end of competence
        return None
    rSide = tokens[index]
    lSide = parseExpression(index+2)
    if lSide == None:
        parseUnaryOperator(tokens[index+1], rSide)
    else:
        parseBinaryOperator(tokens[index + 1], rSide, lSide)
    

def parseCodeBlock(index):
    # TODO: register function names before their commands are added into the cache
    error("Not yet implemented")

def parseFunctionCall(index):
    error("Not yet implemented")

def parseLvalueCommand(index):
    assert(hasThisToken(index))
    assert(hasNextToken(index))
    token = tokens[index]
    assert(token.token == ENUM_TOKENS.IDENTIFIER, "Unexpected token type " + str(token.token) + ", IDENTFIER expected")
    if tokens[index+1].token == ENUM_TOKENS.OPERATOR:
        listOfExpressionTokens = parseExpression(index)
        # TODO: cache listOfExpressionTokens
    elif tokens[index+1].token == ENUM_TOKENS.LPAREN:
        listOfExpressionTokens = parseFunctionCall(index)
    else:
        error("Unexpected token type "+str(tokens[index].token)+", expected IDENTIFIER or LPAREN")
    
def parseCommand(index):
    # FIXME: needs to cache the parsed commands
    assert(hasThisToken(index))
    t = tokens[index].token
    if t == ENUM_TOKENS.IDENTIFIER:
        return parseLvalueCommand(index)
    elif t == ENUM_TOKENS.LBRACE:
        return parseCodeBlock(index)
    else:
        error("Parsing error on token")


def execute(index = 0):
    assert(hasThisToken(index))
    openToken = tokens[index]
    parseCommand(index)
    
    # TODO: example print function
    # TODO: clear commandBuilderCache, singleCommandTokensList, maintain expectedTokens
    # TODO: better error logging
    # TODO: generate variable assignments
    # TODO: support expressions
    # TODO: generate function calls
    # TODO: accept multiple parameters
    # TODO: type checking
    # TODO: explicit type conversions
    # TODO: require
    # TODO: generate structs
    # TODO: support traits
    # TODO: support generics
    # TODO: append expected Tokens

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("usage: python temp.py <filename>")
        return -1
    filename = args.pop()
    print("Parsing " + filename)

    text = None
    with open(os.path.abspath(filename)) as f:
        text = f.readlines()
    tokenize('\n'.join(text))
    for _, v in enumerate(tokens):
        print(v)
    print()
    execute()
    pass
if __name__ == "__main__":
    main()
