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
        self.vm.current_args = [1]
        MiniZamVM.instructions["CONST"].execute(self.vm)
        self.assertEqual(MLValue.from_int(1), self.vm.get_accumulator())

        self.vm.current_args = ["d"]

        with self.assertRaises(ValueError):
            MiniZamVM.instructions["CONST"].execute(self.vm)

        self.vm.current_args = [1, "d"]
        with self.assertRaises(ValueError):
            MiniZamVM.instructions["CONST"].execute(self.vm)


def check_stack(test, size, last):
    test.assertEqual(test.vm.stack.size(), size)
    test.assertEqual(test.vm.peek(), MLValue.from_int(last))


def check_type(test, apply):
    apply()
    with test.assertRaises(TypeError):
        MiniZamVM.instructions["PRIM"].execute(test.vm)


class PrimTestArithmetic(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        values = list(map(MLValue.from_int, [5, 12, 4]))
        self.vm.push(values)
        self.vm.set_accumulator(MLValue.from_int(10))

    def execute(self, op, result):
        self.do_operation(op, result)
        check_stack(self, 2, 12)
        check_type(self, lambda: self.vm.push(MLValue.from_closure(1, [])))
        check_type(self, lambda: self.vm.set_accumulator(MLValue.from_closure(1, [])))

    def test_plus(self):
        self.execute("+", 15)

    def test_minus(self):
        self.execute("-", 5)

    def test_mul(self):
        self.execute("*", 50)

    def test_div(self):
        self.execute("/", 2)

    def do_operation(self, op, result):
        self.vm.current_args = [op]
        MiniZamVM.instructions["PRIM"].execute(self.vm)
        self.assertEqual(MLValue.from_int(result), self.vm.get_accumulator())


class PrimTestLogical(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        values = list(map(MLValue.from_int, [5, 12, 4]))
        self.vm.push(values)

    def execute(self, to_push, result):
        if to_push is not None:
            self.vm.push(to_push)
        MiniZamVM.instructions["PRIM"].execute(self.vm)
        self.assertIs(result, self.vm.get_accumulator())
        check_stack(self, 3, 5)

    def test_and(self):
        self.vm.current_args = ["and"]

        # true and true => true
        self.vm.set_accumulator(MLValue.true())
        self.execute(MLValue.true(), MLValue.true())

        # true and false => false
        self.execute(MLValue.false(), MLValue.false())

        # false and false => false
        self.execute(MLValue.false(), MLValue.false())

        check_type(self, lambda: None)
        check_type(self, lambda: self.vm.set_accumulator(MLValue.from_int(1)))

    def test_or(self):
        self.vm.current_args = ["or"]

        # true or true => true
        self.vm.set_accumulator(MLValue.true())
        self.execute(MLValue.true(), MLValue.true())

        # true or false => true
        self.execute(MLValue.false(), MLValue.true())

        # false or false => false
        self.vm.set_accumulator(MLValue.false())
        self.execute(MLValue.false(), MLValue.false())

        check_type(self, lambda: None)
        check_type(self, lambda: self.vm.set_accumulator(MLValue.from_int(1)))

    def test_not(self):
        self.vm.current_args = ["not"]

        # not true => false
        self.vm.set_accumulator(MLValue.true())
        self.execute(None, MLValue.false())

        # not false => true
        self.execute(None, MLValue.true())

        check_type(self, lambda: self.vm.set_accumulator(MLValue.from_int(1)))


class PrimTestComparison(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

    def execute(self, op, result):
        self.vm.current_args = [op]
        MiniZamVM.instructions["PRIM"].execute(self.vm)
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
        self.vm.current_args = ["L"]
        self.vm.pc = 2
        self.vm.prog = list(map(LineInstruction.build, lines))

    def test_execute(self):
        MiniZamVM.instructions["BRANCH"].execute(self.vm)
        self.assertEqual(4, self.vm.pc)


class BranchIfNotTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        lines = [("", "CONST", "1"), ("", "PRIM", "print"), ("", "BRANCHIFNOT", "L"),
                 ("", "PUSH", ""), ("L", "CONST", "2"), ("", "PUSH", "")]
        self.vm.current_args = ["L"]
        self.vm.pc = 2
        self.vm.prog = list(map(LineInstruction.build, lines))

    def test_execute(self):
        self.vm.set_accumulator(MLValue.false())
        MiniZamVM.instructions["BRANCHIFNOT"].execute(self.vm)
        self.assertEqual(4, self.vm.pc)
        self.vm.pc = 2
        self.vm.set_accumulator(MLValue.true())
        MiniZamVM.instructions["BRANCHIFNOT"].execute(self.vm)
        self.assertEqual(2, self.vm.pc)


class PushTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

    def test_execute(self):
        self.vm.set_accumulator(MLValue.from_int(5))
        MiniZamVM.instructions["PUSH"].execute(self.vm)
        self.assertEqual(MLValue.from_int(5), self.vm.peek())
        self.vm.set_accumulator(MLValue.from_int(10))
        MiniZamVM.instructions["PUSH"].execute(self.vm)
        self.assertEqual(MLValue.from_int(10), self.vm.peek())
        self.assertEqual(2, self.vm.stack.size())


class PopTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.push(list(map(MLValue.from_int, [1, 2, 5])))

    def test_execute(self):
        MiniZamVM.instructions["POP"].execute(self.vm)
        self.assertEqual(2, self.vm.stack.size())
        MiniZamVM.instructions["POP"].execute(self.vm)
        MiniZamVM.instructions["POP"].execute(self.vm)
        self.assertEqual(0, self.vm.stack.size())
        MiniZamVM.instructions["POP"].execute(self.vm)
        self.assertEqual(0, self.vm.stack.size())


class AccTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.push(list(map(MLValue.from_int, [1, 2, 5])))
        self.vm.push(MLValue.from_closure(1, []))

    def execute(self, i, result):
        self.vm.current_args = [i]
        MiniZamVM.instructions["ACC"].execute(self.vm)
        self.assertEqual(4, self.vm.stack.size())
        self.assertEqual(result, self.vm.get_accumulator())

    def test_execute(self):
        self.execute("1", MLValue.from_int(1))
        self.execute("3", MLValue.from_int(5))
        self.execute("0", MLValue.from_closure(1, []))
        with self.assertRaises(IndexError):
            self.execute("5", None)


class EnvAccTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.vm.env = list(map(MLValue.from_int, [1, 2, 5]))

    def execute(self, i, result):
        self.vm.current_args = [i]
        MiniZamVM.instructions["ENVACC"].execute(self.vm)
        self.assertEqual(result, self.vm.get_accumulator())

    def test_execute(self):
        self.execute("0", MLValue.from_int(1))
        self.execute("2", MLValue.from_int(5))
        with self.assertRaises(IndexError):
            self.execute("5", None)


class ClosureTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()

    def test_off_set_closure(self):
        pass

#
# class OffSetClosureTest(unittest.TestCase):
#     def setUp(self):
#         self.vm = MiniZamVM()
#         self.env_int = [MLValue.from_int(3), MLValue.from_int(7), MLValue.from_closure(2, []), MLValue.from_int(12)]
#         self.vm.set_env(self.env_int)
#
#     def test_off_set_closure(self):
#         MiniZamVM.instructions["OFFSETCLOSURE"].execute(self.vm)
#         self.assertEqual(self.vm.get_accumulator(),
#                          MLValue.from_closure(self.env_int[0], self.env_int))
#
#
# class ApplyTest(unittest.TestCase):
#     # TODO Apply
#     def test_extra_args_gt__n(self):
#         pass
#
#
# class ReturnTest(unittest.TestCase):
#     stack_init = None
#
#     def setUp(self):
#         self.vm = MiniZamVM()
#
#         self.stack_init = [MLValue.from_int(15), MLValue.from_closure(9, []), MLValue.from_int(22),
#                            MLValue.from_int(10), MLValue.from_closure(1, []), MLValue.from_int(4)]
#         self.n = 2
#         self.m = 2
#         self.c = 6
#         self.e = [MLValue.from_closure(2, [MLValue.from_int(11)])]
#
#         # préparation de l'environnement
#         self.vm.current_args = [self.n]
#
#         self.vm.push(MLValue.from_int(4))
#         self.vm.push(MLValue.from_closure(1, []))
#         self.vm.push(MLValue.from_int(10))
#         self.vm.push(MLValue.from_int(22))
#         self.vm.push(MLValue.from_closure(9, []))
#         self.vm.push(MLValue.from_int(15))
#
#         self.vm.set_extra_args(self.m)
#         self.vm.set_accumulator(MLValue.from_closure(self.c, self.e))
#
#     def test_extra_args_equal_0(self):
#         """
#         extra_args = 0
#         """
#         vm = copy.copy(self.vm)
#
#         vm.set_extra_args(0)
#         MiniZamVM.instructions["RETURN"].execute(vm)
#
#         self.assertEqual(vm.get_stack().items,
#                          self.stack_init[self.n + 3:])
#         self.assertEqual(vm.get_pc(), self.stack_init[self.n])
#         self.assertEqual(vm.get_env(), self.stack_init[self.n + 1])
#
#     def test_extra_args_not_equal_0(self):
#         vm = copy.copy(self.vm)
#
#         MiniZamVM.instructions["RETURN"].execute(vm)
#         self.assertEqual(vm.get_extra_args(), self.m - 1)
#         self.assertEqual(vm.get_pc(), self.c)
#         self.assertEqual(vm.get_env(), self.e)
#
#
# class GrabTest(unittest.TestCase):
#     def test_extra_args_gt__n(self):
#         """
#         extra_args > n
#         """
#         self.vm = MiniZamVM()
#
#         self.m = 2
#         self.c = 6
#         self.n = 1
#
#         self.vm.set_extra_args(self.m)
#
#         self.vm.set_pc(self.c)
#
#         self.vm.current_args = [self.n]
#         self.vm.set_extra_args(self.m + self.n)
#
#         MiniZamVM.instructions["GRAB"].execute(self.vm)
#
#         self.assertEqual(self.vm.extra_args, self.m)
#
#         self.assertEqual(self.vm.pc, self.c + 1)
#
#     def test_extra_args_equal__n(self):
#         """
#         extra_args = n
#         """
#         self.vm = MiniZamVM()
#
#         self.m = 2
#         self.c = 6
#         self.n = 2
#
#         self.vm.set_extra_args(self.m)
#
#         self.vm.set_pc(self.c)
#
#         self.vm.current_args = [self.n]
#         self.vm.set_extra_args(self.m + self.n)
#
#         MiniZamVM.instructions["GRAB"].execute(self.vm)
#
#         self.assertEqual(self.vm.extra_args, self.m)
#
#         self.assertEqual(self.vm.pc, self.c + 1)
#
#     def test_extra_args_lt_n(self):
#         """
#             # extra_args < n
#         """
#         self.vm = MiniZamVM()
#
#         self.stack_init = [MLValue.from_int(15), MLValue.from_closure(9, []), MLValue.from_int(22),
#                            MLValue.from_int(10), MLValue.from_closure(1, []), MLValue.from_int(4)]
#         self.n = 3
#         self.m = 2
#         self.c = 6
#         self.e = [MLValue.from_closure(2, [MLValue.from_int(11)])]
#
#         # préparation de l'environnement
#         self.vm.current_args = [self.n]
#
#         self.vm.push(MLValue.from_int(4))
#         self.vm.push(MLValue.from_closure(1, []))
#         self.vm.push(MLValue.from_int(10))
#         self.vm.push(MLValue.from_int(22))
#         self.vm.push(MLValue.from_closure(9, []))
#         self.vm.push(MLValue.from_int(15))
#
#         self.vm.set_extra_args(self.m)
#         self.vm.set_pc(self.c)
#         self.vm.set_env(self.e)
#
#         MiniZamVM.instructions["GRAB"].execute(self.vm)
#
#         self.assertEqual(self.vm.get_stack().items, self.stack_init[self.m + 4:])
#         self.assertEqual(self.vm.get_extra_args(), self.stack_init[self.m + 1])
#         self.assertEqual(self.vm.get_pc(), self.stack_init[self.m + 2])
#         self.assertEqual(self.vm.get_env(), self.stack_init[self.m + 3])
#         self.assertTrue(isinstance(self.vm.get_accumulator(), MLValue))
#         self.assertEqual(self.vm.get_accumulator(),
#                          MLValue.from_closure(self.c - 1, [self.e] + self.stack_init[0:self.m + 1]))
#
#
# class ReStartTest(unittest.TestCase):
#     def setUp(self):
#         self.vm = MiniZamVM()
#         self.stack_init = [MLValue.from_int(10), MLValue.from_closure(1, []), MLValue.from_int(4)]
#         self.env_int = [MLValue.from_int(3), MLValue.from_int(7), MLValue.from_closure(2, []), MLValue.from_int(12)]
#         self.m = 3
#
#         self.vm.push(MLValue.from_int(4))
#         self.vm.push(MLValue.from_closure(1, []))
#         self.vm.push(MLValue.from_int(10))
#
#         self.vm.set_extra_args(self.m)
#
#         self.vm.set_env(self.env_int)
#
#         self.n = len(self.vm.get_env())
#
#     def test_restart(self):
#         MiniZamVM.instructions["RESTART"].execute(self.vm)
#
#         self.assertEqual(self.vm.get_stack().items, self.env_int[1:self.n - 1] + self.stack_init)
#         self.assertEqual(self.vm.get_extra_args(), self.m + (self.n - 1))
#         self.assertEqual(self.vm.get_env(), self.env_int[0])
