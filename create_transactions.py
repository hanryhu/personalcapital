from main import main as main_main
from main import TransactionCategoryEnum

import logging

CITIBANK_ACCOUNT = 86993648
UBER_EATS_TAG = 10003640
UBER_EATS_INVERSE_TAG = 10003641

def make_uber_eats_transaction_and_offset(pc, date, description, amount, sleeps=0):
    """
    amount(float): a positive amount.
    """
    try:
        pc.createUserTransaction(
            transactionDate=date,
            userAccountId=CITIBANK_ACCOUNT,
            description=description,
            transactionCategoryId=TransactionCategoryEnum.RESTAURANTS,
            amount=-amount,
            customTags=[UBER_EATS_TAG],
        )
        sleep(sleepsec)
        pc.createUserTransaction(
            transactionDate=date,
            userAccountId=CITIBANK_ACCOUNT,
            description="-"+description,
            transactionCategoryId=TransactionCategoryEnum.RESTAURANTS,
            amount=amount,
            customTags=[UBER_EATS_INVERSE_TAG],
        )
    except Exception as e:
        raise

def main():
    pc = main_main()
    
    return pc

if __name__ == '__main__':
    pc = main()
