from dataclasses import dataclass, field
from datetime import datetime

from decimal import Decimal

from logging import getLogger

from threading import Lock

from typing import *


logger = getLogger(__name__)


class TransactionList(list):

    def __delitem__(self, key):
        pass

    def insert(self, __index, __object):
        pass

    def pop(self, __index = -1):
        pass


class BankAccountError(Exception):
    pass


class BankAccountInactiveError(Exception):
    pass


class BankAccountInsufficiendFundsError(Exception):
    pass


@dataclass
class BankAccount:
    number: str
    history: List['Transaction'] = field(default_factory=TransactionList)
    balance: Decimal = 0.0
    active: bool = True
    lock: Lock = field(default_factory=Lock)

    @classmethod
    def create_bank_account(cls, **params) -> 'BankAccount':
        try:
            bank_account = cls(**params)
        except TypeError:
            raise BankAccountError(f"Cannot create BankAccount with data {params=}")
        else:
            return bank_account

    def process_transaction(self, t):
        amount = t.get_amount(self)
        if amount < 0 and self.balance - amount < 0:
            raise BankAccountInsufficiendFundsError(f"BankAccount {self.number} does not have enough balance")
        self.balance += amount
        self.history.append(t)


@dataclass
class Transaction:
    from_account: BankAccount
    timestamp: datetime
    type: str
    amount: Decimal = 0.0
    to_account: Optional[BankAccount] = None

    def get_amount(self, for_account: BankAccount):
        return 0 - abs(self.amount) if for_account.number == self.from_account.number else abs(self.amount)


@dataclass
class Withdrawal(Transaction):
    type: str = 'WITHDRAWAL'


@dataclass
class Transfer(Transaction):
    type: str = 'TRANSFER'


class LedgerError(Exception):
    pass



@dataclass
class Ledger:
    _transactions: List[Transaction] = field(default_factory=TransactionList, repr=False)
    _bank_accounts: Dict[str, BankAccount] = field(default_factory=dict, repr=False)

    def register_bank_account(self, bank_account: BankAccount) -> bool:
        if bank_account.number in self._bank_accounts:
            return False
        self._bank_accounts[bank_account.number] = bank_account
        return True

    def toggle_bank_account_status(self, bank_account_number: str) -> bool:
        try:
            self._bank_accounts[bank_account_number].active = not self._bank_accounts[bank_account_number].active
        except KeyError:
            raise BankAccountError(f'Bank account is not found: {bank_account_number}')

    def unregister_bank_account(self, bank_account: BankAccount) -> bool:
        if bank_account.number not in self._bank_accounts:
            return False
        del self._bank_accounts[bank_account.number]
        return True

    def add_transaction(self, **kwargs):
        try:
            t = Transaction(**kwargs)
        except TypeError:
            raise LedgerError(f'Cannot initialize transaction {kwargs=}. Aborting')
        else:
            self.process_transaction(t)

    def process_transaction(self, t: Transaction):
        if not self._bank_accounts.get(t.from_account.number):
            raise LedgerError(f'BankAccount {t.from_account} is not found on ledger')
        if t.to_account and not self._bank_accounts.get(t.to_account.number):
            raise LedgerError(f'BankAccount {t.to_account} is not found on ledger')
        with t.from_account.lock:
            t.from_account.process_transaction(t)
            if t.to_account:
                t.to_account.process_transaction(t)
            self._transactions.append(t)

    @classmethod
    def load_transactions(cls, transactions: List[Dict]) -> 'Ledger':
        ledger = cls()
        for transaction in transactions:
            ledger.register_bank_account(transaction['from_account'])
            if transaction.get('to_account'):
                ledger.register_bank_account(transaction['to_account'])
            ledger.add_transaction(**transaction)
        return ledger


