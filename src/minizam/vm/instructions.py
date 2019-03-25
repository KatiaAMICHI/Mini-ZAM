from abc import ABC, abstractmethod
from .mlvalue import MLValue


class Instruction(ABC):
    def parse_args(self, args):
        return args

    @abstractmethod
    def execute(self, state, args):
        pass


class ArgsParser:

    def __init__(self, args, inst):
        self.args = args
        self.inst = inst

    def parse(self, args_types):

        if not isinstance(args_types, list):
            args_types = [args_types]

        if len(self.args) != len(args_types):
            raise ValueError(self.inst + " expect " + str(len(args_types)) + " argument(s).")

        args = []
        for i, type_arg in enumerate(args_types):
            args.append(type_arg(self.args[i]))

        if len(args) == 1:
            return args[0]
        return args

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
        ArgsParser.check_bool(one)
        ArgsParser.check_bool(two)
        if one and two:
            return MLValue.true()

        return MLValue.false()


class _Or(_BinaryPrim):
    def execute(self, one, two):
        ArgsParser.check_bool(one)
        ArgsParser.check_bool(two)
        if one or two:
            return MLValue.true()

        return MLValue.false()


class _Not(_UnaryPrim):
    def execute(self, one):
        ArgsParser.check_bool(one)

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
        return ArgsParser(args, "CONST").parse([int])

    def execute(self, state, n):
        state.set_accumulator(MLValue.from_int(n))


class Prim(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "PRIM").parse([str])

    binary_op = {"+": _Add(), "-": _Minus(), "*": _Mul(), "/": _Div(),
                 "or": _Or(), "and": _And(),
                 "<>": _NotEq(), "=": _Eq(), "<": _Lt(), "<=": _LtEq(), ">": _Gt(), ">=": _GtEq()}

    unary_op = {"not": _Not(), "print": _Print()}

    def execute(self, state, op):

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
        return ArgsParser(args, "BRANCH").parse([str])

    def execute(self, state, label):
        state.set_pc(state.get_position(label))


class BranchIfNot(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "BRANCHIFNOT").parse([str])

    def execute(self, state, label):
        acc = state.get_accumulator()
        if acc == MLValue.false():
            state.set_pc(state.get_position(label))


class Push(Instruction):
    """
    Empilement d'une valeur dans la stack
    """

    def execute(self, state, args):
        state.push(state.get_accumulator())


class Pop(Instruction):
    """
    Dépilement d'une valeur dans la stack
    """

    def execute(self, state, args):
        state.pop()


class Acc(Instruction):
    """
    Accès à la i-ième valeur de la pile
    """

    def parse_args(self, args):
        return ArgsParser(args, "ACC").parse([int])

    def execute(self, state, index):
        state.set_accumulator(state.peek(index))


class EnvAcc(Instruction):
    """
    Accès à la i-ième valeur de l’environnement
    """

    def parse_args(self, args):
        return ArgsParser(args, "ENVACC").parse([int])

    def execute(self, state, index):
        state.set_accumulator(state.get_env(index))


class Closure(Instruction):
    """
    Création de fermeture
    """

    def parse_args(self, args):
        return ArgsParser(args, "CLOSURE").parse([str, int])

    def execute(self, state, args):
        (label, n) = args

        if n > 0:
            state.push(state.get_accumulator())
            state.set_accumulator(MLValue.from_closure(state.get_position(label), state.pop(n)))
        else:
            state.set_accumulator(MLValue.from_closure(state.get_position(label), []))


class ClosureRec(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "CLOSUREREC").parse([str, int])

    def execute(self, state, args):
        (label, n) = args

        pc = state.get_position(label)
        if n > 0:
            state.push(state.get_accumulator())
            state.set_accumulator(MLValue.from_closure(pc, [pc] + state.pop(n)))
        else:
            state.set_accumulator(MLValue.from_closure(pc, [pc]))

        state.push(state.get_accumulator())


class OffSetClosure(Instruction):
    def execute(self, state, args):
        state.set_accumulator(MLValue.from_closure(state.get_env(0), state.get_env()))


class Apply(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "APPLY").parse([int])

    def execute(self, state, n):
        args = state.pop(n)

        env = state.get_env()
        pc = state.get_pc()
        extra_args = state.get_extra_args()
        state.push(args + [pc, env, extra_args])

        state.change_context()
        state.set_extra_args(n - 1)


class Grab(Instruction):
    """
    Gestion de l’application partielle
    """

    def parse_args(self, args):
        return ArgsParser(args, "GRAB").parse([int])

    def execute(self, state, n):

        extra_args = state.get_extra_args()

        if extra_args >= n:
            state.set_extra_args(extra_args - n)
        else:
            # dépiler extra_args+1 éléments
            ele_pop = state.pop(extra_args + 1)

            # changer l'accumulateur
            acc = MLValue.from_closure(state.get_pc() - 2, [state.get_env()] + ele_pop)
            state.set_accumulator(acc)

            # changer les valeurs extra_args, pc, env
            state.set_pc(state.pop())
            state.set_env(state.pop())
            state.set_extra_args(state.pop())


class ReStart(Instruction):
    def execute(self, state, args):
        env = state.get_env()
        n = len(env)

        # déplacer les éléments de env de 1 à n-1 dans la pile
        state.push(env[1:n])

        # extra args est incrémenté de (n − 1).
        state.set_extra_args(state.get_extra_args() + (n - 1))

        # env prend pour valeur de env[0]
        state.set_env(env[0])


class MakeBlock(Instruction):
    """
    Crée un bloc de taille n,
        ajoute un element dans le bloc et change la valeur de l'accumulateur
        si n >0
    """

    def parse_args(self, args):
        return ArgsParser(args, "MAKEBLOCK").parse([int])

    def execute(self, state, n):
        if n > 0:
            accu = state.get_accumulator()
            block = [accu]
            if len(block) < n:
                print("n : ", n)
                val_pop = state.pop(n - 1)
                if not isinstance(val_pop, list):
                    val_pop = [val_pop]
                if len(val_pop) != 0:
                    block = block + val_pop
            state.set_accumulator(MLValue.from_block(block))


class GetField(Instruction):
    """
    Met dans l’accumulateur la n-ième valeur du bloc contenu dans accu.
    """

    def parse_args(self, args):
        return ArgsParser(args, "GETFIELD").parse([int])

    def execute(self, state, n):
        val = state.get_accumulator().value
        print('val[n] : ', val[n])
        state.set_accumulator(val[n])


class VectLength(Instruction):
    """
    met dans l’accumulateur la taille du bloc situé dans accu.
    """

    def execute(self, state, args):
        len_block = len(state.get_accumulator().value)
        state.set_accumulator(MLValue.from_int(len_block))


class GetVectItem(Instruction):
    """
    Dépile un élément n de stack puis met dans accu la n-i`ème valeur du
    bloc situé dans l’accumulateur
    """

    def execute(self, state, args):
        # dépile un élément n de stack
        n = state.pop()
        # récupére bloc dans l’accumulateur
        val_block = state.get_accumulator().value
        # met dans accu la n-i`ème valeur du bloc
        if isinstance(n, MLValue):
            n = n.value
        state.acc = val_block[n]
        state.set_accumulator(val_block[n])


class SetField(Instruction):
    """
    Met dans la n-ième valeur du bloc situé dans accu
    la valeur d´epilée de stack.
    """

    def parse_args(self, args):
        return ArgsParser(args, "SETFIELD").parse([int])

    def execute(self, state, n):
        # dépiler une valeur dans la stack
        val_stack = state.pop()

        # récupérer le bloc dans l'accumulateur sous forme de liste
        block = list(state.get_accumulator().value)
        # mettre la valeur dépilée dans la n'ième valeur du bloc
        block[n] = val_stack

        state.acc.value[n] = val_stack

        # state.set_accumulator(MLValue.from_block(block))


class SetVectItem(Instruction):
    """
    Dépile deux éléments n et v de stack,
    met v dans la n-i`ème valeur du bloc situé dans accu.
    L'accumulateur prend () comme valeur
    """

    def execute(self, state, args):
        # dépiler deux valeurs dans la stack
        n = state.pop()
        v = state.pop()

        if isinstance(n, MLValue):
            n = n.value

        state.acc.value = state.acc.value[0:n] + [v] + state.acc.value[(n + 1)::]
        state.set_accumulator(MLValue.unit())


class Assign(Instruction):
    """
    Remplace le n-ième élément de la pile par la valeur de accu,
    L'accumulator prend la valeur ()
    """

    def parse_args(self, args):
        return ArgsParser(args, "ASSIGN").parse([int])

    def execute(self, state, n):
        acc = state.get_accumulator()

        # remplacer le n-ième élément de la pile par la valeur de accu
        state.set_stack(n, acc)
        # state.stack.items[len(state.stack.items)-n-1] = MLValue.from_int(1111)

        # mettre la valeur () dans l'accumulateur
        state.set_accumulator(MLValue.unit())


class Return(Instruction):

    def parse_args(self, args):
        return ArgsParser(args, "RETURN").parse([int])

    def execute(self, state, n):
        state.pop(n)
        if state.get_extra_args() == 0:
            state.set_pc(state.pop(0))
            state.set_env(state.pop(0))
            state.pop(0)
        else:
            state.set_extra_args(state.get_extra_args() - 1)
            state.change_context()


class AppTerm(Instruction):

    def parse_args(self, args):
        return ArgsParser(args, "APPTERM").parse([int, int])

    def execute(self, state, args):
        n, m = args
        args = state.pop(n)
        state.pop(m - n)
        state.push(args)
        state.change_context()
        state.extra_args = state.extra_args + (n - 1)


class Stop(Instruction):
    def execute(self, state, args):
        state.shutdown()


class PushTrap(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "PUSHTRAP").parse([str])

    def execute(self, state, label):
        state.push([state.get_position(label), state.trap_sp, state.get_env(), state.extra_args])
        state.trap_sp = state.peek()


class PopTrap(Instruction):
    def execute(self, state, args):
        state.pop()
        state.trap_sp = state.pop()
        state.pop(2)


class Raise(Instruction):

    def execute(self, state, args):
        if state.trap_sp is None:
            state.shutdown()
        else:
            index = state.stack.items.index(state.trap_sp)
            state.pop(index)
            state.pc = state.pop()
            state.trap_sp = state.pop()
            state.env = state.pop()
            state.extra_args = state.pop()
            # del state.stack.items[index:index + 4]
