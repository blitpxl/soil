import importlib


class Variable:
    def __init__(self, name, value):
        self.value = value
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var({self.value}, {self.name})"


class VirtualMachine:
    def __init__(self):
        super(VirtualMachine, self).__init__()
        self.src = []       # the code memory
        self.stack = []     # the stack memory
        self.pc = 0         # program counter

    def load_compiled(self, compiled):
        self.src = compiled

    def init_eval_loop(self):
        while self.pc < len(self.src):
            self.eval_inst(*self.src[self.pc])

    def get_var(self, name):
        for obj in self.stack:
            if str(obj) == name:
                return obj.value
        raise RuntimeError(f"Could not find variable {name}")

    def _push(self, value, position="top"):
        if position == "top":
            self.stack.append(value)
        elif position == "replace":
            self.stack.pop()
            self.stack.append(value)
        elif position == "bottom":
            self.stack = [value] + self.stack
        else:
            raise RuntimeError(f"Cannot push value ({value}) onto the stack, invalid position: {position}")

    def push(self, _type, _value, position="top"):
        if _type == "var":
            value = self.get_var(_value)
            if value is not None:
                self._push(value, position)
        elif _type == "string":
            self._push(str(_value), position)
        elif _type == "int":
            self._push(int(_value), position)
        elif _type == "float":
            self._push(float(_value), position)
        elif _type == "bool":
            self._push(bool(_value), position)
        else:
            raise RuntimeError(f"Invalid data type: {_type}")

    def pop(self, elements=1):
        self.stack.pop(-elements)

    def load(self, _type, _value):
        if _type == "var":
            value = self.get_var(_value)
            if value is not None:
                self._push(value)
        elif _type == "string":
            self._push(str(_value))
        elif _type == "int":
            self._push(int(_value))
        elif _type == "float":
            self._push(float(_value))
        elif _type == "bool":
            self._push(bool(_value))
        else:
            raise RuntimeError(f"Invalid data type: {_type}")

    def spawn(self, _type):
        if _type == "var":
            self._push(Variable(self.stack.pop(), self.stack.pop()))
        else:
            raise RuntimeError(f"Invalid spawn type: {_type}")

    def assign(self, name):
        for obj in self.stack:
            if str(obj) == name:
                obj.value = self.stack.pop()

    def print(self, *args):
        if len(args) < 2:
            if args[0] == "__stack":
                print(self.stack)
            elif args[0] == "__src":
                for inst in self.src:
                    print(inst)
            elif args[0] == "__top":
                try:
                    print(self.stack[-1])
                except IndexError:
                    print("Stack is empty")
            else:
                print(*args)
        else:
            _type = args[0]
            value = args[1]
            if _type == "var":
                print(self.get_var(value))
            else:
                raise RuntimeError(f"Invalid type: {_type}")

    def jump(self, label):
        self.pc = self.src.index(["label", label])

    def import_(self, _type, name):
        if _type == "py":
            mod = importlib.import_module(name)
            self._push(mod)

    def get_attr(self, name):
        self._push(getattr(self.stack.pop(), name))

    def call(self, *args):
        callargs = []
        for idx, arg in enumerate(args):
            if (idx % 2) == 0:
                if arg == "var":
                    callargs.append(self.get_var(args[idx + 1]))
                elif arg == "string":
                    callargs.append(str(args[idx + 1]))
                elif arg == "int":
                    callargs.append(int(args[idx + 1]))
                elif arg == "float":
                    callargs.append(float(args[idx + 1]))
                elif arg == "bool":
                    callargs.append(bool(args[idx + 1]))
        _callable = self.stack.pop()
        retval = _callable(*callargs)
        if retval is not None:
            self._push(retval)

    def add(self, mode):
        if mode == "inplace":
            self._push(self.stack.pop() + self.stack.pop())
        elif mode == "adjacent":
            self._push(self.stack[-1] + self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def sub(self, mode):
        if mode == "inplace":
            self._push(self.stack.pop() - self.stack.pop())
        elif mode == "adjacent":
            self._push(self.stack[-1] - self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def mul(self, mode):
        if mode == "inplace":
            self._push(self.stack.pop() * self.stack.pop())
        elif mode == "adjacent":
            self._push(self.stack[-1] * self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def div(self, mode):
        if mode == "inplace":
            self._push(self.stack.pop() / self.stack.pop())
        elif mode == "adjacent":
            self._push(self.stack[-1] / self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def mod(self, mode):
        if mode == "inplace":
            self._push(self.stack.pop() % self.stack.pop())
        elif mode == "adjacent":
            self._push(self.stack[-1] % self.stack[-2])
        else:
            raise RuntimeError(f"Invalid add operation mode: {mode}")

    def eval_inst(self, opcode, *args):

        if opcode == "nop" or opcode == "label":
            pass
        elif opcode == "load":
            self.load(*args)
        elif opcode == "spawn":
            self.spawn(*args)
        elif opcode == "assign":
            self.assign(*args)
        elif opcode == "print":
            self.print(*args)
        elif opcode == "jump":
            self.jump(*args)
        elif opcode == "import":
            self.import_(*args)
        elif opcode == "getattr":
            self.get_attr(*args)
        elif opcode == "call":
            self.call(*args)
        elif opcode == "push":
            self.push(*args)
        elif opcode == "pop":
            self.pop(*args)
        elif opcode == "add":
            self.add(*args)
        elif opcode == "sub":
            self.sub(*args)
        elif opcode == "mul":
            self.mul(*args)
        elif opcode == "div":
            self.div(*args)
        elif opcode == "mod":
            self.mod(*args)
        else:
            raise RuntimeError(f"Invalid opcode: {opcode}")

        self.pc += 1
