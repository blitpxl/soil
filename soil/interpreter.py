import sys

from tokens import *
from compiler import compile_file

import os
import importlib


class Variable:
    def __init__(self, name, value):
        self.value = value
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var({self.name}, {self.value})"


class VirtualMachine:
    def __init__(self):
        super(VirtualMachine, self).__init__()
        self.bytecode = []          # the bytecode memory
        self.stack = []             # the stack memory
        self.bytecode_addr = 0      # current bytecode address, acts like a program counter

        self.script_path = None     # path of the currently running script, used for relative import
        self.ret_addrs = []         # stores the procedure return adressed

    def load_bytecode(self, compiled, path):
        self.script_path = os.path.split(path)[0]
        self.bytecode = compiled

    def init_eval_loop(self):
        try:
            self.bytecode_addr = self.bytecode.index([FUNCTION, "main"]) + 1
        except ValueError:
            pass
        while self.bytecode_addr < len(self.bytecode):
            self.eval_inst(*self.bytecode[self.bytecode_addr])

    def get_var(self, name):
        for obj in self.stack:
            if str(obj) == name:
                return obj.value
        raise RuntimeError(f"Could not find variable {name}")

    def _push(self, value, position=TOP):
        if position == TOP:
            self.stack.append(value)
        elif position == REPLACE:
            self.stack.pop()
            self.stack.append(value)
        elif position == BOTTOM:
            self.stack = [value] + self.stack
        else:
            raise RuntimeError(f"Cannot push value ({value}) onto the stack, invalid position: {position}")

    def push(self, _type, _value, position=TOP):
        if _type == VAR:
            value = self.get_var(_value)
            if value is not None:
                self._push(value, position)
        elif _type == STRING:
            self._push(str(_value), position)
        elif _type == INT:
            self._push(int(_value), position)
        elif _type == FLOAT:
            self._push(float(_value), position)
        elif _type == BOOL:
            if _value == TRUE:
                self._push(True)
            elif _value == FALSE:
                self._push(False)
            else:
                raise RuntimeError(f"{_value} is not a bool")
        else:
            raise RuntimeError(f"Invalid data type: {_type}")

    def pop(self, elements=1):
        self.stack.pop(-int(elements))

    def load(self, _type, _value):
        if _type == VAR:
            value = self.get_var(_value)
            if value is not None:
                self._push(value)
        elif _type == STRING:
            self._push(str(_value))
        elif _type == INT:
            self._push(int(_value))
        elif _type == FLOAT:
            self._push(float(_value))
        elif _type == BOOL:
            if _value == TRUE:
                self._push(True)
            elif _value == FALSE:
                self._push(False)
            else:
                raise RuntimeError(f"{_value} is not a bool")
        else:
            raise RuntimeError(f"Invalid data type: {_type}")

    def spawn(self, _type):
        if _type == VAR:
            self._push(Variable(self.stack.pop(), self.stack.pop()))
        elif _type == UNITIALIZED_VAR:
            self._push(Variable(self.stack.pop(), None))
        else:
            raise RuntimeError(f"Invalid spawn type: {_type}")

    def delete(self, _type, name):
        if _type == VAR:
            for obj in self.stack:
                if str(obj) == name:
                    self.stack.remove(obj)
        else:
            raise RuntimeError(f"Invalid delete type: {_type}")

    def assign(self, name):
        for obj in self.stack:
            if str(obj) == name:
                obj.value = self.stack.pop()

    def print(self, *args):
        if len(args) < 2:
            if args[0] == STACK_MEM:
                print(self.stack)
            elif args[0] == BYTECODE:
                for inst in self.bytecode:
                    print(inst)
            elif args[0] == STACK_TOP:
                try:
                    print(self.stack[-1])
                except IndexError:
                    print("Stack is empty")
            else:
                print(*args)
        else:
            _type = args[0]
            value = args[1]
            if _type == VAR:
                print(self.get_var(value))
            else:
                raise RuntimeError(f"Invalid type: {_type}")

    def jump(self, labelname):
        self.bytecode_addr = self.bytecode.index([LABEL, labelname])

    def jumpt(self, labelname):
        if self.stack.pop():
            self.bytecode_addr = self.bytecode.index([LABEL, labelname])

    def jumpf(self, labelname):
        if not self.stack.pop():
            self.bytecode_addr = self.bytecode.index([LABEL, labelname])

    def comp(self, operator=None):
        if operator is None:
            if self.stack[-1] == self.stack[-2]:
                self._push(True)
            else:
                self._push(False)
        else:
            if operator == AND:
                if self.stack[-1] and self.stack[-2]:
                    self._push(True)
                else:
                    self._push(False)
            elif operator == OR:
                if self.stack[-1] or self.stack[-2]:
                    self._push(True)
                else:
                    self._push(False)
            elif operator == NOT:
                if not (self.stack[-1] == self.stack[-2]):
                    self._push(True)
                else:
                    self._push(False)
            elif operator == NAND:
                if not (self.stack[-1] and self.stack[-2]):
                    self._push(True)
                else:
                    self._push(False)
            elif operator == NOR:
                if not (self.stack[-1] or self.stack[-2]):
                    self._push(True)
                else:
                    self._push(False)
            elif operator == GREATER_THAN:
                if self.stack[-1] > self.stack[-2]:
                    self._push(True)
                else:
                    self._push(False)
            elif operator == GREATER_THAN_OR_EQUAL:
                if self.stack[-1] >= self.stack[-2]:
                    self._push(True)
                else:
                    self._push(False)
            elif operator == LESS_THAN:
                if self.stack[-1] < self.stack[-2]:
                    self._push(True)
                else:
                    self._push(False)
            elif operator == LESS_THAN_OR_EQUAL:
                if self.stack[-1] <= self.stack[-2]:
                    self._push(True)
                else:
                    self._push(False)
            else:
                raise RuntimeError(f"Invalid comparison modifier: {operator}")

    def sl_import(self, name):
        compiled = compile_file(f"{self.script_path}/{name}.sl")
        self.bytecode.pop(self.bytecode.index([SOIL_IMPORT, name]))
        self.bytecode = compiled + self.bytecode
        self.bytecode_addr = self.bytecode_addr - 1

    def py_import(self, name):
        mod = importlib.import_module(name)
        self._push(mod)

    def get_attr(self, name):
        self._push(getattr(self.stack.pop(), name))

    def pycall(self, *args):
        callargs = []
        for idx, arg in enumerate(args):
            if (idx % 2) == 0:
                if arg == VAR:
                    callargs.append(self.get_var(args[idx + 1]))
                elif arg == STRING:
                    callargs.append(str(args[idx + 1]))
                elif arg == INT:
                    callargs.append(int(args[idx + 1]))
                elif arg == FLOAT:
                    callargs.append(float(args[idx + 1]))
                elif arg == BOOL:
                    callargs.append(bool(args[idx + 1]))
        _callable = self.stack.pop()
        retval = _callable(*callargs)
        if retval is not None:
            self._push(retval)

    def add(self, mode):
        if mode == INPLACE:
            self._push(self.stack.pop() + self.stack.pop())
        elif mode == ADJACENT:
            self._push(self.stack[-1] + self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def sub(self, mode):
        if mode == INPLACE:
            self._push(self.stack.pop() - self.stack.pop())
        elif mode == ADJACENT:
            self._push(self.stack[-1] - self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def mul(self, mode):
        if mode == INPLACE:
            self._push(self.stack.pop() * self.stack.pop())
        elif mode == ADJACENT:
            self._push(self.stack[-1] * self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def div(self, mode):
        if mode == INPLACE:
            self._push(self.stack.pop() / self.stack.pop())
        elif mode == ADJACENT:
            self._push(self.stack[-1] / self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def mod(self, mode):
        if mode == INPLACE:
            self._push(self.stack.pop() % self.stack.pop())
        elif mode == ADJACENT:
            self._push(self.stack[-1] % self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def proc_def(self):
        current_bytecode_addr = self.bytecode_addr
        while 1:
            if self.bytecode[current_bytecode_addr][0] == RETURN:
                break
            else:
                current_bytecode_addr += 1
        self.bytecode_addr = current_bytecode_addr

    def call(self, function_name):
        self.ret_addrs.append(self.bytecode_addr)
        self.bytecode_addr = self.bytecode.index([FUNCTION, function_name])

    def ret(self):
        try:
            self.bytecode_addr = self.ret_addrs.pop()
        except IndexError:
            sys.exit(0)

    def prompt(self, message):
        self._push(input(message))

    def cast(self, _type):
        if _type == STRING:
            self._push(str(self.stack.pop()))
        elif _type == INT:
            self._push(int(self.stack.pop()))
        elif _type == FLOAT:
            self._push(float(self.stack.pop()))
        elif _type == BOOL:
            self._push(bool(self.stack.pop()))

    def eval_inst(self, opcode, *args):

        if opcode == NOP or opcode == LABEL:
            pass
        elif opcode == FUNCTION:
            self.proc_def()
        elif opcode == RETURN:
            self.ret()
        elif opcode == LOAD:
            self.load(*args)
        elif opcode == SPAWN:
            self.spawn(*args)
        elif opcode == DELETE:
            self.delete(*args)
        elif opcode == ASSIGN:
            self.assign(*args)
        elif opcode == PRINT:
            self.print(*args)
        elif opcode == JUMP:
            self.jump(*args)
        elif opcode == JUMP_IF_TRUE:
            self.jumpt(*args)
        elif opcode == JUMP_IF_FALSE:
            self.jumpf(*args)
        elif opcode == SOIL_IMPORT:
            self.sl_import(*args)
        elif opcode == PYTHON_IMPORT:
            self.py_import(*args)
        elif opcode == GETATTR:
            self.get_attr(*args)
        elif opcode == PYTHON_CALL:
            self.pycall(*args)
        elif opcode == CALL:
            self.call(*args)
        elif opcode == PUSH:
            self.push(*args)
        elif opcode == POP:
            self.pop(*args)
        elif opcode == ADD:
            self.add(*args)
        elif opcode == SUB:
            self.sub(*args)
        elif opcode == MUL:
            self.mul(*args)
        elif opcode == DIV:
            self.div(*args)
        elif opcode == MOD:
            self.mod(*args)
        elif opcode == COMP:
            self.comp(*args)
        elif opcode == PROMPT:
            self.prompt(*args)
        elif opcode == CAST:
            self.cast(*args)
        else:
            raise RuntimeError(f"Invalid opcode: {opcode}")

        self.bytecode_addr += 1
