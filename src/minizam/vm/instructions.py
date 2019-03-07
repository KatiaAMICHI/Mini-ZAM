from abc import ABC, abstractmethod
from .mlvalue import MLValue


class Instruction(ABC):
    def parse_args(self, args):
        pass

    @abstractmethod
    def execute(self, state):
        pass

    @staticmethod
    def check_instance(value, clazz, message):
        if not isinstance(value, clazz):
            raise ValueError(str(value) + "is not an instance of " + message + ".")

    @staticmethod
    def check_mlvalue(value):
        Instruction.check_instance(value, MLValue, "MLValue")

    @staticmethod
    def check_int(value):
        Instruction.check_instance(value, int, "int")

    @staticmethod
    def check_str(value):
        Instruction.check_instance(value, str, "string")

    @staticmethod
    def check_length(value, l, inst):
        if len(value) != l:
            raise ValueError(inst + " expect " + str(l) + " argument(s).")


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
        return one and two


class _Or(_BinaryPrim):
    def execute(self, one, two):
        return one or two


class _Not(_UnaryPrim):
    def execute(self, one):
        return not one


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
        print(chr(one))


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
        if acc == 0:
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
            state.set_accumulator(MLValue.from_closure(state.get_position(label), state.pop(n)))
            state.pop(n - 1)


class Apply(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 1, "APPLY")
        return int(args[0])

    def execute(self, state):
        n = self.parse_args(state.fetch())

        args = state.pop(n)
        env = state.get_env()
        pc = state.get_pc() + 1
        state.push(args + [pc] + [env])
        acc = state.get_accumulator()
        state.change_context(acc)


class Return(Instruction):
    def parse_args(self, args):
        Instruction.check_length(args, 1, "RETURN")
        return int(args[0])

    def execute(self, state):
        n = self.parse_args(state.fetch())
        Instruction.check_int(n)

        args = state.pop(n)
        state.set_pc(state.pop())
        state.set_env(state.pop())
        # state.change_context(args[-1])


class Stop(Instruction):
    def execute(self, state):
        state.shutdown()
