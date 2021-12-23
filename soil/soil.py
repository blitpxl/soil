import os.path

from compiler import compile_file
from interpreter import VirtualMachine
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise RuntimeError("Not enough argument to start the compiler")
    else:
        if sys.argv[1] == "--version":
            print("0.2.0-dev")
        else:
            compiled = compile_file(sys.argv[1])
            vm = VirtualMachine()
            vm.load_bytecode(compiled, path=os.path.abspath(sys.argv[1]))
            vm.init_eval_loop()
