class Switcher(object):
    def __init__(self, MINII_ZAM):
        self.MINII_ZAM = MINII_ZAM  # une référence vers MINI_ZIM
        self.n = None
        self.i = None
        self.op = None
        self.L = None

    def setArgument(self, n=None, i=None, op=None, L=None):
        """

        :arg n :        Valeur
        :arg i :
        :arg op :
        :arg L :        Label qui correspond à une instruction
        :rtype:         object
        """
        self.n = n
        self.i = i
        self.op = op
        self.L = L

    def instructions_machine(self, argument):

        method_name = str(argument)
        method = getattr(self, method_name, lambda: "Invalid instruction")
        return method()

    def CONST(self):
        """
        L’accumulateur (accu) prend pour valeur la constante n et incrementer pc
        """
        print("CONST ", self.n)

        self.MINII_ZAM.set_accu(value=self.n)

        # incrementer pc
        self.MINII_ZAM.increment_pc()

    def PRIM(self, op):
        print("PRIM ", self.op)
        # op a deux arguments

        # op unaire

        # incrementer pc
        self.MINII_ZAM.increment_pc()

    def BRANCH(self):
        """
        La valeur pc est changé par la position du label L
        """
        print("BRANCH ", self.L)
        self.MINII_ZAM.set_p_opt(label=self.L)

    def BRANCHIFNOT(self):
        """
        Change la valeur de pc en fonction de la valeur de l’accumulateur
        """
        print("BRANCHIFNOT", self.L)

        if self.MINII_ZAM.get_accu() == 0:
            self.BRANCH()
        else:
            # incrementer pc
            self.MINII_ZAM.increment_pc()

    def PUSH(self):
        """
        Empile en tête de stack la valeur située dans accu et increment pc
        """
        print("PUSH")

        self.MINII_ZAM.put_in_to_stack()
        # incrementer pc
        self.MINII_ZAM.increment_pc()

    def POP(self):
        """
        Retire et renvoie l'élément en tête de stack et increment pc

        :rtype: int
        :return : renvoie l'élément en tête de stack
        """
        print("POP")

        # incrementer pc
        self.MINII_ZAM.increment_pc()
        return self.MINII_ZAM.get_in_to_stack()

    def ACC(self):
        """
        accu prend la valeur de la i-ième valeur de stack
        """
        self.MINII_ZAM.set_accu_index(self.i, stack=True)
        # incrementer pc
        self.MINII_ZAM.increment_pc()
        print("ACC", self.i)

    def ENVACC(self):
        """
        accu prend la valeur de la i-ième valeur de env
        """
        print("ENVACC", self.i)

        self.MINII_ZAM.set_accu_index(self.i, env=True)

        # incrementer pc
        self.MINII_ZAM.increment_pc()

    def CLOSURE(self):
        """
        Change la valeur de accu en fonction de n
            Si n > 0 alors l’accumulateur est empilé.
            et une fermeture dont le code correspond au label L et dont l’environnement est constitué
            de n valeurs d´epilées de stack est créée et mise dans l’accumulateur
        """
        print("CLOSURE", self.L, self.n)
        if self.n>0:
            self.MINII_ZAM.set_acc(label=self.L, nb_elem=self.n)

        # incrementer pc
        self.MINII_ZAM.increment_pc()

    def APPLY(self):
        """

        """

        # n arguments sont dépilés

        # pc reçoit le pointeur de code de la fermeture située dans accu
        self.MINII_ZAM.set_pc_opt(apply=True)
        # env reçoit l’environnement de la fermeture située dans accu
        self.MINII_ZAM.set_env_opt(apply=True)

        # incrementer pc
        self.MINII_ZAM.increment_pc()
        print("APPLY", self.n)

    def RETURN(self):
        # incrementer pc
        self.MINII_ZAM.increment_pc()
        print("RETURN", self.n)

    def STOP(self):
        # incrementer pc
        self.MINII_ZAM.increment_pc()
        print("STOP")

    def CLOSUREREC(self):
        """
        permet de créer une fermeture récursive

        :rtype: object
        """
        # incrementer pc
        self.MINII_ZAM.increment_pc()
        print("CLOSUREREC", self.L, self.n)

    def OFFSETCLOSURE(self):
        """
        met dans accu une fermeture dont le code correspond a env[0]
        :rtype: object
        """
        # incrementer pc
        self.MINII_ZAM.increment_pc()
        print("OFFSETCLOSURE", self.L, self.n)
