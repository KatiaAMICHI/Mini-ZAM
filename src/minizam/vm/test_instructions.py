import unittest
from .instructions import *
from .vm import MiniZamVM


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
        self.vm.push([MLValue.from_int(5), MLValue.from_int(2), MLValue.from_int(4)])
        self.vm.set_accumulator(MLValue.from_int(10))

    def do_operation(self, op, result):
        self.vm.current_args = [op]
        MiniZamVM.instructions["PRIM"].execute(self.vm)
        self.assertEqual(MLValue.from_int(result), self.vm.get_accumulator())
        self.assertEqual(self.vm.stack.size(), 2)
        self.assertEqual(self.vm.peek(), MLValue.from_int(2))

    def test_add_minus_mul_div(self):
        self.do_operation("+", 15)
        self.do_operation("-", 5)
        self.do_operation("*", 150)
        self.do_operation("/", 2)

        # TODO check when in acc there is a closure and expect error typeError / or in Stack

    def test_or_and(self):
        pass

    def test_notEq_eq_lt_gt_ltEq_gtEq(self):
        pass


class BranchTest(unittest.TestCase):
    pass


class BranchIfNotTest(unittest.TestCase):
    pass

