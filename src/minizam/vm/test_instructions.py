import unittest
from .instructions import *
from .vm import MiniZamVM
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


class PrimTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        values = list(map(MLValue.from_int, [5, 2, 4]))
        self.vm.push(values)
        self.vm.set_accumulator(MLValue.from_int(10))

    def test_arithmetic_ops(self):
        arithmetic = {"+": 15, "-": 5, "*": 150, "/": 2}
        # "or", "and",
        # "<>", "=", "<", "<=", ">", ">="
        for op in arithmetic:
            self.do_operation(op, arithmetic[op])
            self.check_stack()
            self.check_type()

    def test_logical_ops(self):
        self.do_operation("+", 15)
        self.check_stack()
        self.check_type()

    def do_operation(self, op, result):
        self.vm.current_args = [op]
        MiniZamVM.instructions["PRIM"].execute(self.vm)
        self.assertEqual(MLValue.from_int(result), self.vm.get_accumulator())

    def check_stack(self):
        self.assertEqual(self.vm.stack.size(), 2)
        self.assertEqual(self.vm.peek(), MLValue.from_int(2))

    def check_type(self):
        self.vm.push(MLValue.from_closure(1, []))
        with self.assertRaises(TypeError):
            MiniZamVM.instructions["PRIM"].execute(self.vm)

        self.vm.set_accumulator(MLValue.from_closure(1, []))
        with self.assertRaises(TypeError):
            MiniZamVM.instructions["PRIM"].execute(self.vm)


class ClosureTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_off_set_closure(self):
        pass


class OffSetClosureTest(unittest.TestCase):
    def setUp(self):
        self.vm = MiniZamVM()
        self.env_int = [MLValue.from_int(3), MLValue.from_int(7), MLValue.from_closure(2, []), MLValue.from_int(12)]
        self.vm.set_env(self.env_int)

    def test_off_set_closure(self):
        MiniZamVM.instructions["OFFSETCLOSURE"].execute(self.vm)
        self.assertEqual(self.vm.get_accumulator(),
                         MLValue.from_closure(self.env_int[0], self.env_int))


class ApplyTest(unittest.TestCase):
    # TODO Apply
    def test_extra_args_gt__n(self):
        pass


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
        self.vm.current_args = [self.n]

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
        MiniZamVM.instructions["RETURN"].execute(vm)

        self.assertEqual(vm.get_stack().items,
                         self.stack_init[self.n + 3:])
        self.assertEqual(vm.get_pc(), self.stack_init[self.n])
        self.assertEqual(vm.get_env(), self.stack_init[self.n + 1])

    def test_extra_args_not_equal_0(self):
        vm = copy.copy(self.vm)

        MiniZamVM.instructions["RETURN"].execute(vm)
        self.assertEqual(vm.get_extra_args(), self.m - 1)
        self.assertEqual(vm.get_pc(), self.c)
        self.assertEqual(vm.get_env(), self.e)


class GrabTest(unittest.TestCase):
    def test_extra_args_gt__n(self):
        """
        extra_args > n
        """
        self.vm = MiniZamVM()

        self.m = 2
        self.c = 6
        self.n = 1

        self.vm.set_extra_args(self.m)

        self.vm.set_pc(self.c)

        self.vm.current_args = [self.n]
        self.vm.set_extra_args(self.m + self.n)

        MiniZamVM.instructions["GRAB"].execute(self.vm)

        self.assertEqual(self.vm.extra_args, self.m)

        self.assertEqual(self.vm.pc, self.c + 1)

    def test_extra_args_equal__n(self):
        """
        extra_args = n
        """
        self.vm = MiniZamVM()

        self.m = 2
        self.c = 6
        self.n = 2

        self.vm.set_extra_args(self.m)

        self.vm.set_pc(self.c)

        self.vm.current_args = [self.n]
        self.vm.set_extra_args(self.m + self.n)

        MiniZamVM.instructions["GRAB"].execute(self.vm)

        self.assertEqual(self.vm.extra_args, self.m)

        self.assertEqual(self.vm.pc, self.c + 1)

    def test_extra_args_lt_n(self):
        """
            # extra_args < n
        """
        self.vm = MiniZamVM()

        self.stack_init = [MLValue.from_int(15), MLValue.from_closure(9, []), MLValue.from_int(22),
                           MLValue.from_int(10), MLValue.from_closure(1, []), MLValue.from_int(4)]
        self.n = 3
        self.m = 2
        self.c = 6
        self.e = [MLValue.from_closure(2, [MLValue.from_int(11)])]

        # préparation de l'environnement
        self.vm.current_args = [self.n]

        self.vm.push(MLValue.from_int(4))
        self.vm.push(MLValue.from_closure(1, []))
        self.vm.push(MLValue.from_int(10))
        self.vm.push(MLValue.from_int(22))
        self.vm.push(MLValue.from_closure(9, []))
        self.vm.push(MLValue.from_int(15))

        self.vm.set_extra_args(self.m)
        self.vm.set_pc(self.c)
        self.vm.set_env(self.e)

        MiniZamVM.instructions["GRAB"].execute(self.vm)

        self.assertEqual(self.vm.get_stack().items, self.stack_init[self.m + 4:])
        self.assertEqual(self.vm.get_extra_args(), self.stack_init[self.m + 1])
        self.assertEqual(self.vm.get_pc(), self.stack_init[self.m + 2])
        self.assertEqual(self.vm.get_env(), self.stack_init[self.m + 3])
        self.assertTrue(isinstance(self.vm.get_accumulator(), MLValue))
        self.assertEqual(self.vm.get_accumulator(),
                         MLValue.from_closure(self.c - 1, [self.e] + self.stack_init[0:self.m + 1]))


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

    def test_restart(self):
        MiniZamVM.instructions["RESTART"].execute(self.vm)

        self.assertEqual(self.vm.get_stack().items, self.env_int[1:self.n - 1] + self.stack_init)
        self.assertEqual(self.vm.get_extra_args(), self.m + (self.n - 1))
        self.assertEqual(self.vm.get_env(), self.env_int[0])
