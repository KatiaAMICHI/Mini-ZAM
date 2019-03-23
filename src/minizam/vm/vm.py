import re
from .instructions import *
import sys


class _Stack:

    def __init__(self):
        self.items = []

    def peek(self, i=0):
        """
              Renvoie le i-ième element de la queue
              :param i ith element in the queue
          """
        return self.items[i]

    def pop(self, n=0):
        """
           Renvoie et retire les n premier element de la queue
           :param n
       """
        if self.is_empty():
            return []
        elif n == 0:
            result = self.items[n]
            del self.items[n]
            return result
        else:
            result = self.items[:n]
            del self.items[:n]
        return result

    def push(self, elements):
        if not isinstance(elements, list):
            elements = [elements]

        self.items = elements + self.items

    def set_element(self, index, value):
        self.items[len(self.items) - index - 1] = value

    def is_empty(self):
        return self.items == []

    def size(self):
        return len(self.items)

    def __repr__(self):
        return "_Stack(items : %s )" % (self.items)


class LineInstruction:
    def __init__(self, label=None, command=None, args=None):
        self.label = label
        self.command = command
        self.args = args if args else []

    def __repr__(self):
        return "LineInstruction(Label : %s, Command : %s, args : %s)" % (self.label, self.command, self.args)

    def __str__(self):
        return "(Label : %s, Command : %s, args : %s)" % (self.label, self.command, self.args)

    @staticmethod
    def build(line):
        label = line[0] if line[0] else None
        command = line[1]
        args = line[2].replace(' ', '').split(",") if line[2] else []
        return LineInstruction(label, command, args)


class MiniZamVM:
    instructions = {"CONST": Const(), "PRIM": Prim(), "BRANCH": Branch(), "BRANCHIFNOT": BranchIfNot(),
                    "PUSH": Push(), "POP": Pop(), "ACC": Acc(), "ENVACC": EnvAcc(),
                    "CLOSURE": Closure(), "CLOSUREREC": ClosureRec(), "OFFSETCLOSURE": OffSetClosure(),
                    "RESTART": ReStart(), "GRAB": Grab(), "APPLY": Apply(), "MAKEBLOCK": MakeBlock(),
                    "GETFIELD": GetField(), "VECTLENGTH": VectLength(), "GETVECTITEM": GetVectItem(),
                    "SETFIELD": SetField(), "SETVECTITEM": SetVectItem(), "ASSIGN": Assign(),
                    "RETURN": Return(), "STOP": Stop()}

    def __init__(self):
        self.prog = []
        self.stack = _Stack()  # structure LIFO
        self.env = []  # un collection de mlvalue
        self.pc = 0  # pointeur de code vers l’instruction courante
        self.acc = MLValue.unit()
        self.current_args = []
        self.extra_args = 0  # le nombre d’arguments restant a appliquer à une fonction

    def get_bloc(self):
        return self.bloc

    def add_to_bloc(self, element):
        self.bloc.append(element)

    def get_stack(self):
        return self.stack

    def set_stack(self, index, value):
        return self.stack.set_element(index, value)

    def set_accumulator(self, acc):
        self.acc = acc

    def get_accumulator(self):
        return self.acc

    def get_extra_args(self):
        return self.extra_args

    def set_extra_args(self, extra_args):
        self.extra_args = extra_args

    def pop(self, n=0):
        return self.stack.pop(n)

    def push(self, elements):
        self.stack.push(elements)

    def peek(self, i=0):
        return self.stack.peek(i)

    def is_empty(self):
        return self.stack.is_empty()

    def set_pc(self, pc):
        self.pc = pc

    def increment_pc(self):
        pc = self.pc
        self.pc += 1
        if self.prog:
            self.current_args = self.prog[pc].args
        return pc

    def get_pc(self):
        return self.pc

    def get_env(self, i=None):
        if isinstance(i, int):
            return self.env[i]
        return self.env

    def set_env(self, env):
        self.env = env

    """
    def pop_env(self, n=0):
        # TODO a supp !
        result = self.env[n]
        del self.env[n]
        return result
    """

    def get_position(self, label):
        """

        :return: renvoie la position du label dans prog
        """
        inst = next(filter(lambda x: x.label == label, self.prog))

        return self.prog.index(inst)

    def change_context(self):
        """
        Change le context de pc et env à partir de la valeur de acc
        """

        self.pc = self.acc.value[0]
        self.env = self.acc.value[1]

    def fetch(self):
        """

        :return: renvoie les arguments de l'instruction courante
        """
        return self.current_args

    def print_current_state(self):
        print('          '
              '    -> pc=', self.pc, ' | accu=', self.acc,
              " | stack=", self.stack.items, " | env=", self.env, " <-")

    def run(self):
        while True:
            # print(self.prog[self.pc].command, 'pc =', self.pc)
            self.instructions[self.prog[self.increment_pc()].command].execute(self)
            print(self.prog[self.pc - 1].command + str(self.current_args))
            self.print_current_state()

    def shutdown(self):
        print("acc = ", self.acc)
        exit()

    def load_file(self, file):

        """
        read intruction of program and set self.prog
        :rtype: object
        """
        with open(file, "r") as f:
            lines = re.findall(r'(?:(\w+):)?\t(\w+)(.*)', f.read())
            self.prog = list(map(LineInstruction.build, lines))
