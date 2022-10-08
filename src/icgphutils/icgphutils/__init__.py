import random
import string
import re

from math import floor
from decimal import Decimal
from typing import Optional

from icgphutils.constants import Constants


def func_validate_password(
        password,
        allow_lower,
        allow_upper,
        allow_num,
        allow_symbol
):
    symbols = string.punctuation
    flag = True
    if allow_lower is True and not re.search("[a-z]", password):
        flag = False
    elif allow_upper is True and not re.search("[A-Z]", password):
        flag = False
    elif allow_num is True and not re.search("[0-9]", password):
        flag = False
    elif allow_symbol is True and not any(char in symbols for char in password):
        flag = False
    elif re.search("\s", password):
        flag = False
    else:
        print('{} password is valid'.format(password))
    return flag


def func_generate_password(
        length,
        allow_lower=True,
        allow_upper=True,
        allow_num=True,
        allow_symbol=True
):
    # define data
    all = ''
    if allow_lower is True:
        all += string.ascii_lowercase
    if allow_upper is True:
        all += string.ascii_uppercase
    if allow_num is True:
        all += string.digits
    if allow_symbol is True:
        all += string.punctuation

    password = ""
    while True:
        # use random
        temp = random.sample(all, length)

        # create the password
        password = "".join(temp)

        is_valid = func_validate_password(password, allow_lower, allow_upper, allow_num, allow_symbol)
        if is_valid is True:
            break

    return password


def func_floor_to_precision(num: float, precision: int = Constants.CRYPTO_PRECISION) -> float:
    """
    Returns a float value rounded down to a specific number of decimal places

    :param num: float
    :param precision: number of decimal places
    :return: float
    """
    result = num
    num_dp = Decimal(str(num)).as_tuple().exponent * -1

    if num_dp > precision:
        factor = 10 ** precision
        result = floor(num * factor) / factor
    return result


def func_get_step_precision(step: float) -> int:
    """
    Returns the precision value for the step value

    :param step: original step value
    :return: int
    """
    if step % 1 == 0:
        # Drop excess dp
        step = int(step)

    step_dp = Decimal(str(step)).as_tuple().exponent * -1
    return step_dp


def func_get_step_from_precision(precision: int) -> float:
    """
    Returns the step value for the precision

    :param precision: recision value
    :return: float
    """
    return 1 / (10 ** precision)


def func_apply_value_step(input_val: float, step: float, precision: int = Constants.CRYPTO_PRECISION) -> float:
    step_dp = func_get_step_precision(step)

    # Select which precision to use for the factor
    if step_dp > 0:
        adjusted_precision = step_dp
    else:
        adjusted_precision = precision

    # Compute the factor
    factor = 10 ** adjusted_precision

    # Adjust step based on computed factor
    step_exp = floor(step * factor)

    if step_exp == 1:
        # Just truncate based on the number of dp in step
        adjusted_value = func_floor_to_precision(input_val, step_dp)
    else:
        adjusted_value = floor(input_val / step) * step

    return func_floor_to_precision(adjusted_value, precision)


def func_adjust_value_to_step(input_val: float, step: float) -> float:
    if step % 1 == 0:
        # Drop excess dp
        step = int(step)
    return func_floor_to_precision(
        input_val,
        func_get_step_precision(step)
    )


def func_float_arithmetic_add(step_value: float, *args) -> float:
    total = 0
    for num in args:
        total += Decimal(str(num))
    corrected_total = func_adjust_value_to_step(float(total), step_value)
    return corrected_total


def func_float_divide(dividend: float, divisor: float, step: Optional[float] = None) -> float:
    if step is None:
        step = Constants.DEFAULT_STEP_VALUE
    return func_adjust_value_to_step(
        float(Decimal(str(dividend)) / Decimal(str(divisor))),
        step
    )


def func_float_multiply(multiplicand: float, multiplier: float, step: Optional[float] = None) -> float:
    if step is None:
        step = Constants.DEFAULT_STEP_VALUE
    return func_adjust_value_to_step(
        float(Decimal(str(multiplicand)) * Decimal(str(multiplier))),
        step
    )
