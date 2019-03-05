import numpy as np
from src.minizam.vm.instructions import *

FILE_facto_tailrec = r"../../../tests/appterm/facto_tailrec.txt"
FILE_fun1 = r"../../../tests/unary_funs/fun1.txt"


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


class MiniZamVM:
    instructions = {"CONST": Acc(), "PRIM": Prim(), "BRANCH": Branch(), "BRANCHIFNOT": BranchIfNot(),
                    "PUSH": Push(), "POP": Pop(), "ACC": Acc(), "ENVACC": EnvAcc(),
                    "CLOSURE": Closure(), "APPLY": Apply(), "RETURN": Return(), "STOP": Stop()}

    def __init__(self):
        self.prog = np.array([])
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
        """

        :return: renvoie la position du label dans prog
        """
        return [list(self.prog).index(n) for n in self.prog if label == n.get_label()][0]

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

    def run(self):
        # TODO keep evaluating instruction respecting the pc register until encountering STOP
        while self.prog[self.pc].get_command() != 'STOP':
            print("intruction courant : ", self.prog[self.pc])
            self.instructions[self.prog[self.pc].get_command()].execute(self)

    # TODO replace by using re
    def read_file(self, file):
        """
        read intruction of program and set self.prog
        :rtype: object
        """

        with open(file, "r") as f:
            for line in f.readlines():
                buffer = line.split()
                label = buffer[0].replace(':', '')

                if len(buffer) == 3:
                    self.prog = np.append(self.prog,
                                          LineInstruction(label=label, command=buffer[1], args=buffer[2]))
                elif len(buffer) == 2:
                    self.prog = np.append(self.prog, LineInstruction(command=buffer[0], args=buffer[1]))
                elif len(buffer) == 1:
                    # self.prog = np.insert(self.prog, self.prog.size, LineInstruction(command=buffer[0]))
                    self.prog = np.append(self.prog, LineInstruction(command=buffer[0]))

                else:
                    print('eroor: ', buffer)


miniZamVM = MiniZamVM()

miniZamVM.read_file(FILE_fun1)
miniZamVM.run()
