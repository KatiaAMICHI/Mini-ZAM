import gc
from queue import LifoQueue

import numpy as np

gc.disable()

FILE_facto_tailrec = r"tests/appterm/facto_tailrec.txt"


# a partir de self.prog[...][O] qu'on  determine l'instruction à effectué


class LIFO(LifoQueue):

    def get_val(self, i):
        """
        Renvoie le i-ième element de la queue
        """
        return self.queue[i]

    def get_vals(self, n):
        """
        Renvoie et retire les n premier element de la queue
        """
        result = self.queue[:n]
        del self.queue[:n]
        return result

    def put_list(self, list_elem):
        self.queue = list_elem + self.queue


class MiniZAM:
    def __init__(self):
        self.prog = np.array([], dtype=[('label', np.object),
                                        ('baz', np.object)])  # un tableau de couples (label, instruction)
        self.stack = LIFO()  # structure LIFO
        self.env = []  # un collection de mlvalue
        self.pc = 0  # pointeur de code vers l’instruction courante
        self.accu = []  # pour stocker certaines values (mlvalue)

        # TODO demmander au prof si on a le droit de rajouter un attribut dans la class MiniZam
        self.position_label = dict()

    def set_accu_index(self, i, env=True, stack=False):
        if stack:
            self.accu = self.stack.get_val(i)
        elif env:
            self.accu = self.env[i]

    def get_accu(self):
        return self.accu

    def set_accu(self, value=None, label=None, nb_elem=None):
        """

        :arg value
        :arg label
        :arg nb_elem
        """
        if label and nb_elem:
            self.accu = (self.position_label(label), self.stack.get_vals(nb_elem))
        elif value:
            self.accu = value

    def pop_push_strack(self, nb_elem=None):
        if nb_elem:
            self.stack.get_vals(nb_elem)
            self.stack.put(self.env)
            self.stack.put(self.pc + 1)

    def put_in_to_stack(self):
        """
        Ajout en tête de stack la valeur de accu
        """
        self.stack.put(self.accu)

    def get_in_to_stack(self):
        """
        Retire et renvoie l'élément en tête de stack

        :rtype: int
        :return : renvoie l'élément en tête de stack
        """
        return self.stack.get(0)

    def set_pc_opt(self, label=None, apply=False):
        if label:
            self.pc = self.position_label[label]
        if apply:
            # self.accu[0] correspond au label d'une instruction
            self.pc = self.accu[0]

    def set_env_opt(self, apply=False):
        if apply:
            self.env = self.accu[1]

    def position(self):
        for n in self.prog:
            if n[0] is not None:
                self.position_label[n[0]] = list(self.prog).index(n)

    def stack_empty(self):
        return self.stack.empty()

    def increment_pc(self):
        self.pc += 1

    def read_file(self):
        """ !!  a changer d'emplacement
        read intruction of program and set self.prog
        :rtype: object
        """
        with open(FILE_facto_tailrec, "r") as f:
            for line in f.readlines():
                buffer = line.split()

                # dans le cas où on a bien (label, instructions)
                if len(buffer) == 3:
                    label = buffer[0].replace(':', '')
                    instructions = buffer[1:]
                    self.prog = np.insert(self.prog, self.prog.size, (label, instructions))
                # sinon on insert (None, instructions) None correspont a l'absence du label
                elif len(buffer) > 0:
                    self.prog = np.insert(self.prog, self.prog.size, (None, buffer))
                # dans la cas la line est vide
                else:
                    print('eroor: ', buffer)
        self.position()
        del buffer, line
        if label:
            del label
        if instructions:
            del instructions


mini_zam = MiniZAM()
mini_zam.read_file()
mini_zam.stack.put(1)
mini_zam.stack.put(2)
mini_zam.stack.put(3)
mini_zam.stack.put(5)
mini_zam.stack.put(4)
print("avant : ", mini_zam.stack.qsize())
