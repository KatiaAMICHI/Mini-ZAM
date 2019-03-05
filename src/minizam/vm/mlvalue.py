class MLValue:
    _TRUE = True
    _FALSE = False
    _UNIT = None

    def __init__(self):
        super().__init__()
        self.value = None

    @staticmethod
    def from_closure(pc, env):
        value = MLValue()
        value.value = (pc, env)
        return value

    @staticmethod
    def from_int(integer):
        if not isinstance(integer, int):
            raise TypeError(str(integer) + "is not an instance of int.")

        value = MLValue()
        value.value = integer
        return value

    @staticmethod
    def true():
        value = MLValue()
        value.value = MLValue._TRUE
        return value

    @staticmethod
    def false():
        value = MLValue()
        value.value = MLValue._FALSE
        return value

    @staticmethod
    def unit():
        value = MLValue()
        value.value = MLValue._UNIT
        return value

    def _check(self, other):
        if not isinstance(self.value, int):
            raise TypeError(str(self.value) + " is not an instance of int")
        if not isinstance(other, MLValue):
            raise TypeError(str(other) + " is not an instance of MLValue")
        if not isinstance(other.value, int):
            raise TypeError(str(other.value) + " is not an instance of int")

    def __repr__(self):
        if self.value is MLValue._FALSE:
            return "False"
        if self.value is MLValue._TRUE:
            return "True"
        if self.value is MLValue._UNIT:
            return "()"

        return "mlvalue(Value: %s)" % str(self.value)

    def __str__(self):
        if self.value is MLValue._FALSE:
            return "False"
        if self.value is MLValue._TRUE:
            return "True"
        if self.value is MLValue._UNIT:
            return "()"
        return "mlvalue(Value: %s)" % str(self.value)

    def __add__(self, other):
        self._check(other)
        return MLValue.from_int(self.value + other.value)

    def __sub__(self, other):
        self._check(other)
        return MLValue.from_int(self.value - other.value)

    def __mul__(self, other):
        self._check(other)
        return MLValue.from_int(self.value * other.value)

    def __truediv__(self, other):
        self._check(other)
        return MLValue.from_int(self.value / other.value)

    def __eq__(self, other):
        if self.value == other.value:
            return MLValue.true()
        else:
            return MLValue.false()

    def __ne__(self, other):
        if self.value != other.value:
            return MLValue.true()
        else:
            return MLValue.false()

    def __lt__(self, other):
        self._check(other)
        if self.value < other.value:
            return MLValue.true()
        else:
            return MLValue.false()

    def __le__(self, other):
        self._check(other)
        if self.value <= other.value:
            return MLValue.true()
        else:
            return MLValue.false()

    def __gt__(self, other):
        self._check(other)
        if self.value > other.value:
            return MLValue.true()
        else:
            return MLValue.false()

    def __ge__(self, other):
        self._check(other)
        if self.value >= other.value:
            return MLValue.true()
        else:
            return MLValue.false()

    def __bool__(self):
        if self.value is MLValue._FALSE:
            return False
        elif self.value is MLValue._TRUE:
            return True
        else:
            raise TypeError(str(self) + " is not an instance of bool")
