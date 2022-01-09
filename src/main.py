# -*- coding: utf-8 -*-
from os import lseek
import os.path
import inspect
"""
Spyder Editor

This is a temporary script file.
"""
import sys
import uuid

lastEndlIndex = 0
currentRow = 1
filename: str = None


class Token:
    index = 0

    def __init__(self, token, data=None):
        self.token: ENUM_TOKENS = token
        self.data = data or []
        self.row = currentRow
        self.col = Token.index - lastEndlIndex + 1

    def __str__(self):
        return self.token

    def __repr__(self):
        return self.token


class ENUM_TOKENS:
    ENDLINE = "ENDLINE"
    IDENTIFIER = "IDENTIFIER"
    NUM_LITERAL = "NUM_LITERAL"
    STR_LITERAL = "STR_LITERAL"
    COLON = "COLON"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    OPERATOR = "OPERATOR"
    COMMA = "COMMA"


tokens = []
opList = ['=', '+', '-', '*', '/']


def error(msg, level=1):
    assert (level >= 1)
    frame = inspect.currentframe()
    outerframe = inspect.getouterframes(frame, 2)
    print(msg + "\n" + str(outerframe[level][1]) + ":" +
          str(outerframe[level][2]))
    print("", flush=True)
    exit(-1)


def errNYI():
    error("Not yet implemented.", 2)


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
        # TODO: make sure numbers are followed by whitespace
    elif char == '\"':
        openToken = Token(ENUM_TOKENS.STR_LITERAL)
        # TODO: make sure string literals are followed by whitespace
    elif char == '(':
        openToken = Token(ENUM_TOKENS.LPAREN)
    elif char == ')':
        openToken = Token(ENUM_TOKENS.RPAREN)
    elif char == '{':
        openToken = Token(ENUM_TOKENS.LBRACE)
    elif char == '}':
        openToken = Token(ENUM_TOKENS.RBRACE)
    elif char == ',':
        openToken = Token(ENUM_TOKENS.COMMA)
    elif char == ':':
        openToken = Token(ENUM_TOKENS.COLON)
    elif opList.__contains__(char):
        openToken = Token(ENUM_TOKENS.OPERATOR)
    return openToken


def tokenize(text, index=0, openToken=None):
    # FIXME: repeating newlines when parsing
    if index >= len(text):
        return
    char = text[index]
    if openToken == None:
        Token.index = index
        openToken = openNewToken(char)
        if openToken == None:
            return tokenize(text, index + 1, None)
        else:
            tokens.append(openToken)
    tok = openToken.token
    ts = ENUM_TOKENS
    if tok == ts.ENDLINE:
        global currentRow
        currentRow += 1
        lastEndlIndex = index
        return tokenize(text, index + 2, None)
    elif tok == ts.COLON:
        openToken = None
    elif tok == ts.IDENTIFIER:
        if char.isalpha() or char.isdigit():
            openToken.data.append(char)
        else:
            return tokenize(text, index, None)
    elif tok == ts.STR_LITERAL:
        if char == '\"':
            if openToken.data.__len__() != 0:
                openToken = None
        else:
            openToken.data.append(char)
    elif tok == ts.NUM_LITERAL:
        if char.isdigit():
            openToken.data.append(char)
        else:
            return tokenize(text, index, None)
    elif tok == ts.OPERATOR:
        if opList.__contains__(char):
            openToken.data.append(char)
        else:
            openToken = None
    elif [ts.LBRACE, ts.RBRACE, ts.LPAREN, ts.RPAREN,
          ts.COMMA].__contains__(tok):
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
    if tokens[index].token == ENUM_TOKENS.STR_LITERAL or tokens[
            index].token == ENUM_TOKENS.NUM_LITERAL or tokens[
                index].token == ENUM_TOKENS.IDENTIFIER:
        return True
    else:
        return False


class INSTRUCTION_BLOCK:
    ADD = "ADD"
    MUL = "MUL"
    CALL = "CALL"


class BytecodeParser:
    __slots__ = ('index', 'bytecode', 'identifiers')

    def __init__(self):
        self.index = 0
        self.bytecode = []
        self.identifiers = []

    def nextToken(self):
        self.index += 1
        return self

    def prevToken(self):
        self.index -= 1
        return self

    def getTokenType(self):
        return tokens[self.index].token

    def getTokenData(self):
        return ''.join(tokens[self.index].data)

    def hasNext(self):
        if len(tokens) >= self.index: return False
        return True

    def unexpectedTokenError(self):
        # TODO: print line number
        error(
            "Unexpected token " + str(self.getTokenType()) + " at " +
            filename + ":" + str(tokens[self.index].row) + ":" +
            str(tokens[self.index].col), 2)


def getPrecedingOperator(a, b):
    # TODO: test
    assert (a.token == ENUM_TOKENS.OPERATOR)
    assert (b.token == ENUM_TOKENS.OPERATOR)
    adata = ''.join(a.data)
    bdata = ''.join(b.data)
    precedence = ["++", "*", "+", "=", "=="]
    if precedence.index(adata) > precedence.index(bdata):
        return bdata
    else:
        return adata


def consumeNumLiteral(bp: BytecodeParser):
    if bp.getTokenType() != ENUM_TOKENS.NUM_LITERAL:
        return bp, None, False
    data = bp.getTokenData()
    return bp.nextToken(), data, True


def consumeArgsList(bp: BytecodeParser):
    # NOTE: must return bp.index of the next ',' or of ')'

    if not [ENUM_TOKENS.LPAREN, ENUM_TOKENS.COMMA].__contains__(bp.getTokenType()):
        if bp.getTokenType() == ENUM_TOKENS.RPAREN:
            return bp.nextToken()
        bp.unexpectedTokenError()
    print("Hello")
    bp, literal, success = consumeNumLiteral(bp.nextToken())
    if success:
        consumeArgsList(bp)
    # TODO: consider replacing all string literals with an identifier
    # TODO: consumeStringLiteral, consumeIdentifierArg
    return


def consumeFunctionCall(bp: BytecodeParser):
    if tokens[bp.index + 1].token != ENUM_TOKENS.LPAREN:
        return bp
    args = consumeArgsList(bp.nextToken())
    return bp


def consumeVariableAssign(bp: BytecodeParser):
    tokObj = tokens[bp.index + 1]
    if tokObj.token != ENUM_TOKENS.OPERATOR or ''.join(tokObj.data) != "=":
        return bp
    errNYI()


def consumeVariableExpression(bp: BytecodeParser):
    # TODO: unary operators need to be supported
    oldindex = bp.index
    bp = consumeVariableAssign(bp)
    if oldindex == bp.index:
        error("This is meaningless code")
    return bp


def consumeEmptyExpression(bp: BytecodeParser, isParenthesized):
    if not isParenthesized and tokens[bp.index + 1].token == ENUM_TOKENS.ENDLINE:
        return bp.nextToken()
    return bp


def consumeExpression(bp: BytecodeParser, isParenthesized=False):
    tokenType = tokens[bp.index].token
    print("parsing token " + tokenType)
    if not bp.hasNext():
        return bp
    if tokenType == ENUM_TOKENS.LPAREN:
        consumeExpression(bp.nextToken(), True)
    elif tokenType == ENUM_TOKENS.IDENTIFIER:
        # NOTE: These functions must return the index of the endline character(or right paren, if isParenthesized == True)
        # NOTE: These functions must return index back if they're not supposed to parse
        bp = consumeFunctionCall(bp)
        bp = consumeVariableExpression(bp)
        bp = consumeEmptyExpression(bp)
    else:
        bp.unexpectedTokenError()
    return consumeEmptyExpression(bp.nextToken(), isParenthesized)


def consumeTokens(i=0):
    result = consumeExpression(BytecodeParser())
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
    global filename
    filename = args.pop()
    print("Parsing " + filename)

    text = None
    with open(os.path.abspath(filename)) as f:
        text = f.readlines()
    tokenize('\n'.join(text))
    if tokens[tokens.__len__() - 1].token != ENUM_TOKENS.ENDLINE:
        tokens.append(Token(ENUM_TOKENS.ENDLINE))
    for _, v in enumerate(tokens):
        print(v, v.data)
    print()
    consumeTokens()
    print("hello", flush=True)
    pass


if __name__ == "__main__":
    main()
