from abc import ABC, abstractmethod
from .mlvalue import MLValue


class Instruction(ABC):
    def parse_args(self, args):
        return args

    @abstractmethod
    def execute(self, vm, args):
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

    def execute(self, vm, n):
        vm.acc = MLValue.from_int(n)


class Prim(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "PRIM").parse([str])

    binary_op = {"+": _Add(), "-": _Minus(), "*": _Mul(), "/": _Div(),
                 "or": _Or(), "and": _And(),
                 "<>": _NotEq(), "=": _Eq(), "<": _Lt(), "<=": _LtEq(), ">": _Gt(), ">=": _GtEq()}

    unary_op = {"not": _Not(), "print": _Print()}

    def execute(self, vm, op):

        if op in Prim.unary_op:
            vm.acc = Prim.unary_op[op].execute(vm.acc)
        elif op in Prim.binary_op:
            vm.acc = Prim.binary_op[op].execute(vm.acc, vm.pop())
        else:
            raise ValueError(str(op) + "is not an operator.")


class Branch(Instruction):

    def parse_args(self, args):
        return ArgsParser(args, "BRANCH").parse([str])

    def execute(self, vm, label):
        vm.pc = vm.get_position(label)


class BranchIfNot(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "BRANCHIFNOT").parse([str])

    def execute(self, vm, label):
        acc = vm.acc
        if acc is MLValue.false():
            vm.pc = vm.get_position(label)


class Push(Instruction):
    """
    Empilement d'une valeur dans la stack
    """

    def execute(self, vm, args):
        vm.push(vm.acc)


class Pop(Instruction):
    """
    Dépilement d'une valeur dans la stack
    """

    def execute(self, vm, args):
        vm.pop()


class Acc(Instruction):
    """
    Accès à la i-ième valeur de la pile
    """

    def parse_args(self, args):
        return ArgsParser(args, "ACC").parse([int])

    def execute(self, vm, index):
        vm.acc = vm.peek(index)


class EnvAcc(Instruction):
    """
    Accès à la i-ième valeur de l’environnement
    """

    def parse_args(self, args):
        return ArgsParser(args, "ENVACC").parse([int])

    def execute(self, vm, index):
        vm.acc = vm.get_env(index)


class Closure(Instruction):
    """
    Création de fermeture
    """

    def parse_args(self, args):
        return ArgsParser(args, "CLOSURE").parse([str, int])

    def execute(self, vm, args):
        (label, n) = args

        if n > 0:
            vm.push(vm.acc)
            vm.acc = MLValue.from_closure(vm.get_position(label), vm.pop(n))
        else:
            vm.acc = MLValue.from_closure(vm.get_position(label), [])


class ClosureRec(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "CLOSUREREC").parse([str, int])

    def execute(self, vm, args):
        (label, n) = args

        pc = vm.get_position(label)
        if n > 0:
            vm.push(vm.acc)
            vm.acc = MLValue.from_closure(pc, [pc] + vm.pop(n))
        else:
            vm.acc = MLValue.from_closure(pc, [pc])

        vm.push(vm.acc)


class OffSetClosure(Instruction):
    def execute(self, vm, args):
        vm.acc = MLValue.from_closure(vm.get_env(0), vm.env)


class Apply(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "APPLY").parse([int])

    def execute(self, vm, n):
        args = vm.pop(n)

        env = vm.env
        pc = vm.pc
        extra_args = vm.extra_args
        vm.push(args + [pc, env, extra_args])

        vm.change_context()
        vm.extra_args = n - 1


class Grab(Instruction):
    """
    Gestion de l’application partielle
    """

    def parse_args(self, args):
        return ArgsParser(args, "GRAB").parse([int])

    def execute(self, vm, n):

        extra_args = vm.extra_args

        if extra_args >= n:
            vm.extra_args = extra_args - n
        else:
            # dépiler extra_args+1 éléments
            ele_pop = vm.pop(extra_args + 1)

            # changer l'accumulateur
            acc = MLValue.from_closure(vm.pc - 2, [vm.env] + ele_pop)
            vm.acc = acc
            # changer les valeurs extra_args, pc, env
            vm.pc = vm.pop()
            vm.env = vm.pop()
            vm.extra_args = vm.pop()


class ReStart(Instruction):
    def execute(self, vm, args):
        env = vm.env
        n = len(env)

        # déplacer les éléments de env de 1 à n-1 dans la pile
        vm.push(env[1:n])

        # extra args est incrémenté de (n − 1).
        vm.extra_args = vm.extra_args + (n - 1)

        # env prend pour valeur de env[0]
        vm.env = env[0]


class MakeBlock(Instruction):
    """
    Crée un bloc de taille n,
        ajoute un element dans le bloc et change la valeur de l'accumulateur
        si n >0
    """

    def parse_args(self, args):
        return ArgsParser(args, "MAKEBLOCK").parse([int])

    def execute(self, vm, n):
        if n > 0:
            acc = vm.acc
            block = [acc]
            val_pop = vm.pop(n - 1)
            if not isinstance(val_pop, list):
                val_pop = [val_pop]
            if len(val_pop) != 0:
                block = block + val_pop
            vm.acc = MLValue.from_block(block)


class GetField(Instruction):
    """
    Met dans l’accumulateur la n-ième valeur du bloc contenu dans accu.
    """

    def parse_args(self, args):
        return ArgsParser(args, "GETFIELD").parse([int])

    def execute(self, vm, n):
        val = vm.acc.value
        vm.acc = val[n]


class VectLength(Instruction):
    """
    met dans l’accumulateur la taille du bloc situé dans accu.
    """

    def execute(self, vm, args):
        len_block = len(vm.acc.value)
        vm.acc = MLValue.from_int(len_block)


class GetVectItem(Instruction):
    """
    Dépile un élément n de stack puis met dans accu la n-i`ème valeur du
    bloc situé dans l’accumulateur
    """

    def execute(self, vm, args):
        # dépile un élément n de stack
        n = vm.pop()
        # récupére bloc dans l’accumulateur
        val_block = vm.acc.value
        # met dans accu la n-i`ème valeur du bloc
        if isinstance(n, MLValue):
            n = n.value
        vm.acc = val_block[n]
        vm.acc = val_block[n]


class SetField(Instruction):
    """
    Met dans la n-ième valeur du bloc situé dans accu
    la valeur d´epilée de stack.
    """

    def parse_args(self, args):
        return ArgsParser(args, "SETFIELD").parse([int])

    def execute(self, vm, n):
        # dépiler une valeur dans la stack
        val_stack = vm.pop()

        # récupérer le bloc dans l'accumulateur sous forme de liste
        block = list(vm.acc.value)
        # mettre la valeur dépilée dans la n'ième valeur du bloc
        block[n] = val_stack

        # vm.acc.value[n] = val_stack

        vm.acc = MLValue.from_block(block)


class SetVectItem(Instruction):
    """
    Dépile deux éléments n et v de stack,
    met v dans la n-i`ème valeur du bloc situé dans accu.
    L'accumulateur prend () comme valeur
    """

    def execute(self, vm, args):
        # dépiler deux valeurs dans la stack
        n = vm.pop()
        v = vm.pop()

        if isinstance(n, MLValue):
            n = n.value

        vm.acc.value = vm.acc.value[0:n] + [v] + vm.acc.value[(n + 1)::]
        vm.acc = MLValue.unit()


class Assign(Instruction):
    """
    Remplace le n-ième élément de la pile par la valeur de accu,
    L'accumulator prend la valeur ()
    """

    def parse_args(self, args):
        return ArgsParser(args, "ASSIGN").parse([int])

    def execute(self, vm, n):
        acc = vm.acc

        # remplacer le n-ième élément de la pile par la valeur de accu
        vm.set_element(n, acc)
        # vm.stack.items[len(vm.stack.items)-n-1] = MLValue.from_int(1111)

        # mettre la valeur () dans l'accumulateur
        vm.acc = MLValue.unit()


class Return(Instruction):

    def parse_args(self, args):
        return ArgsParser(args, "RETURN").parse([int])

    def execute(self, vm, n):
        vm.pop(n)
        if vm.extra_args == 0:
            vm.pc = vm.pop()
            vm.env = vm.pop()
            vm.pop()
        else:
            vm.extra_args = vm.extra_args - 1
            vm.change_context()


class AppTerm(Instruction):

    def parse_args(self, args):
        return ArgsParser(args, "APPTERM").parse([int, int])

    def execute(self, vm, args):
        n, m = args
        args = vm.pop(n)
        vm.pop(m - n)
        vm.push(args)
        vm.change_context()
        vm.extra_args = vm.extra_args + (n - 1)


class Stop(Instruction):
    def execute(self, vm, args):
        vm.shutdown()


class PushTrap(Instruction):
    def parse_args(self, args):
        return ArgsParser(args, "PUSHTRAP").parse([str])

    def execute(self, vm, label):
        vm.push([vm.get_position(label), vm.trap_sp, vm.env, vm.extra_args])
        vm.trap_sp = vm.peek()


class PopTrap(Instruction):
    def execute(self, vm, args):
        vm.pop()
        vm.trap_sp = vm.pop()
        vm.pop(2)


class Raise(Instruction):

    def execute(self, vm, args):
        if vm.trap_sp is None:
            vm.shutdown()
        else:
            index = vm.stack.items.index(vm.trap_sp)
            vm.pop(index)
            vm.pc = vm.pop()
            vm.trap_sp = vm.pop()
            vm.env = vm.pop()
            vm.extra_args = vm.pop()
            # del vm.stack.items[index:index + 4]
