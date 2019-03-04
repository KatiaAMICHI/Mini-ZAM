from abc import ABC, abstractmethod
from .mlvalue import MLValue


class Instruction(ABC):
    @abstractmethod
    def execute(self, state):
        pass


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
    def execute(self, state):
        state.set_accumulator(state.fetch())


class Prim(Instruction):
    binary_op = {"+": _Add(), "-": _Minus(), "*": _Mul(), "/": _Div(),
                 "or": _Or(), "and": _And(),
                 "<>": _NotEq(), "=": _Eq(), "<": _Lt(), "<=": _LtEq(), ">": _Gt(), ">=": _GtEq()}

    unary_op = {"not": _Not(), "print": _Print()}

    def execute(self, state):
        op = state.fetch()

        if op in Prim.unary_op:
            x = Prim.unary_op[op].execute(state.get_accumulator())
            state.set_accumulator(x)

        elif op in Prim.binary_op:
            x = Prim.binary_op[op].execute(state.get_accumulator(), state.pop())
            state.set_accumulator(x)


class Branch(Instruction):
    def execute(self, state):
        label = state.fetch()
        state.set_pc(state.get_position(label))


class BranchIfNot(Instruction):
    def execute(self, state):
        label = state.fetch()
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
    def execute(self, state):
        state.set_accumulator(state.peek(state.fetch()))


class EnvAcc(Instruction):
    def execute(self, state):
        state.set_accumulator(state.get_env(state.fetch()))


class Closure(Instruction):
    def execute(self, state):
        (label, n) = state.fetch()
        if n > 0:
            state.push(state.get_accumulator())
            state.set_accumulator(MLValue.from_closure(state.get_position(label), state.pop(n)))


class Apply(Instruction):
    def execute(self, state):
        n = state.fetch()
        args = state.pop(n)
        env = state.get_env()
        pc = state.get_pc() + 1
        state.push(MLValue.from_closure(pc, env), args)
        acc = state.get_accumulator()
        state.change_context(acc)


class Return(Instruction):
    def execute(self, state):
        n = state.fetch()
        args = state.pop(n)
        state.change_context(args[-1])


class Stop(Instruction):
    def execute(self, state):
        pass