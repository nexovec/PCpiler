# -*- coding: utf-8 -*-
from os import lseek
import os
import inspect
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


BYTECODE_INSTRUCTIONS = {
    "ADD": 0,
    "MUL": 1,
    "CALL": 2,
    "STACK": 3
}


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

    def peekToken(self, offset: int = 1):
        return tokens[self.index + offset]

    def getTokenType(self):
        return tokens[self.index].token

    def getTokenData(self):
        return ''.join(tokens[self.index].data)

    def hasNext(self):
        if len(tokens) > self.index + 1:
            return True
        return False

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


def consumeArgsList(bp: BytecodeParser, argsList = None):
    # NOTE: must return bp.index of the next ',' or of ')'
    if argsList == None:
        # this means this is the first argument
        argsList = []
    if not [ENUM_TOKENS.LPAREN, ENUM_TOKENS.COMMA].__contains__(bp.getTokenType()):
        if bp.getTokenType() == ENUM_TOKENS.RPAREN:
            bp.nextToken()
            return True
        bp.unexpectedTokenError()
    if consumeRValue(bp.nextToken()) == False:
        error("Expected RValue!")
    consumeArgsList(bp)
    return True


stack = []
def inbuilt_print():
    params = stack[-1]
    def func(v):
        return str(v)
    print(''.join(map(func, params)))

inbuiltFunctions = {
    "print": inbuilt_print
}

def consumeFunctionCall(bp: BytecodeParser):
    if bp.getTokenType() != ENUM_TOKENS.IDENTIFIER or tokens[bp.index + 1].token != ENUM_TOKENS.LPAREN:
        return False
    functionName = ''.join(bp.getTokenData())
    print("running function " + functionName)
    # TODO: Add bytecode instruction here
    if functionName in inbuiltFunctions:
        stack.append([])
        args = consumeArgsList(bp.nextToken())
        inbuiltFunctions.get(functionName)()
        stack.pop()
    else:
        error("This function doesn't exist yet!")


    return True


def consumeVariableAssign(bp: BytecodeParser):
    tok = bp.peekToken()
    if tok.token != ENUM_TOKENS.OPERATOR or ''.join(tok.data) != "=":
        return False
    errNYI()

def consumeEmptyCodeLine(bp: BytecodeParser, isParenthesized: bool = False):
    if bp.hasNext() == False:
        return False
    if not isParenthesized and bp.getTokenType() == ENUM_TOKENS.ENDLINE:
        bp.nextToken()
        return True
    return False


def consumeRValue(bp: BytecodeParser, isParenthesized: bool = False, ):
    tokenType = bp.getTokenType()
    success = False
    if tokenType == ENUM_TOKENS.LPAREN:
        if not consumeRValue(bp.nextToken(), True):
            bp.unexpectedTokenError()
    if tokenType == ENUM_TOKENS.RPAREN:
        if not isParenthesized:
            bp.unexpectedTokenError()
        bp.nextToken()
        return True
    # if consumeVariableAssign(bp):
    #     return True
    if consumeFunctionCall(bp) == True:
        return True
    if bp.getTokenType() == ENUM_TOKENS.NUM_LITERAL:
        # print("Encountered number literal in rvlaue, great job!")
        stack[-1].append(bp.getTokenData())
        bp.nextToken()
        return True
    # TODO: String literals
    # TODO: Consider replacing all literals with an identifier
    return False

def consumeLValue(bp: BytecodeParser):
    tokenType = bp.getTokenType()
    if not bp.hasNext():
        return True
    # print("consuming LValue " + str(tokenType) + "!")
    # NOTE: These functions must return with index of the endline character(or right paren, if isParenthesized == True)
    # NOTE: These functions must return with index back if they're not supposed to parse.
    if consumeFunctionCall(bp):
        return True
    if consumeVariableAssign(bp):
        return True

    if not [ENUM_TOKENS.IDENTIFIER].__contains__(tokenType):
        bp.unexpectedTokenError()
    return False


# Returns whether it encountered some errors
def consumeModule(bp: BytecodeParser, fileName):
    bp.prevToken()
    while bp.hasNext():
        bp.nextToken()
        if not consumeLValue(bp):
            error("File " + fileName + "has not parsed successfully!")
    # TODO: better error logging - show expected tokens
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

def parseFile(fileName):
    text = None
    with open(os.path.abspath(fileName)) as f:
        text = f.readlines()
    tokenize('\n'.join(text))
    if tokens[tokens.__len__() - 1].token != ENUM_TOKENS.ENDLINE:
        tokens.append(Token(ENUM_TOKENS.ENDLINE))
    for _, v in enumerate(tokens):
        print(v, v.data)
    bp: BytecodeParser = BytecodeParser()
    consumeModule(bp, fileName)
    print("Successfully parsed " + fileName, flush=True)


def parseFilesAndDirectories(args, prefix = ""):
    for arg in args:
        fileOrDirName = prefix + arg
        if os.path.exists(fileOrDirName) == False:
            print(fileOrDirName)
            error("Invalid file path")
        if os.path.isdir(fileOrDirName):
            fileOrDirName += "/"
            print("Parsing a directory " + fileOrDirName)
            parseFilesAndDirectories(os.listdir(fileOrDirName), fileOrDirName)
        else:
            print("Trying to parse a file " + arg)
            parseFile(fileOrDirName)


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: python temp.py <filename>")
        return -1
    parseFilesAndDirectories(args)
    print()



if __name__ == "__main__":
    main()
