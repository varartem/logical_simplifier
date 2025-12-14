class LogicExpression:
    """Базовый класс для логических выражений."""

    def simplify(self):
        """Упрощает выражение."""
        return self

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __str__(self):
        return self._str()

    def _str(self):
        raise NotImplementedError


class Variable(LogicExpression):
    """Логическая переменная."""

    def __init__(self, name):
        self.name = name

    def simplify(self):
        return self

    def _str(self):
        return self.name


class Constant(LogicExpression):
    """Логическая константа (True/False)."""

    def __init__(self, value):
        self.value = value

    def simplify(self):
        return self

    def _str(self):
        return "True" if self.value else "False"


class Not(LogicExpression):
    """Логическое отрицание."""

    def __init__(self, operand):
        self.operand = operand

    def simplify(self):
        # Упрощаем операнд
        simplified_operand = self.operand.simplify()

        # Закон двойного отрицания: not(not A) = A
        if isinstance(simplified_operand, Not):
            return simplified_operand.operand.simplify()

        # not(True) = False, not(False) = True
        if isinstance(simplified_operand, Constant):
            return Constant(not simplified_operand.value)

        return Not(simplified_operand)

    def _str(self):
        if isinstance(self.operand, (Variable, Constant)):
            return f"not {self.operand}"
        return f"not ({self.operand})"


class And(LogicExpression):
    """Логическое И."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def simplify(self):
        # Упрощаем операнды
        left = self.left.simplify()
        right = self.right.simplify()

        # A and False = False
        if isinstance(left, Constant) and not left.value:
            return Constant(False)
        if isinstance(right, Constant) and not right.value:
            return Constant(False)

        # A and True = A
        if isinstance(left, Constant) and left.value:
            return right
        if isinstance(right, Constant) and right.value:
            return left

        # A and A = A (идемпотентность)
        if left.__class__ == right.__class__ and left.__dict__ == right.__dict__:
            return left

        # (A or not A) and B = B (закон исключенного третьего)
        if self._is_excluded_middle(left):
            return right
        if self._is_excluded_middle(right):
            return left

        return And(left, right)

    def _is_excluded_middle(self, expr):
        """Проверяет, является ли выражение законом исключенного третьего: A or not A"""
        if isinstance(expr, Or):
            left_is_var = isinstance(expr.left, Variable)
            right_is_var = isinstance(expr.right, Variable)
            left_is_not = isinstance(expr.left, Not) and isinstance(expr.left.operand, Variable)
            right_is_not = isinstance(expr.right, Not) and isinstance(expr.right.operand, Variable)

            if left_is_var and right_is_not and expr.left.name == expr.right.operand.name:
                return True
            if left_is_not and right_is_var and expr.left.operand.name == expr.right.name:
                return True
        return False

    def _str(self):
        left_str = f"({self.left})" if isinstance(self.left, Or) else str(self.left)
        right_str = f"({self.right})" if isinstance(self.right, Or) else str(self.right)
        return f"{left_str} and {right_str}"


class Or(LogicExpression):
    """Логическое ИЛИ."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def simplify(self):
        # Упрощаем операнды
        left = self.left.simplify()
        right = self.right.simplify()

        # A or True = True
        if isinstance(left, Constant) and left.value:
            return Constant(True)
        if isinstance(right, Constant) and right.value:
            return Constant(True)

        # A or False = A
        if isinstance(left, Constant) and not left.value:
            return right
        if isinstance(right, Constant) and not right.value:
            return left

        # A or A = A (идемпотентность)
        if left.__class__ == right.__class__ and left.__dict__ == right.__dict__:
            return left

        # (A and not A) or B = B (закон противоречия)
        if self._is_contradiction(left):
            return right
        if self._is_contradiction(right):
            return left

        return Or(left, right)

    def _is_contradiction(self, expr):
        """Проверяет, является ли выражение законом противоречия: A and not A"""
        if isinstance(expr, And):
            left_is_var = isinstance(expr.left, Variable)
            right_is_var = isinstance(expr.right, Variable)
            left_is_not = isinstance(expr.left, Not) and isinstance(expr.left.operand, Variable)
            right_is_not = isinstance(expr.right, Not) and isinstance(expr.right.operand, Variable)

            if left_is_var and right_is_not and expr.left.name == expr.right.operand.name:
                return True
            if left_is_not and right_is_var and expr.left.operand.name == expr.right.name:
                return True
        return False

    def _str(self):
        return f"({self.left} or {self.right})"


def parse_expression(expr_str):
    """
    Простой парсер логических выражений.
    Поддерживает: переменные, not, and, or, скобки.
    """
    expr_str = expr_str.replace(" ", "").replace("not", "~").replace("and", "&").replace("or", "|")

    tokens = []
    i = 0
    while i < len(expr_str):
        if expr_str[i:i+4] == "True":
            tokens.append("True")
            i += 4
        elif expr_str[i:i+5] == "False":
            tokens.append("False")
            i += 5
        elif expr_str[i].isalpha():
            # Собираем полное имя переменной
            start = i
            while i < len(expr_str) and expr_str[i].isalpha():
                i += 1
            token = expr_str[start:i]
            tokens.append(token)
        elif expr_str[i] in "~&|()":
            tokens.append(expr_str[i])
            i += 1
        else:
            i += 1

    def parse_primary():
        """Парсит первичные выражения: переменные, константы, отрицания, скобки"""
        if not tokens:
            raise ValueError("Неправильное выражение")

        token = tokens.pop(0)

        if token == "True":
            return Constant(True)
        elif token == "False":
            return Constant(False)
        elif token in ["true", "false"]:
            return Constant(token == "true")
        elif token.isalpha():
            return Variable(token)
        elif token == "~":
            return Not(parse_primary())
        elif token == "(":
            expr = parse_expression_tokens()
            if not tokens or tokens.pop(0) != ")":
                raise ValueError("Ожидалась закрывающая скобка")
            return expr

        raise ValueError(f"Неизвестный токен: {token}")

    def parse_expression_tokens():
        """Парсит выражения с and/or"""
        left = parse_primary()

        while tokens and tokens[0] in "&|":
            op = tokens.pop(0)
            right = parse_primary()

            if op == "&":
                left = And(left, right)
            elif op == "|":
                left = Or(left, right)

        return left

    try:
        result = parse_expression_tokens()
        if tokens:
            raise ValueError("Лишние токены в выражении")
        return result
    except Exception as e:
        raise ValueError(f"Ошибка парсинга: {e}")


def simplify_logic_expression(expression):
    """
    Упрощает логическое выражение с использованием законов логики.
    """
    if isinstance(expression, str):
        parsed = parse_expression(expression)
        if parsed is None:
            raise ValueError(f"Не удалось распарсить выражение: {expression}")
    elif isinstance(expression, LogicExpression):
        parsed = expression
    else:
        raise TypeError("Аргумент должен быть строкой или LogicExpression")

    # Применяем упрощение до тех пор, пока выражение не перестанет изменяться
    current = parsed
    steps = 0
    max_steps = 10  # Защита от бесконечного цикла
    while steps < max_steps:
        simplified = current.simplify()
        if str(simplified) == str(current):
            return simplified
        current = simplified
        steps += 1
    return current


# Примеры использования
if __name__ == "__main__":
    # Пример из задания
    expr1 = "(A or (not A)) and B"
    result1 = simplify_logic_expression(expr1)
    print(f"{expr1} = {result1}")

    # Другие примеры
    examples = [
        "A and True",
        "A or False",
        "A and False",
        "A or True",
        "not (not A)",
        "A and A",
        "A or A",
        "not True",
        "not False",
        "(A and (not A)) or B",
    ]

    print("\nТестирование упрощений:")
    for example in examples:
        try:
            result = simplify_logic_expression(example)
            print(f"{example} = {result}")
        except Exception as e:
            print(f"Ошибка в {example}: {e}")
