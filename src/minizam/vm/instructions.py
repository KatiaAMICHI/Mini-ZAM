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
        print(' one : ', one, ' - two : ', two)
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
        print(" *** Begin CONST *** : ")

        state.set_accumulator(MLValue.from_int(int(state.fetch()[0])))
        state.increment_pc()

        print(" *** End CONST *** ")


class Prim(Instruction):
    binary_op = {"+": _Add(), "-": _Minus(), "*": _Mul(), "/": _Div(),
                 "or": _Or(), "and": _And(),
                 "<>": _NotEq(), "=": _Eq(), "<": _Lt(), "<=": _LtEq(), ">": _Gt(), ">=": _GtEq()}

    unary_op = {"not": _Not(), "print": _Print()}

    def execute(self, state):
        op = state.fetch()[0]

        if op in Prim.unary_op:
            x = Prim.unary_op[op].execute(state.get_accumulator())
            state.set_accumulator(x)
        elif op in Prim.binary_op:
            x = Prim.binary_op[op].execute(state.get_accumulator(), state.pop())
            state.set_accumulator(x)

        state.increment_pc()


class Branch(Instruction):
    def execute(self, state):
        print(" *** Begin Branch ***")

        label = state.fetch()[0]
        state.set_pc(state.get_position(label))

        print(" --- End Branch ---")


class BranchIfNot(Instruction):
    def execute(self, state):
        print(" *** Begin BranchIfNot ***")

        label = state.fetch()
        acc = state.get_accumulator()
        if acc == 0:
            state.set_pc(state.get_position(label))
        else:
            state.increment_pc()

        print(" --- End BranchIfNot ---")


class Push(Instruction):
    def execute(self, state):
        print(" *** Begin PUCH ***")

        state.push(state.get_accumulator())
        state.increment_pc()

        print(" --- End PUCH ---")


class Pop(Instruction):
    def execute(self, state):
        print(" *** Begin POP ***")

        state.pop()
        state.increment_pc()

        print(" --- End POP ---")


class Acc(Instruction):
    def execute(self, state):
        print(" *** Begin ACC ***")

        state.set_accumulator(state.peek(int(state.fetch()[0])))
        state.increment_pc()

        print(" --- End  ACC ---")


class EnvAcc(Instruction):
    def execute(self, state):
        print(" *** Begin ENVACC ***")

        state.set_accumulator(state.get_env(state.fetch()))
        state.increment_pc()

        print(" --- End ENVACC ---")


class Closure(Instruction):

    def execute(self, state):
        print(" *** Begin CLOSURE ***")

        (label, n) = tuple(state.fetch())
        if int(n) > 0:
            state.set_accumulator(MLValue.from_closure(state.get_position(label), state.pop(n)))
            state.pop(int(n) - 1)
        state.increment_pc()

        print(" --- End CLOSURE ---")


class Apply(Instruction):
    def execute(self, state):
        print(" *** Begin APPLY ***")

        n = int(state.fetch()[0])
        args = state.pop(n)
        env = state.get_env()
        pc = state.get_pc() + 1
        state.push(args + [pc] + [env])
        acc = state.get_accumulator()
        state.change_context(acc)

        print(" --- End APPLY ---")


class Return(Instruction):
    def execute(self, state):
        print(" *** Begin RETURN ***")

        n = int(state.fetch()[0])
        args = state.pop(n)
        state.set_pc(state.pop())
        state.set_env(state.pop())

        # state.change_context(args[-1])

        print(" --- End RETURN ---")


class Stop(Instruction):
    def execute(self, state):
        print("STOP")
        pass
