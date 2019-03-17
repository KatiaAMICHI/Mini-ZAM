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

