from tokens import *


def split_line(string):
    result = []
    idx = 0
    str_start = None
    look_for_spaces = True
    start_idx = 0

    for char in string:
        if char == " " and look_for_spaces:
            result.append(string[start_idx:idx])
            start_idx = idx + 1
        elif char == "#" and look_for_spaces:
            break
        elif char == '"':
            look_for_spaces = False
            if str_start is None:
                str_start = idx + 1
            else:
                str_end = idx
                result.append(string[str_start:str_end])
                start_idx = idx + 2
                look_for_spaces = True
                str_start = None

        if idx == len(string) - 1:
            result.append(string[start_idx:])

        idx += 1
    return [token for token in result if token != ""]


def tokenize_line(splitted_line):
    tokenized_line = []
    for token in splitted_line:
        if token == "add":
            tokenized_line.append(ADD)
        elif token == "assign":
            tokenized_line.append(ASSIGN)
        elif token == "call":
            tokenized_line.append(CALL)
        elif token == "comp":
            tokenized_line.append(COMP)
        elif token == "div":
            tokenized_line.append(DIV)
        elif token == "getattr":
            tokenized_line.append(GETATTR)
        elif token == "import":
            tokenized_line.append(IMPORT)
        elif token == "jump":
            tokenized_line.append(JUMP)
        elif token == "label":
            tokenized_line.append(LABEL)
        elif token == "load":
            tokenized_line.append(LOAD)
        elif token == "mod":
            tokenized_line.append(MOD)
        elif token == "mul":
            tokenized_line.append(MUL)
        elif token == "nop":
            tokenized_line.append(NOP)
        elif token == "pop":
            tokenized_line.append(POP)
        elif token == "print":
            tokenized_line.append(PRINT)
        elif token == "push":
            tokenized_line.append(PUSH)
        elif token == "spawn":
            tokenized_line.append(SPAWN)
        elif token == "sub":
            tokenized_line.append(SUB)
        elif token == "adjacent":
            tokenized_line.append(ADJACENT)
        elif token == "bool":
            tokenized_line.append(BOOL)
        elif token == "bottom":
            tokenized_line.append(BOTTOM)
        elif token == "float":
            tokenized_line.append(FLOAT)
        elif token == "inplace":
            tokenized_line.append(INPLACE)
        elif token == "int":
            tokenized_line.append(INT)
        elif token == "py":
            tokenized_line.append(PY)
        elif token == "replace":
            tokenized_line.append(REPLACE)
        elif token == "string":
            tokenized_line.append(STRING)
        elif token == "top":
            tokenized_line.append(TOP)
        elif token == "var":
            tokenized_line.append(VAR)
        elif token == "!":
            tokenized_line.append(NOT)
        elif token == "&":
            tokenized_line.append(AND)
        elif token == "|":
            tokenized_line.append(OR)
        elif token == "false":
            tokenized_line.append(FALSE)
        elif token == "true":
            tokenized_line.append(TRUE)
        elif token == "__src":
            tokenized_line.append(SOURCE_MEM)
        elif token == "__stack":
            tokenized_line.append(STACK_MEM)
        elif token == "__top":
            tokenized_line.append(STACK_TOP)
        else:
            tokenized_line.append(token)

    return tokenized_line


def compile_file(file):
    with open(file) as src:
        src = src.readlines()
        _compiled = []
        for line in src:
            line = line.strip()
            if not line or line.startswith("#"):
                _compiled.append([NOP])
            else:
                splitted_line = split_line(line)
                tokenized_line = tokenize_line(splitted_line)
                _compiled.append(tokenized_line)

        __compiled = []
        for line in _compiled:
            __compiled.append([ln for ln in line if ln != ""])

    return __compiled
