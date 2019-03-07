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

    def test_add(self):
        self.vm.current_args = ["+"]
        MiniZamVM.instructions["PRIM"].execute(self.vm)
        self.assertEqual(MLValue.from_int(15), self.vm.get_accumulator())
        self.assertEqual(self.vm.stack.size(), 2)
        self.assertEqual(self.vm.peek(), MLValue.from_int(2))

        # TODO check when in acc there is a closure and expect error typeError / or in Stack
