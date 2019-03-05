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
        print(chr(one.value))


###########################################
class Const(Instruction):
    def execute(self, state):
        state.set_accumulator(MLValue.from_int(int(state.fetch()[0])))
        state.increment_pc()


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
        label = state.fetch()[0]
        state.set_pc(state.get_position(label))


class BranchIfNot(Instruction):
    def execute(self, state):
        label = state.fetch()
        acc = state.get_accumulator()
        if acc.value == 0:
            state.set_pc(state.get_position(label[0]))
        else:
            state.increment_pc()


class Push(Instruction):
    def execute(self, state):
        state.push(state.get_accumulator())
        state.increment_pc()


class Pop(Instruction):
    def execute(self, state):
        state.pop()
        state.increment_pc()


class Acc(Instruction):
    def execute(self, state):
        state.set_accumulator(state.peek(int(state.fetch()[0])))
        state.increment_pc()


class EnvAcc(Instruction):
    def execute(self, state):
        print(" state.get_env(int(state.fetch()[0])) : ", state.get_env(int(state.fetch()[0])))
        state.set_accumulator(MLValue.from_int(state.get_env(int(state.fetch()[0]))))
        state.increment_pc()


class Closure(Instruction):

    def execute(self, state):
        (label, n) = tuple(state.fetch())
        n = int(n)
        vals_pop = state.pop(n - 1)
        vals_pop = (vals_pop if isinstance(vals_pop, list) else [vals_pop])

        acc = state.get_accumulator()
        if n > 0:
            state.push(acc)

        state.set_accumulator(MLValue.from_closure(state.get_position(label), vals_pop))

        state.increment_pc()


class ClosureRec(Instruction):
    def execute(self, state):
        (label, n) = tuple(state.fetch())
        n = int(n)
        vals_pop = state.pop(n - 1)
        vals_pop = (vals_pop if isinstance(vals_pop, list) else [vals_pop])

        acc = state.get_accumulator()
        if n > 0:
            state.push(acc)

        acc = MLValue.from_closure(state.get_position(label), [state.get_position(label)] + vals_pop)
        state.set_accumulator(acc)
        state.push(acc)

        state.increment_pc()


class OffSetClosure(Instruction):
    def execute(self, state):
        state.set_accumulator(MLValue.from_closure(state.get_env(0), state.get_env()))
        state.increment_pc()


class Apply(Instruction):
    def execute(self, state):
        n = int(state.fetch()[0])

        args = state.pop(n)

        env = state.get_env()
        pc = state.get_pc() + 1
        extra_args = state.get_extra_args()

        state.push(args + [pc] + [env] + [extra_args])

        acc = state.get_accumulator()
        state.change_context(acc)
        state.set_extra_args(n - 1)


class ReStart(Instruction):
    def execute(self, state):
        env = state.get_env()
        n = len(env)

        # pc prend la (n+1)-ième valeur de stack
        state.set_pc(state.peek(n + 1))
        # déplacer les éléements de env de 1 à n-1 dans la pile
        state.pop(env[1:n - 1])
        # env prend pour valeur de env[0]
        state.set_env(env[0])
        # extra args est incrémenté de (n − 1).
        state.set_extra_args(state.get_extra_args() + (n - 1))


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

            # changer les valeurs extra args, pc, env
            state.set_extra_args(state.pop())
            state.set_pc(state.pop())
            state.set_env(state.pop())


class Return(Instruction):
    def execute(self, state):
        n = int(state.fetch()[0])
        args = state.pop(n)
        if state.get_extra_args() == 0:
            # TODO on conserve le fonctionnement pr´ec´edent (mais on fera attention à
            # bien se remettre dans le contexte de l’appelant en tenant compte des modifications apport´ees
            # `a APPLY)
            pass
        else:
            state.set_extra_args(state.get_extra_args() - 1)
            state.set_env(state.pop())
            state.set_pc(state.pop())


class Stop(Instruction):
    def execute(self, state):
        print("STOP")
        pass
