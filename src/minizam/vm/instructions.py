from abc import ABC, abstractmethod
from .mlvalue import MLValue


class Instruction(ABC):
    def parse_args(self, args):
        return args;

    @abstractmethod
    def execute(self, state):
        pass

    @staticmethod
    def check_length(value, l, inst):
        if len(value) != l:
            raise ValueError(inst + " expect " + str(l) + " argument(s).")

    @staticmethod
    def check_bool(value):
        if not (value is MLValue.true()) and not (value is MLValue.false()):
            raise TypeError(str(value) + " is not an instance of bool.")


class _BinaryPrim(ABC):
    @abstractmethod
    def execute(self, one, two):
        pass


class _UnaryPrim(ABC):
    @abstractmethod
    def execute(self, one):
        pass


class _Add(_BinaryPrim):
    def execute(self, one, two):
        return one + two


class _Minus(_BinaryPrim):
    def execute(self, one, two):
        return one - two


class _Mul(_BinaryPrim):
    def execute(self, one, two):
        return one * two


class _Div(_BinaryPrim):
    def execute(self, one, two):
        return one / two


class _And(_BinaryPrim):
    def execute(self, one, two):
        Instruction.check_bool(one)
        Instruction.check_bool(two)
        if one and two:
            return MLValue.true()

        return MLValue.false()


class _Or(_BinaryPrim):
    def execute(self, one, two):
        Instruction.check_bool(one)
        Instruction.check_bool(two)
        if one or two:
            return MLValue.true()

        return MLValue.false()


class _Not(_UnaryPrim):
    def execute(self, one):
        Instruction.check_bool(one)

        if one is MLValue.true():
            return MLValue.false()
        return MLValue.true()


class _Eq(_BinaryPrim):
    def execute(self, one, two):
        return one == two


class _NotEq(_BinaryPrim):
    def execute(self, one, two):
        return one != two


class _Lt(_BinaryPrim):
    def execute(self, one, two):
        return one < two


class _LtEq(_BinaryPrim):
    def execute(self, one, two):
        return one <= two


class _Gt(_BinaryPrim):
    def execute(self, one, two):
        return one > two


class _GtEq(_BinaryPrim):
    def execute(self, one, two):
        return one >= two


class _Print(_UnaryPrim):
    def execute(self, one):
        print(chr(one.value))


###########################################
class Const(Instruction):

    def parse_args(self, args):
        Instruction.check_length(args, 1, "CONST")
        return MLValue.from_int(int(args[0]))

    def execute(self, state):
        acc = self.parse_args(state.fetch())
        state.set_accumulator(acc)


class Prim(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 1, "PRIM")
        return args[0]

    binary_op = {"+": _Add(), "-": _Minus(), "*": _Mul(), "/": _Div(),
                 "or": _Or(), "and": _And(),
                 "<>": _NotEq(), "=": _Eq(), "<": _Lt(), "<=": _LtEq(), ">": _Gt(), ">=": _GtEq()}

    unary_op = {"not": _Not(), "print": _Print()}

    def execute(self, state):
        op = self.parse_args(state.fetch())

        if op in Prim.unary_op:
            x = Prim.unary_op[op].execute(state.get_accumulator())
            state.set_accumulator(x)
        elif op in Prim.binary_op:
            x = Prim.binary_op[op].execute(state.get_accumulator(), state.pop())
            state.set_accumulator(x)
        else:
            raise ValueError(str(op) + "is not an operator.")


class Branch(Instruction):

    def parse_args(self, args):
        Instruction.check_length(args, 1, "BRANCH")
        return args[0]

    def execute(self, state):
        label = self.parse_args(state.fetch())
        state.set_pc(state.get_position(label))


class BranchIfNot(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 1, "BRANCHIFNOT")
        return args[0]

    def execute(self, state):
        label = self.parse_args(state.fetch())

        acc = state.get_accumulator()
        if acc is MLValue.false():
            state.set_pc(state.get_position(label))


class Push(Instruction):
    def execute(self, state):
        state.push(state.get_accumulator())


class Pop(Instruction):
    def execute(self, state):
        state.pop()


class Acc(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 1, "ACC")
        return int(args[0])

    def execute(self, state):
        index = self.parse_args(state.fetch())
        state.set_accumulator(state.peek(index))


class EnvAcc(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 1, "ENVACC")
        return int(args[0])

    def execute(self, state):
        index = self.parse_args(state.fetch())
        state.set_accumulator(state.get_env(index))


class Closure(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 2, "CLOSURE")
        return args[0], int(args[1])

    def execute(self, state):
        (label, n) = self.parse_args(state.fetch())

        if n > 0:
            state.push(state.get_accumulator())
            state.set_accumulator(MLValue.from_closure(state.get_position(label), state.pop(n)))
        else:
            state.set_accumulator(MLValue.from_closure(state.get_position(label), []))


class ClosureRec(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 2, "CLOSURE")
        return args[0], int(args[1])

    def execute(self, state):
        (label, n) = self.parse_args(state.fetch())

        pc = state.get_position(label)
        if n > 0:
            state.push(state.get_accumulator())
            state.set_accumulator(MLValue.from_closure(pc, [pc] + state.pop(n)))
        else:
            state.set_accumulator(MLValue.from_closure(pc, [pc]))

        state.push(state.get_accumulator())


class OffSetClosure(Instruction):
    def execute(self, state):
        state.set_accumulator(MLValue.from_closure(state.get_env(0), state.get_env()))


class Apply(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 1, "APPLY")
        return int(args[0])

    def execute(self, state):
        n = self.parse_args(state.fetch())

        args = state.pop(n)

        env = state.get_env()
        pc = state.get_pc()
        extra_args = state.get_extra_args()
        state.push(args + [pc, env, extra_args])

        state.change_context()
        state.set_extra_args(n - 1)


class ReStart(Instruction):
    def execute(self, state):
        env = state.get_env()
        n = len(env)

        # déplacer les éléments de env de 1 à n-1 dans la pile
        state.push(env[1:n - 1])

        # extra args est incrémenté de (n − 1).
        state.set_extra_args(state.get_extra_args() + (n - 1))

        # env prend pour valeur de env[0]
        state.set_env(env[0])

        state.increment_pc()


class Grab(Instruction):
    def execute(self, state):
        n = int(state.fetch()[0])
        extra_args = int(state.get_extra_args())

        if extra_args >= n:
            state.set_extra_args(extra_args - n)
            state.increment_pc()
        else:
            # dépiler extra_args+1 éléments
            ele_pop = state.pop(extra_args + 1)

            # changer l'accumulateur
            acc = MLValue.from_closure(state.get_pc() - 1, [state.get_env()] + ele_pop)
            state.set_accumulator(acc)

            # changer les valeurs extra_args, pc, env
            state.set_extra_args(state.pop())
            state.set_pc(state.pop())
            state.set_env(state.pop())


class MakeBlock(Instruction):
    """
    Crée un bloc de taille n,
        ajoute un element dans le bloc et change la valeur de l'accumulateur si n >0
    """

    def execute(self, state):
        n = int(state.fetch()[0])
        if n > 0:
            accu = state.get_accumulator()
            state.add_to_bloc(accu)
            state.pop(n - 1)
            state.set_accumulator(MLValue.from_bloc(state.get_bloc()))
        state.increment_pc()


class GetField(Instruction):
    """
    Met dans l’accumulateur la n-ième valeur du bloc contenu dans accu.
    """

    def execute(self, state):
        n = int(state.fetch()[0])
        val = state.set_accumulator().value
        state.set_accumulator(val[n])
        state.increment_pc()


class GetVectItem(Instruction):
    """
    met dans l’accumulateur la taille du bloc situé dans accu.
    """

    def execute(self, state):
        len_bloc = len(state.get_accumulator().value)
        state.set_accumulator(len_bloc)
        state.increment_pc()


class VectLength(Instruction):
    """
    Dépile un élément n de stack puis met dans accu la n-i`ème valeur du
    bloc situé dans l’accumulateur
    """

    def execute(self, state):
        # dépile un élément n de stack
        n = state.pop()
        # récupére bloc dans l’accumulateur
        val_bloc = state.get_accumulator().value
        # met dans accu la n-i`ème valeur du bloc
        state.set_accumulator(val_bloc[n])

        state.increment_pc()


class SetField(Instruction):
    def execute(self, state):
        n = int(state.fetch()[0])

        # dépiler une valeur dans la stack
        val_stack = state.pop()

        # récupérer le bloc dans l'accumulateur sous forme de liste
        bloc = list(state.get_accumulator().value)
        # TODO es ce qu'on écrase la n'ième valeur du bloc ??
        # mettre la valeur dépilée dans la n'ième valeur du bloc
        bloc[n] = val_stack

        state.increment_pc()


class SetVectItem(Instruction):
    def execute(self, state):
        # dépiler deux valeurs dans la stack
        n = state.pop()
        v = state.pop()

        # récupérer le bloc dans l'accumulateur sous forme de liste
        bloc = list(state.get_accumulator().value)
        # TODO es ce qu'on écrase la n'ième valeur du bloc ??
        # mettre la valeur dépilée dans la n'ième valeur du bloc
        bloc[n] = v

        state.set_accumulator(MLValue.unit())

        state.increment_pc()


class Assign(Instruction):
    """
    Remplace le n-ième élément de la pile par la valeur de accu,
    L'accumulator prend la valeur ()
    """

    def execute(self, state):
        n = int(state.fetch()[0])
        acc = state.get_accumulator()

        # remplacer le n-ième élément de la pile par la valeur de accu
        state.set_stack(n, acc)

        # mettre la valeur () dans l'accumulateur
        state.set_accumulator(MLValue.unit())

        state.increment_pc()


class Return(Instruction):
    def execute(self, state):
        n = int(state.fetch()[0])
        state.pop(n)
        if state.get_extra_args() == 0:
            state.set_pc(state.pop(0))
            state.set_env(state.pop(0))
            state.pop(0)
        else:
            state.set_extra_args(state.get_extra_args() - 1)
            state.set_env(state.get_accumulator().value[1])
            state.set_pc(state.get_accumulator().value[0])


class Stop(Instruction):
    def execute(self, state):
        state.shutdown()
