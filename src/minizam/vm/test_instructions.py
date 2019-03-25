import unittest
from .instructions import *
from .vm import MiniZamVM, LineInstruction
import copy


class ConstTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

    def tearDown(self):
        pass

    def test_execute(self):
        MiniZamVM.instructions["CONST"].execute(self.vm, 1)
        self.assertEqual(MLValue.from_int(1), self.vm.get_accumulator())

        with self.assertRaises(TypeError):
            MiniZamVM.instructions["CONST"].execute(self.vm, "d")

        with self.assertRaises(TypeError):
            MiniZamVM.instructions["CONST"].execute(self.vm, [1, "d"])


def check_stack(test, size, last):
    test.assertEqual(test.vm.stack.size(), size)
    test.assertEqual(test.vm.peek(), MLValue.from_int(last))


def check_type(test, apply, args):
    apply()
    with test.assertRaises(TypeError):
        MiniZamVM.instructions["PRIM"].execute(test.vm, args)


class PrimTestArithmetic(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        values = list(map(MLValue.from_int, [5, 12, 4]))
        self.vm.push(values)
        self.vm.set_accumulator(MLValue.from_int(10))

    def execute(self, op, result):
        self.do_operation(op, result)
        check_stack(self, 2, 12)
        check_type(self, lambda: self.vm.push(MLValue.from_closure(1, [])), op)
        check_type(self, lambda: self.vm.set_accumulator(MLValue.from_closure(1, [])), op)

    def test_plus(self):
        self.execute("+", 15)

    def test_minus(self):
        self.execute("-", 5)

    def test_mul(self):
        self.execute("*", 50)

    def test_div(self):
        self.execute("/", 2)

    def do_operation(self, op, result):
        MiniZamVM.instructions["PRIM"].execute(self.vm, op)
        self.assertEqual(MLValue.from_int(result), self.vm.get_accumulator())


class PrimTestLogical(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        values = list(map(MLValue.from_int, [5, 12, 4]))
        self.vm.push(values)

    def execute(self, to_push, result):
        if to_push is not None:
            self.vm.push(to_push)
        MiniZamVM.instructions["PRIM"].execute(self.vm, self.args)
        self.assertIs(result, self.vm.get_accumulator())
        check_stack(self, 3, 5)

    def test_and(self):
        self.args = "and"

        # true and true => true
        self.vm.set_accumulator(MLValue.true())
        self.execute(MLValue.true(), MLValue.true())

        # true and false => false
        self.execute(MLValue.false(), MLValue.false())

        # false and false => false
        self.execute(MLValue.false(), MLValue.false())

        check_type(self, lambda: None,"and")
        check_type(self, lambda: self.vm.set_accumulator(MLValue.from_int(1)),"and")

    def test_or(self):
        self.args = "or"

        # true or true => true
        self.vm.set_accumulator(MLValue.true())
        self.execute(MLValue.true(), MLValue.true())

        # true or false => true
        self.execute(MLValue.false(), MLValue.true())

        # false or false => false
        self.vm.set_accumulator(MLValue.false())
        self.execute(MLValue.false(), MLValue.false())

        check_type(self, lambda: None,"or")
        check_type(self, lambda: self.vm.set_accumulator(MLValue.from_int(1)),"or")

    def test_not(self):
        self.args = "not"

        # not true => false
        self.vm.set_accumulator(MLValue.true())
        self.execute(None, MLValue.false())

        # not false => true
        self.execute(None, MLValue.true())

        check_type(self, lambda: self.vm.set_accumulator(MLValue.from_int(1)),"not")


class PrimTestComparison(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

    def execute(self, op, result):
        MiniZamVM.instructions["PRIM"].execute(self.vm, op)
        self.assertIs(result, self.vm.get_accumulator())

    def prepare(self, acc, to_psuh):
        self.vm.set_accumulator(acc)
        self.vm.push(to_psuh)

    def test_notEq(self):
        self.prepare(MLValue.from_int(5), MLValue.from_int(2))
        self.execute("<>", MLValue.true())
        self.prepare(MLValue.from_int(5), MLValue.from_int(5))
        self.execute("<>", MLValue.false())

    def test_eq(self):
        self.prepare(MLValue.from_int(5), MLValue.from_int(2))
        self.execute("=", MLValue.false())
        self.prepare(MLValue.from_int(5), MLValue.from_int(5))
        self.execute("=", MLValue.true())

    def test_lt(self):
        self.prepare(MLValue.from_int(5), MLValue.from_int(2))
        self.execute("<", MLValue.false())
        self.prepare(MLValue.from_int(5), MLValue.from_int(10))
        self.execute("<", MLValue.true())
        self.prepare(MLValue.from_int(5), MLValue.from_int(5))
        self.execute("<", MLValue.false())

    def test_ltEq(self):
        self.prepare(MLValue.from_int(5), MLValue.from_int(2))
        self.execute("<=", MLValue.false())
        self.prepare(MLValue.from_int(5), MLValue.from_int(10))
        self.execute("<=", MLValue.true())
        self.prepare(MLValue.from_int(5), MLValue.from_int(5))
        self.execute("<=", MLValue.true())

    def test_gt(self):
        self.prepare(MLValue.from_int(5), MLValue.from_int(2))
        self.execute(">=", MLValue.true())
        self.prepare(MLValue.from_int(5), MLValue.from_int(10))
        self.execute(">", MLValue.false())
        self.prepare(MLValue.from_int(5), MLValue.from_int(5))
        self.execute(">", MLValue.false())

    def test_gtEq(self):
        self.prepare(MLValue.from_int(5), MLValue.from_int(2))
        self.execute(">=", MLValue.true())
        self.prepare(MLValue.from_int(5), MLValue.from_int(10))
        self.execute(">=", MLValue.false())
        self.prepare(MLValue.from_int(5), MLValue.from_int(5))
        self.execute(">=", MLValue.true())


class BranchTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        lines = [("", "CONST", "1"), ("", "PRIM", "print"), ("", "BRANCH", "L"),
                 ("", "PUSH", ""), ("L", "CONST", "2"), ("", "PUSH", "")]
        self.vm.pc = 2
        self.vm.prog = list(map(LineInstruction.build, lines))

    def test_execute(self):
        MiniZamVM.instructions["BRANCH"].execute(self.vm, "L")
        self.assertEqual(4, self.vm.pc)


class BranchIfNotTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        lines = [("", "CONST", "1"), ("", "PRIM", "print"), ("", "BRANCHIFNOT", "L"),
                 ("", "PUSH", ""), ("L", "CONST", "2"), ("", "PUSH", "")]
        self.vm.pc = 2
        self.vm.prog = list(map(LineInstruction.build, lines))

    def test_execute(self):
        self.vm.set_accumulator(MLValue.false())
        MiniZamVM.instructions["BRANCHIFNOT"].execute(self.vm, "L")
        self.assertEqual(4, self.vm.pc)
        self.vm.pc = 2
        self.vm.set_accumulator(MLValue.true())
        MiniZamVM.instructions["BRANCHIFNOT"].execute(self.vm, "L")
        self.assertEqual(2, self.vm.pc)


class PushTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

    def test_execute(self):
        self.vm.set_accumulator(MLValue.from_int(5))
        MiniZamVM.instructions["PUSH"].execute(self.vm, None)
        self.assertEqual(MLValue.from_int(5), self.vm.peek())
        self.vm.set_accumulator(MLValue.from_int(10))
        MiniZamVM.instructions["PUSH"].execute(self.vm, None)
        self.assertEqual(MLValue.from_int(10), self.vm.peek())
        self.assertEqual(2, self.vm.stack.size())


class PopTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.push(list(map(MLValue.from_int, [1, 2, 5])))

    def test_execute(self):
        MiniZamVM.instructions["POP"].execute(self.vm, None)
        self.assertEqual(2, self.vm.stack.size())
        MiniZamVM.instructions["POP"].execute(self.vm, None)
        MiniZamVM.instructions["POP"].execute(self.vm, None)
        self.assertEqual(0, self.vm.stack.size())
        MiniZamVM.instructions["POP"].execute(self.vm, None)
        self.assertEqual(0, self.vm.stack.size())


class AccTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.push(list(map(MLValue.from_int, [1, 2, 5])))
        self.vm.push(MLValue.from_closure(1, []))

    def execute(self, i, result):
        MiniZamVM.instructions["ACC"].execute(self.vm, i)
        self.assertEqual(4, self.vm.stack.size())
        self.assertEqual(result, self.vm.get_accumulator())

    def test_execute(self):
        self.execute(1, MLValue.from_int(1))
        self.execute(3, MLValue.from_int(5))
        self.execute(0, MLValue.from_closure(1, []))
        with self.assertRaises(IndexError):
            self.execute(5, None)


class EnvAccTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.env = list(map(MLValue.from_int, [1, 2, 5]))

    def execute(self, i, result):
        MiniZamVM.instructions["ENVACC"].execute(self.vm, i)
        self.assertEqual(result, self.vm.get_accumulator())

    def test_execute(self):
        self.execute(0, MLValue.from_int(1))
        self.execute(2, MLValue.from_int(5))
        with self.assertRaises(IndexError):
            self.execute(5, None)


class ClosureTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.push(list(map(MLValue.from_int, [1, 2, 5])))
        lines = [("", "CONST", "1"), ("", "PRIM", "print"),
                 ("", "PUSH", ""), ("L", "CONST", "2"), ("", "PUSH", "")]
        self.vm.pc = 2
        self.vm.prog = list(map(LineInstruction.build, lines))

    def test_execute(self):
        MiniZamVM.instructions["CLOSURE"].execute(self.vm, ["L", 0])
        self.assertEqual(MLValue.from_closure(3, []), self.vm.get_accumulator())
        self.assertEqual(3, self.vm.stack.size())

        self.vm.set_accumulator(MLValue.false())
        MiniZamVM.instructions["CLOSURE"].execute(self.vm, ["L", 2])
        self.assertEqual(MLValue.from_closure(3, [MLValue.false(), MLValue.from_int(1)]), self.vm.get_accumulator())
        self.assertEqual(2, self.vm.stack.size())


class ClosureRecTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.push(list(map(MLValue.from_int, [1, 2, 5])))
        lines = [("", "CONST", "1"), ("", "PRIM", "print"),
                 ("", "PUSH", ""), ("L", "CONST", "2"), ("", "PUSH", "")]
        self.vm.pc = 2
        self.vm.prog = list(map(LineInstruction.build, lines))

    def test_execute(self):
        MiniZamVM.instructions["CLOSUREREC"].execute(self.vm, ["L", 0])
        self.assertEqual(MLValue.from_closure(3, [3]), self.vm.get_accumulator())
        self.assertEqual(4, self.vm.stack.size())

        # undo last push by CLOSUREREC
        self.vm.pop()

        # setup acc
        self.vm.set_accumulator(MLValue.false())
        # test with n > 0
        MiniZamVM.instructions["CLOSUREREC"].execute(self.vm, ["L", 2])
        self.assertEqual(MLValue.from_closure(3, [3, MLValue.false(), MLValue.from_int(1)]), self.vm.get_accumulator())
        self.assertEqual(3, self.vm.stack.size())


class OffSetClosureTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.env_int = [MLValue.from_int(3), MLValue.from_int(7), MLValue.from_closure(2, []), MLValue.from_int(12)]
        self.vm.set_env(self.env_int)

    def test_off_set_closure(self):
        MiniZamVM.instructions["OFFSETCLOSURE"].execute(self.vm, None)
        self.assertEqual(self.vm.get_accumulator(), MLValue.from_closure(self.env_int[0], self.env_int))


class ApplyTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.push(list(map(MLValue.from_int, [1, 2, 5])))
        self.vm.pc = 15
        self.env = list(map(MLValue.from_int, [5, 3, 6]))
        self.vm.env = self.env
        self.vm.set_accumulator(MLValue.from_closure(5, []))

    def test_execute(self):
        MiniZamVM.instructions["APPLY"].execute(self.vm, 2)
        self.assertEqual([], self.vm.env)
        self.assertEqual(5, self.vm.pc)

        expected = list(map(MLValue.from_int, [1, 2])) + [15, self.env, 0]
        # nargs=2 + pc + env + extra_args  == 5
        self.assertEqual(expected, self.vm.pop(5))

        self.assertEqual(1, self.vm.extra_args)


class ReturnTest(unittest.TestCase):
    stack_init = None

    def setUp(self):
        self.vm = MiniZamVM()

        self.stack_init = [MLValue.from_int(15), MLValue.from_closure(9, []), MLValue.from_int(22),
                           MLValue.from_int(10), MLValue.from_closure(1, []), MLValue.from_int(4)]
        self.n = 2
        self.m = 2
        self.c = 6
        self.e = [MLValue.from_closure(2, [MLValue.from_int(11)])]

        # préparation de l'environnement

        self.vm.push(MLValue.from_int(4))
        self.vm.push(MLValue.from_closure(1, []))
        self.vm.push(MLValue.from_int(10))
        self.vm.push(MLValue.from_int(22))
        self.vm.push(MLValue.from_closure(9, []))
        self.vm.push(MLValue.from_int(15))

        self.vm.set_extra_args(self.m)
        self.vm.set_accumulator(MLValue.from_closure(self.c, self.e))

    def test_extra_args_equal_0(self):
        """
        extra_args = 0
        """
        vm = copy.copy(self.vm)

        vm.set_extra_args(0)
        MiniZamVM.instructions["RETURN"].execute(vm, self.n)

        self.assertEqual(vm.get_stack().items,
                         self.stack_init[self.n + 3:])
        self.assertEqual(vm.get_pc(), self.stack_init[self.n])
        self.assertEqual(vm.get_env(), self.stack_init[self.n + 1])

    def test_extra_args_not_equal_0(self):
        vm = copy.copy(self.vm)

        MiniZamVM.instructions["RETURN"].execute(vm, self.n)
        self.assertEqual(vm.get_extra_args(), self.m - 1)
        self.assertEqual(vm.get_pc(), self.c)
        self.assertEqual(vm.get_env(), self.e)


class ReStartTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.stack_init = [MLValue.from_int(10), MLValue.from_closure(1, []), MLValue.from_int(4)]
        self.env_int = [MLValue.from_int(3), MLValue.from_int(7), MLValue.from_closure(2, []), MLValue.from_int(12)]
        self.m = 3

        self.vm.push(MLValue.from_int(4))
        self.vm.push(MLValue.from_closure(1, []))
        self.vm.push(MLValue.from_int(10))
        self.vm.set_extra_args(self.m)
        self.vm.set_env(self.env_int)
        self.n = len(self.vm.get_env())

    def test_execute(self):
        MiniZamVM.instructions["RESTART"].execute(self.vm, None)

        self.assertEqual(self.vm.get_stack().items, self.env_int[1:self.n] + self.stack_init)
        self.assertEqual(self.vm.get_extra_args(), self.m + (self.n - 1))
        self.assertEqual(self.vm.get_env(), self.env_int[0])


class GrabTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

        self.m = 2
        self.c = 6
        self.n = 1
        self.e = [MLValue.from_closure(2, [MLValue.from_int(11)])]
        self.stack_init = [MLValue.from_int(15), MLValue.from_closure(9, []), MLValue.from_int(22),
                           MLValue.from_int(10), MLValue.from_closure(1, []), MLValue.from_int(4)]

        self.vm.set_extra_args(self.m)

        self.vm.set_pc(self.c)

        self.vm.set_extra_args(self.m + self.n)

    def test_execute(self):
        # extra_args > n
        MiniZamVM.instructions["GRAB"].execute(self.vm, self.n)
        self.assertEqual(self.vm.extra_args, self.m)

        # extra_args = n
        self.setUp()
        self.m = 2
        MiniZamVM.instructions["GRAB"].execute(self.vm, self.n)
        self.assertEqual(self.vm.extra_args, self.m)

        # extra_args < n
        self.setUp()
        self.n = 3

        self.vm.push(MLValue.from_int(4))
        self.vm.push(MLValue.from_closure(1, []))
        self.vm.push(MLValue.from_int(10))
        self.vm.push(MLValue.from_int(22))
        self.vm.push(MLValue.from_closure(9, []))
        self.vm.push(MLValue.from_int(15))

        self.vm.set_extra_args(self.m)
        self.vm.set_pc(self.c)
        self.vm.set_env(self.e)

        MiniZamVM.instructions["GRAB"].execute(self.vm, self.n)

        self.assertEqual(self.vm.get_stack().items, self.stack_init[self.m + 4:])
        pc = self.stack_init[self.m + 1]
        self.assertEqual(self.vm.get_pc(), pc)
        self.assertEqual(self.vm.get_env(), self.stack_init[self.m + 2])
        self.assertEqual(self.vm.get_extra_args(), self.stack_init[self.m + 3])
        self.assertEqual(self.vm.get_accumulator(),
                         MLValue.from_closure(self.c - 2, [self.e] + self.stack_init[0:self.m + 1]))


class MakeBlockTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

        self.n = 2
        stack_init = [MLValue.from_int(10), MLValue.from_closure(1, []), MLValue.from_int(4)]
        accu = MLValue.from_int(1)
        self.block = [accu] + stack_init[0:self.n - 1]

        self.vm.set_accumulator(accu)

        self.vm.push(list(map(MLValue.from_int, [10, 1, 4])))

    def test_execute(self):
        MiniZamVM.instructions["MAKEBLOCK"].execute(self.vm, self.n)

        self.assertEqual(self.vm.get_accumulator().value, self.block)


class GetFieldTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

        self.n = 1
        self.accu_vals = [MLValue.from_int(1), MLValue.from_int(8), MLValue.from_int(4)]

        self.vm.set_accumulator(MLValue.from_block(self.accu_vals))

    def test_execute(self):
        MiniZamVM.instructions["GETFIELD"].execute(self.vm, self.n)
        self.assertEqual(self.vm.get_accumulator(), self.accu_vals[self.n])


class VectLengthTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

        self.val_block = [MLValue.from_int(1), MLValue.from_closure(1, []), MLValue.from_int(10)]

        self.vm.set_accumulator(MLValue.from_block(self.val_block))

    def test_execute(self):
        MiniZamVM.instructions["VECTLENGTH"].execute(self.vm, None)
        self.assertEqual(self.vm.get_accumulator(), MLValue.from_int(len(self.val_block)))


class GetVectItemTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

        self.val_stack = [MLValue.from_int(1), MLValue.from_int(3), MLValue.from_int(36)]
        self.val_block = [MLValue.from_closure(1, []), MLValue.from_int(10)]
        self.vm.set_accumulator(MLValue.from_block(self.val_block))
        self.vm.push(list(map(MLValue.from_int, [1, 3, 36])))

    def test_execute(self):
        MiniZamVM.instructions["GETVECTITEM"].execute(self.vm, None)

        self.assertEqual(self.vm.get_stack().items, self.val_stack[1:])
        self.assertTrue(isinstance(self.vm.get_accumulator(), MLValue))
        self.assertEqual(self.vm.get_accumulator(), self.val_block[1])


class SetFieldTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

        self.n = 1
        self.val_stack = [MLValue.from_int(4), MLValue.from_int(3), MLValue.from_int(36)]
        self.val_block = [MLValue.from_closure(1, []), MLValue.from_int(10)]

        self.vm.set_accumulator(MLValue.from_block(self.val_block))
        self.vm.push(list(map(MLValue.from_int, [4, 3, 36])))

    def test_execute(self):
        MiniZamVM.instructions["SETFIELD"].execute(self.vm, self.n)
        self.assertEqual(self.vm.get_accumulator().value, [self.val_block[0]] + [self.val_stack[0]])


class SetVectItemTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

        self.val_stack = [MLValue.from_int(1), MLValue.from_int(3), MLValue.from_int(36)]
        self.val_block = [MLValue.from_closure(1, []), MLValue.from_int(10)]

        self.vm.set_accumulator(MLValue.from_block(self.val_block))
        self.vm.push(MLValue.from_block(self.val_block))
        self.vm.push(list(map(MLValue.from_int, [1, 3, 36])))

    def test_execute(self):
        MiniZamVM.instructions["SETVECTITEM"].execute(self.vm, None)
        self.val_block[1] = MLValue.from_int(3)
        stack_res = self.val_stack[2::] + [MLValue.from_block(self.val_block)]

        self.assertEqual(self.vm.get_accumulator(), MLValue.unit())
        self.assertEqual(self.vm.get_stack().items, stack_res)


class AssignTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.n = 1

        self.val_stack = [MLValue.from_int(1), MLValue.from_int(3), MLValue.from_int(36)]
        self.val_block = [MLValue.from_closure(1, []), MLValue.from_int(10)]

        self.vm.set_accumulator(MLValue.from_block(self.val_block))
        self.vm.push(list(map(MLValue.from_int, [1, 3, 36])))

    def test_exeucte(self):
        MiniZamVM.instructions["ASSIGN"].execute(self.vm, self.n)

        self.val_stack[self.n] = MLValue.from_block(self.val_block)

        self.assertEqual(self.vm.get_stack().items, self.val_stack)
        self.assertEqual(self.vm.get_accumulator(), MLValue.unit())


