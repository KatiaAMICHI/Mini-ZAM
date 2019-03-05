import numpy as np
from .mlvalue import MLValue
from .instructions import *
import re

FILE_facto_tailrec = r"tests/appterm/facto_tailrec.txt"


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
        result = self.items[:n]
        del self.items[:n]
        return result

    def push(self, elements):
        if not isinstance(elements, list):
            elements = [].append(elements)
            pass
        self.items = elements[::-1] + self.items

    def is_empty(self):
        return self.items == []

    def size(self):
        return len(self.items)


# TODO a line instruction is define by its label, instruction, arguments
class LineInstruction:

    @staticmethod
    def build(line):
        label = line[0] if line[0] else None
        command = line[1]
        args = line[2].split(",") if line[2] else None
        return LineInstruction(label, command, args)


class MiniZamVM:
    instructions = {"CONST": Acc(), "PRIM": Prim(), "BRANCH": Branch(), "BRANCHIFNOT": BranchIfNot(),
                    "PUSH": Push(), "POP": Pop(), "ACC": Acc(), "ENVACC": EnvAcc(),
                    "CLOSURE": Closure(), "APPLY": Apply(), "RETURN": Return(), "STOP": Stop()}

    def __init__(self):
        # TODO prog is an array of LineInstruction
        self.prog = np.array([], dtype=[('label', np.object),
                                        ('inst', np.object)])  # un tableau de couples (label, instruction)
        self.stack = _Stack()  # structure LIFO
        self.env = []  # un collection de mlvalue
        self.pc = 0  # pointeur de code vers l’instruction courante
        self.acc = MLValue.unit()

    def set_accumulator(self, acc):
        assert isinstance(acc, MLValue)
        self.acc = acc

    def get_accumulator(self):
        return self.acc

    def pop(self, n=0):
        return self.stack.pop(n)

    def push(self, elements):
        self.stack.push(elements)

    def peek(self, i):
        return self.stack.peek(i)

    def is_empty(self):
        return self.stack.is_empty()

    def set_pc(self, pc):
        self.pc = pc

    def get_pc(self):
        return self.pc

    def increment_pc(self):
        self.pc += 1

    def get_env(self, i=None):
        if i:
            assert i < len(self.env)
            return self.env[i]
        return self.env

    def get_position(self, label):
        # TODO
        pass

    def change_context(self, acc):
        self.pc = acc.value[0]
        self.env = acc.value[1]
        # TODO update pc and env, called by the Apply Instruction
        pass

    def fetch(self):
        # TODO return current (pc) instruction arguments
        pass

    def run(self):
        # TODO keep evaluating instruction respecting the pc register until encountering STOP
        pass

    # TODO replace by using re
    def read_file(self):
        """ !!  a changer d'emplacement
        read intruction of program and set self.prog
        :rtype: object
        """
        with open(FILE_facto_tailrec, "r") as f:
            lines = re.findall(r'(?:(\w+):)?\t(\w+)(.*)', f.read())
            self.prog = list(map(LineInstruction.build, lines))
