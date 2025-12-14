# Упрощение логических выражений

Функция `simplify_logic_expression()` упрощает логические выражения с использованием законов логики.

## Использование

```python
from logic_simplifier import simplify_logic_expression

# Пример из задания
result = simplify_logic_expression("(A or (not A)) and B")
print(result)  # B
```

## Поддерживаемые законы логики

- **Закон исключенного третьего**: `(A or not A) and B = B`
- **Закон противоречия**: `(A and not A) or B = B`
- **Идемпотентность**: `A and A = A`, `A or A = A`
- **Константы**: `A and True = A`, `A or False = A`, `A and False = False`, `A or True = True`
- **Закон двойного отрицания**: `not (not A) = A`
- **Де Моргана** (косвенно через упрощение)

## Синтаксис выражений

- Переменные: `A`, `B`, `C`, ...
- Константы: `True`, `False`
- Операторы: `and`, `or`, `not`
- Скобки: `(`, `)`

Примеры:

- `(A or (not A)) and B`
- `A and True`
- `not (not B)`
