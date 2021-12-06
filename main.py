from compiler import compile_file
from interpreter import VirtualMachine
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise RuntimeError("Not enough argument to start the compiler")
    else:
        compiled = compile_file(sys.argv[1])
        vm = VirtualMachine()
        vm.load_compiled(compiled)
        vm.init_eval_loop()
