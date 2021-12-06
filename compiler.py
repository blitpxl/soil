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


def compile_file(file):
    with open(file) as src:
        src = src.readlines()
        _compiled = []
        for line in src:
            line = line.strip()
            if not line or line.startswith("#"):
                _compiled.append(["nop"])
            else:
                _compiled.append(split_line(line))

        __compiled = []
        for line in _compiled:
            __compiled.append([ln for ln in line if ln != ""])

    return __compiled
