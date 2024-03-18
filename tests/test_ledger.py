from datetime import datetime

from decimal import Decimal

import freezegun
import pytest

from ledger.main import (
    BankAccount,
    Ledger,
    Transfer,
    Withdrawal
)



def test_ledger_create_ok(fake_transactions):
    ledger = Ledger.load_transactions(fake_transactions)
    assert len(ledger._transactions) == len(fake_transactions)


def test_cannot_pop_from_transactions(fake_transactions):
    ledger = Ledger.load_transactions(fake_transactions)
    transactions_len = len(ledger._transactions)
    res = ledger._transactions.pop()
    assert res is None, "Should not return any value"
    assert len(ledger._transactions) == transactions_len


def test_cannot_insert_transactions(fake_transactions):
    ledger = Ledger.load_transactions(fake_transactions)
    transactions_len = len(ledger._transactions)
    t = Withdrawal(**{'from_account': ledger._bank_accounts['12345'], 'amount': 20, 'timestamp': datetime.now()})
    ledger._transactions.insert(0, t)
    assert len(ledger._transactions) == transactions_len


def test_bank_balance(fake_transactions):
    ledger = Ledger.load_transactions(fake_transactions)
    account1 = ledger._bank_accounts['12345']
    account2 = ledger._bank_accounts['54321']
    assert account1.balance == Decimal(205)  # 155 - 150 + 200
    assert account2.balance == Decimal(0)  # 200 - 200


@freezegun.freeze_time('2024-03-18T10:00:00')
def test_simple_ledger_workflow():
    ledger = Ledger()
    assert len(ledger._bank_accounts) == 0
    assert len(ledger._transactions) == 0
    account1 = BankAccount(number='1', balance=Decimal(1500))
    account2 = BankAccount(number='2', balance=Decimal(1000))
    ledger.register_bank_account(account1)
    assert len(ledger._bank_accounts) == 1
    ledger.register_bank_account(account2)
    assert len(ledger._bank_accounts) == 2
    res = ledger.register_bank_account(account2)
    assert res is False
    assert len(ledger._bank_accounts) == 2
    w = Withdrawal(from_account=account1, amount=Decimal(500), timestamp=datetime.now())
    ledger.process_transaction(w)
    assert account1.balance == Decimal(1000)
    assert len(account1.history) == len(ledger._transactions)
    t = Transfer(from_account=account1, to_account=account2, amount=Decimal(500), timestamp=datetime.now())
    ledger.process_transaction(t)
    assert account1.balance == Decimal(500)
    assert account2.balance == Decimal(1500)
