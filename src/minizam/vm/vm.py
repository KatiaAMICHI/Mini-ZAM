import pprint
import numpy as np
import re
from src.minizam.vm.instructions import *

FILE_facto_tailrec = r"../../../tests/appterm/facto_tailrec.txt"

FILE_fun1 = r"../../../tests/unary_funs/fun1.txt"

FILE_fun4 = r"../../../tests/unary_funs/fun4-nooptim.txt"


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
            return None
        elif n == 0:
            result = self.items[n]
            del self.items[n]
            return result
        result = self.items[:n]
        del self.items[:n]
        return result

    def push(self, elements):
        if not isinstance(elements, list):
            elements = [elements]
            pass
        self.items = elements + self.items

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
        self.args = args

    def get_label(self):
        return self.label

    def get_command(self):
        return self.command

    def get_args(self):
        return self.args

    def __repr__(self):
        return "LineInstruction(Label : %s, Command : %s, args : %s)" % (self.label, self.command, self.args)

    def __str__(self):
        return "(Label : %s, Command : %s, args : %s)" % (self.label, self.command, self.args)

    @staticmethod
    def build(line):
        label = line[0] if line[0] else None
        command = line[1]
        args = line[2].replace(' ', '').split(",") if line[2] else None
        return LineInstruction(label, command, args)


class MiniZamVM:
    instructions = {"CONST": Const(), "PRIM": Prim(), "BRANCH": Branch(), "BRANCHIFNOT": BranchIfNot(),
                    "PUSH": Push(), "POP": Pop(), "ACC": Acc(), "ENVACC": EnvAcc(),
                    "CLOSURE": Closure(), "CLOSUREREC": ClosureRec(), "OFFSETCLOSURE": OffSetClosure(),
                    "RESTART": ReStart(), "GRAB": Grab(), "APPLY": Apply(),
                    "RETURN": Return(), "STOP": Stop()}

    def __init__(self):
        self.prog = np.array([])
        self.stack = _Stack()  # structure LIFO
        self.env = []  # un collection de mlvalue
        self.pc = 0  # pointeur de code vers l’instruction courante
        self.acc = MLValue.unit()
        self.extra_args = 0  # le nombre d’arguments restant a appliquer à une fonction

    def set_accumulator(self, acc):
        assert isinstance(acc, MLValue)
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

    def peek(self, i):
        return self.stack.peek(i)

    def is_empty(self):
        return self.stack.is_empty()

    def set_pc(self, pc):
        self.pc = pc

    def increment_pc(self):
        self.pc += 1

    def get_pc(self):
        return self.pc

    def increment_pc(self):
        self.pc += 1

    def get_env(self, i=None):
        if i:
            assert i < len(self.env)
            return self.env[i]
        return self.env

    def set_env(self, env):
        self.env = env

    def pop_env(self, n=0):
        # TODO a supp !
        result = self.env[n]
        del self.env[n]
        return result

    def get_position(self, label):
        """

        :return: renvoie la position du label dans prog
        """

        return list(self.prog).index(list(filter(lambda x: x.get_label() == label, self.prog))[0])

    def change_context(self, acc):
        """
        Change le context de pc et env à partir de la valeur de acc
        """
        self.pc = acc.value[0]
        self.env = acc.value[1]

    def fetch(self):
        """

        :return: renvoie les arguments de l'instruction courante
        """
        return self.prog[self.pc].get_args()

    def print_current_state(self):
        print('                                           '
              '    -> pc=', self.pc, ' | accu=', self.acc,
              " | size(stack)=", self.stack, " | env=", self.env, " <<<")

    def run(self):
        while self.prog[self.pc].get_command() != 'STOP':
            print("Current instruction :", self.prog[self.pc])
            self.instructions[self.prog[self.pc].get_command()].execute(self)
            self.print_current_state()

    def read_file(self, file):
        """
        read intruction of program and set self.prog
        :rtype: object
        """
        with open(file, "r") as f:
            lines = re.findall(r'(?:(\w+):)?\t(\w+)(.*)', f.read())
            self.prog = list(map(LineInstruction.build, lines))


if __name__ == '__main__':
    miniZamVM = MiniZamVM()
    miniZamVM.read_file(FILE_fun1)
    # pprint.pprint(miniZamVM.prog)
    miniZamVM.run()
