import re
from .instructions import *
import sys


# TODO changer acc -> accu

class _Stack:
    """
    Class qui correspond à une LIFO
    """

    def __init__(self):
        """
        initialisation de la pile à vide
        """

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
        """
        Empile en tête de stack elements

        :param elements : elements à ajouter dans la stack
        """

        if not isinstance(elements, list):
            elements = [elements]
        self.items = elements + self.items

    def set_element(self, index, value):
        """
        Changement de la valeur à l'indice index dans la stack par value

        :param index: qui correspond à un indice dans la pile
        :param value: la nouvelle valeur à changer dans la pile
        """

        if len(self.items) % 2 == 0:
            self.items[len(self.items) - index] = value
        else:
            self.items[len(self.items) - index - 1] = value

    def is_empty(self):
        """
        Vérifier si la pile est vide

        :return: renvoie true si la pile est vide, false dans le cas contraire
        """

        return self.items == []

    def size(self):
        """
        Méthode qui renvoie la taille de la pile

        :return: renvoie la taille de la pile
        """
        return len(self.items)

    def __repr__(self):
        """

        :return: renvoie le str des elements de la pile
        """
        return "_Stack(items : %s )" % (self.items)


class LineInstruction:
    """
    Class qui correspond à aux instructions du programme
    """

    def __init__(self, label=None, command=None, args=None):
        """
        Initialisation de la ligne d'instruction

        :param label: label de l'instruction
        :param command: la commande à exécution
        :param args: les arguments de la commande à exécution
        """
        self.label = label
        self.command = command
        self.args = args

    def __repr__(self):
        return "LineInstruction(Label : %s, Command : %s, args : %s)" % (self.label, self.command, self.args)

    def __str__(self):
        return "(Label : %s, Command : %s, args : %s)" % (self.label, self.command, self.args)

    @staticmethod
    def build(line):
        label = line[0] if line[0] else None
        command = line[1]
        args = line[2].replace(' ', '').split(",") if line[2] else []
        args = MiniZamVM.instructions[command].parse_args(args)
        return LineInstruction(label, command, args)


class MiniZamVM:
    """
    Class qui contient les fonctions principales de la machine virtuelle
    """

    instructions = {"CONST": Const(), "PRIM": Prim(),
                    "BRANCH": Branch(), "BRANCHIFNOT": BranchIfNot(),
                    "PUSH": Push(), "POP": Pop(), "ACC": Acc(), "ENVACC": EnvAcc(),
                    "CLOSURE": Closure(), "CLOSUREREC": ClosureRec(), "OFFSETCLOSURE": OffSetClosure(),
                    "RESTART": ReStart(), "GRAB": Grab(), "APPLY": Apply(), "RETURN": Return(), "APPTERM": AppTerm(),
                    "MAKEBLOCK": MakeBlock(), "GETFIELD": GetField(), "VECTLENGTH": VectLength(),
                    "GETVECTITEM": GetVectItem(), "SETFIELD": SetField(), "SETVECTITEM": SetVectItem(),
                    "ASSIGN": Assign(),
                    "PUSHTRAP": PushTrap(), "POPTRAP": PopTrap(), "RAISE": Raise(),
                    "STOP": Stop()}

    def __init__(self):
        """
        Initialisation de la machine, la mémoire à des tableau et liste vide et pc à zéro
        """

        self.prog = []
        self.stack = _Stack()  # structure LIFO
        self.env = []  # un collection de mlvalue
        self.pc = 0  # pointeur de code vers l’instruction courante
        self.acc = MLValue.unit()
        self.extra_args = 0  # le nombre d’arguments restant a appliquer à une fonction
        self.trap_sp = None

    def set_element(self, index, value):
        """
        Méthode qui modifier la valeur à l'indice stack par value

        :param index: l'indice de la stack à modifier
        :param value: la nouvelle valeur dans stack[index]
        :return: renvoie la stack avec element modifier
        """

        return self.stack.set_element(index, value)

    def pop(self, n=0):
        """
        Retire et renvoie l'élément en tête de stack

        :param n: l'indice de l'élément à retirer
        :return: renvoie l'élément retirer
        """

        return self.stack.pop(n)

    def push(self, elements):
        """
        Empile en tête de stack un élément

        :param elements: l'élément à empiler
        """

        self.stack.push(elements)

    def peek(self, i=0):
        """
        Méthode qui renvoie la valeur de la stack à l'indice i

        :param i: l'indice de l'élément à renvoyer
        :return: renvoie la valeur à l'indice i de la stack
        """

        return self.stack.peek(i)

    def is_empty(self):
        """
        Vérifier si la pile est vide

        :return: renvoie true si la pile est vide, false dans le cas contraire
        """

        return self.stack.is_empty()

    def increment_pc(self):
        """
        Incrementation de la valeur de pc

        :return: renvoie la nouvelle valeur de pc
        """

        pc = self.pc
        self.pc += 1
        if self.prog:
            self.current_args = self.prog[pc].args
        return pc

    def get_env(self, i=None):
        """
        Renvoie la valeur de env à l'indice i

        :param i: correspond à un indice dans une liste
        :return:renvoie la valeur dans env à l'indice i
        """

        if isinstance(i, int):
            return self.env[i]
        return self.env

    def get_position(self, label):
        """
        Renvoie la position courrant

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

    def print_current_state(self):
        """
        Impression du context du programme
        """

        print('\n\tpc = ', self.pc, '\n\n\taccu =', self.acc, ' ',
              "\n\n\tstack=", self.stack.items, end="\n")

    def run(self):
        """
        Méthode qui exécute les instructions du programme
        """

        while True:
            # print('\n\\item',self.prog[self.pc].command, ' pc =', self.pc)
            inst = self.prog[self.increment_pc()]
            self.instructions[inst.command].execute(self, inst.args)
            # self.print_current_state()

    def shutdown(self):
        """
        Fin de l’exécution du programme
        """

        print("acc = ", self.acc)
        exit()

    def load_file(self, file):

        """
        L'écture du programme et chargement du programme dans le registre prog
        """

        with open(file, "r") as f:
            lines = re.findall(r'(?:(\w+):)?\t(\w+)(.*)', f.read())
            self.prog = list(map(LineInstruction.build, lines))

    def load_file_optimized(self, file):
        self.load_file(file)
        for i, line in enumerate(self.prog):
            if self.prog[i].command == "APPLY" and self.prog[i + 1].command == "RETURN":
                self.prog[i].command = "APPTERM"
                n = self.prog[i].args
                m = n + self.prog[i + 1].args
                self.prog[i].args = [n, m]
                del self.prog[i + 1]
