# -*- coding: utf-8 -*-
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
def close_token(openToken):
    tokens.append(openToken)
    return None
def is_whitespace(text, index):
    if text[index] == ' ' or text[index] == '\n' or text[index] == '\t':
        return True
    else:
        return False
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
        assert(False,"Parsing error, character not expected")
    return tokenize(text, index + 1, openToken)

class SYMBOL_TYPES:
    FUNCTION_NAME = 0
heap = {}
symbolNames = {"print":SYMBOL_TYPES.FUNCTION_NAME}
expectedTokens = [[ENUM_TOKENS.IDENTIFIER, ENUM_TOKENS.LBRACE]]
def execute(index = 0):
    if index >= len(tokens):
        return
    

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
