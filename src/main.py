# -*- coding: utf-8 -*-
from os import lseek
import os
import inspect
import sys
import uuid

lastEndlIndex = 0
currentRow = 1
file_name: str = None


opList = ['=', '+', '-', '*', '/']


tokens = []
stack = []


def inbuilt_print():
    params = stack[-1]

    def func(v):
        return str(v)
    print(''.join(map(func, params)))


inbuiltFunctions = {
    "print": inbuilt_print
}


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


def error(msg, level=1):
    assert (level >= 1)
    frame = inspect.currentframe()
    outerframe = inspect.getouterframes(frame, 2)
    print(msg + "\n" + str(outerframe[level][1]) + ":" +
          str(outerframe[level][2]))
    print("", flush=True)
    exit(-1)


def err_NYI():
    error("Not yet implemented.", 2)


def is_whitespace(text, index):
    if text[index] == ' ' or text[index] == '\n' or text[index] == '\t':
        return True
    else:
        return False


def close_token(openToken):
    tokens.append(openToken)
    return None


def open_new_token(char: str):
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
        openToken = open_new_token(char)
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


def has_this_token(index):
    if index < len(tokens):
        return True
    else:
        return False


def has_next_token(index):
    if index + 1 < len(tokens):
        return True
    else:
        return False


def has_next_n_tokens(index, n):
    if index + n < len(tokens):
        return True
    else:
        return False


def is_value_token(index):
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
    __slots__ = ('index', 'bytecode')

    def __init__(self):
        self.index = 0
        self.bytecode = []

    def next_token(self):
        self.index += 1
        return self

    def prev_token(self):
        self.index -= 1
        return self

    def peekToken(self, offset: int = 1):
        return tokens[self.index + offset]

    def get_token_type(self):
        return tokens[self.index].token

    def get_token_data(self):
        return ''.join(tokens[self.index].data)

    def has_next(self):
        if len(tokens) > self.index + 1:
            return True
        return False

    def unexpected_token_error(self):
        # TODO: print line number
        print(self.get_token_type())
        token_type = self.get_token_type()
        temp_row = str(tokens[self.index].row)
        temp_col = str(tokens[self.index].col)
        assert token_type
        assert temp_row
        assert temp_col
        assert file_name
        error(
            "Unexpected token " + token_type + " at " +
            file_name + ":" + temp_row + ":" +
            temp_col, 2)


def get_preceding_operator(a, b):
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


def consume_num_literal(bp: BytecodeParser):
    if bp.get_token_type() != ENUM_TOKENS.NUM_LITERAL:
        return bp, None, False
    data = bp.get_token_data()
    return bp.next_token(), data, True


def consume_args_list(bp: BytecodeParser, argsList=None):
    # NOTE: must return bp.index of the next ',' or of ')'
    assert file_name
    if argsList == None:
        # this means this is the first argument
        argsList = []
    if not [ENUM_TOKENS.LPAREN, ENUM_TOKENS.COMMA].__contains__(bp.get_token_type()):
        if bp.get_token_type() == ENUM_TOKENS.RPAREN:
            bp.next_token()
            return True
        bp.unexpected_token_error()
    if consume_rvalue(bp.next_token()) == False:
        error("Expected RValue!")
    consume_args_list(bp)
    return True


def consume_function_call(bp: BytecodeParser):
    if bp.get_token_type() != ENUM_TOKENS.IDENTIFIER or tokens[bp.index + 1].token != ENUM_TOKENS.LPAREN:
        return False
    function_name = ''.join(bp.get_token_data())
    print("running function " + function_name)
    # TODO: Add bytecode instruction here
    if function_name in inbuiltFunctions:
        stack.append([])
        args = consume_args_list(bp.next_token())
        inbuiltFunctions.get(function_name)()
        stack.pop()
    else:
        error("This function doesn't exist yet!")

    return True


def consume_variable_assign(bp: BytecodeParser):
    varName = ''.join(bp.get_token_data())
    varTokType = bp.get_token_type()
    tokType = bp.next_token().get_token_type()
    tokData = bp.get_token_data()
    if varTokType != ENUM_TOKENS.IDENTIFIER or tokType != ENUM_TOKENS.OPERATOR or ''.join(tokData) != "=":
        return False

    # TODO: Module scoped stack frame
    print("Assigning a variable " + varName)
    if consume_rvalue(bp.next_token()) == False:
        error("Expected valid RValue!")
    return True


def consumeEmptyCodeLine(bp: BytecodeParser, isParenthesized: bool = False):
    if bp.has_next() == False:
        return False
    if not isParenthesized and bp.get_token_type() == ENUM_TOKENS.ENDLINE:
        bp.next_token()
        return True
    return False


def consume_rvalue(bp: BytecodeParser, isParenthesized: bool = False, ):
    assert file_name
    tokenType = bp.get_token_type()
    success = False
    if tokenType == ENUM_TOKENS.LPAREN:
        if not consume_rvalue(bp.next_token(), True):
            bp.unexpected_token_error()
    if tokenType == ENUM_TOKENS.RPAREN:
        if not isParenthesized:
            bp.unexpected_token_error()
        bp.next_token()
        return True
    # if consumeVariableAssign(bp):
    #     return True
    if consume_function_call(bp) == True:
        return True
    if bp.get_token_type() == ENUM_TOKENS.NUM_LITERAL:
        # print("Encountered number literal in rvlaue, great job!")
        stack[-1].append(bp.get_token_data())
        bp.next_token()
        return True
    # TODO: String literals
    # TODO: Consider replacing all literals with an identifier
    return False


def consume_lvalue(bp: BytecodeParser):
    assert file_name
    tokenType = bp.get_token_type()
    if not bp.has_next():
        return True
    # print("consuming LValue " + str(tokenType) + "!")
    # NOTE: These functions must return with index of the endline character(or right paren, if isParenthesized == True)
    # NOTE: These functions must return with index back if they're not supposed to parse.
    if not [ENUM_TOKENS.IDENTIFIER].__contains__(tokenType):
        bp.unexpected_token_error()
    if consume_function_call(bp):
        return True
    elif consume_variable_assign(bp):
        return True

    return False


# Returns whether it encountered some errors
def consume_module(bp: BytecodeParser):
    assert file_name
    stack.append([])
    bp.prev_token()
    while bp.has_next():
        bp.next_token()
        if not consume_lvalue(bp):
            error("File " + file_name + "has not parsed successfully!")
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


def reset_mem():
    stack.clear()
    tokens.clear()


def parse_file(f_path):
    file_name = str(f_path)
    text = None
    with open(os.path.abspath(f_path)) as f:
        text = f.readlines()
    reset_mem()
    tokenize('\n'.join(text))
    if tokens[tokens.__len__() - 1].token != ENUM_TOKENS.ENDLINE:
        tokens.append(Token(ENUM_TOKENS.ENDLINE))
    for _, v in enumerate(tokens):
        print(v, v.data)
    bp: BytecodeParser = BytecodeParser()
    assert file_name
    consume_module(bp)
    print("Successfully parsed " + file_name, flush=True)


def parse_files_and_directories(args, prefix=""):
    for arg in args:
        file_or_dir_name = prefix + arg
        if os.path.exists(file_or_dir_name) == False:
            print(file_or_dir_name)
            error("Invalid file path")
        if os.path.isdir(file_or_dir_name):
            file_or_dir_name += "/"
            print("Parsing a directory " + file_or_dir_name)
            parse_files_and_directories(os.listdir(
                file_or_dir_name), file_or_dir_name)
        else:
            print("Trying to parse a file " + arg)
            parse_file(file_or_dir_name)


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: python temp.py <filename>")
        return -1
    parse_files_and_directories(args)
    print()


if __name__ == "__main__":
    main()
