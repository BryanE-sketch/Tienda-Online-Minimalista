import uuid
from dataclasses import dataclass

DECLINED_TEST_CARD = '4000000000000002'


@dataclass
class PaymentResult:
    approved: bool
    reference: str = ''


def luhn_is_valid(number):
    """Comprueba el dígito de control que llevan todas las tarjetas."""
    total = 0
    for index, char in enumerate(reversed(number)):
        digit = int(char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def simulate_payment(card_number):
    """Hace el papel del banco: rechaza la tarjeta de prueba y aprueba el resto."""
    if card_number == DECLINED_TEST_CARD:
        return PaymentResult(approved=False)
    reference = f'SIM-{uuid.uuid4().hex[:10].upper()}'
    return PaymentResult(approved=True, reference=reference)