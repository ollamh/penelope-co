import pytest

from datetime import datetime
from decimal import Decimal

from ledger.main import BankAccount

import freezegun


@freezegun.freeze_time('2024-03-18T15:33:00')
@pytest.fixture
def fake_transactions():
    account1 = BankAccount(number='12345', balance=Decimal(155.0))
    account2 = BankAccount(number='54321', balance=Decimal(200.0))
    return [
        {
            'from_account': account1,
            'type': 'WITHDRAWAL',
            'timestamp': datetime.now(),
            'amount': 150
        },
        {
            'from_account': account2,
            'type': 'WITHDRAWAL',
            'timestamp': datetime.now(),
            'amount': 200,
            'to_account': account1
        }
    ]
