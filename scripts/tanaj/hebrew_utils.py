"""
Hebrew text utilities for Tanaj processing.
"""

import logging

logger = logging.getLogger(__name__)


def number_to_hebrew_numeral(num: int) -> str:
    """
    Convert a number to Hebrew numeral representation.

    Hebrew numerals use letters with special combinations:
    - 1-9: א-ט
    - 10-19: י + unit (except 15=טו, 16=טז)
    - 20-90: כ, ל, מ, נ, ס, ע, פ, צ + unit
    - 100-400: ק, ר, ש, ת + tens + units
    - 500+: ת + remainder
    """
    if num <= 0:
        return str(num)

    # Use the existing HEBREW_NUMERALS dictionary for numbers 1-50
    # For consistency with Besorah books
    from scripts.text.books import HEBREW_NUMERALS

    if num in HEBREW_NUMERALS:
        return HEBREW_NUMERALS[num]

    # For numbers beyond 50, generate Hebrew numerals
    # Units: א-ט (1-9)
    units = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט']
    # Tens: י, כ, ל, מ, נ, ס, ע, פ, צ (10-90)
    tens = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ']
    # Hundreds: ק, ר, ש, ת (100-400)
    hundreds = ['', 'ק', 'ר', 'ש', 'ת']

    result = ''

    # Handle hundreds (100-400)
    if num >= 100:
        hundreds_digit = num // 100
        if hundreds_digit <= 4:
            result += hundreds[hundreds_digit]
        else:
            # For 500+, use ת (400) + remainder
            result += 'ת'
            remainder = num - 400
            if remainder > 0:
                return result + number_to_hebrew_numeral(remainder)
        num = num % 100

    # Handle tens (20-90)
    if num >= 20:
        tens_digit = num // 10
        result += tens[tens_digit]
        num = num % 10

    # Handle 10-19
    elif num >= 10:
        if num == 15:
            result += 'טו'
        elif num == 16:
            result += 'טז'
        else:
            result += 'י' + units[num - 10]
        num = 0

    # Handle units (1-9)
    if num > 0:
        result += units[num]

    return result