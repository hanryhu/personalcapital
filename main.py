from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
import getpass
import json
import logging
import os
import urllib
from datetime import datetime, timedelta

# Python 2 and 3 compatibility
if hasattr(__builtins__, 'raw_input'):
    input = raw_input

class PewCapital(PersonalCapital):
    """
    Extends PersonalCapital to save and load session
    So that it doesn't require 2-factor auth every time
    """
    def __init__(self):
        PersonalCapital.__init__(self)
        self.__session_file = 'session.json'

    def load_session(self):
        try:
            with open(self.__session_file) as data_file:    
                cookies = {}
                try:
                    cookies = json.load(data_file)
                except ValueError as err:
                    logging.error(err)
                self.set_session(cookies)
        except IOError as err:
            logging.error(err)

    def save_session(self):
        with open(self.__session_file, 'w') as data_file:
            data_file.write(json.dumps(self.get_session()))

class TransactionCategoryEnum(object):
    # Incomplete list
    RESTAURANTS = 35

class PewCapitalAPI(PewCapital):
    """
    Adds API calls to PewCapital.
    """
    def createUserTransaction(self, transactionDate, userAccountId, description, transactionCategoryId, amount, customTags):
        """
        transactionDate (str): YYYY-MM-DD
        userAccountId (int): integer ID for account on which transaction should be posted.
        description (str): string description
        transactionCategoryId (int): integer TransactionCategoryEnum
        amount (float): transaction amount.
        """
        # Limit char length for readability
        if len(description) > 39:
            logging.warning('Shortening description for readability: {description}')
            description = description[:39]
        amount = f'{amount:.2f}'
        customTags = f'[{",".join(str(x) for x in customTags)}]'
        data = {
            'transactionDate': transactionDate,
            'userAccountId': userAccountId,
            'description': description,
            'transactionCategoryId': transactionCategoryId,
            'amount': amount,
            'customTags': customTags
        }
        try:
            return self.fetch('/transaction/createUserTransaction', data)
        except Exception as e:
            logging.error('create user transaction failed', e)
            raise

def get_email():
    email = os.getenv('PEW_EMAIL')
    if not email:
        print('You can set the environment variables for PEW_EMAIL and PEW_PASSWORD so the prompts don\'t come up every time')
        return input('Enter email:')
    return email

def get_password():
    password = os.getenv('PEW_PASSWORD')
    if not password:
        return getpass.getpass('Enter password:')
    return password

def main():
    email, password = get_email(), get_password()
    pc = PewCapitalAPI()
    pc.load_session()

    try:
        pc.login(email, password)
    except RequireTwoFactorException:
        pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
        pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, input('code: '))
        pc.authenticate_password(password)

    accounts_response = pc.fetch('/newaccount/getAccounts')
    
    now = datetime.now()
    date_format = '%Y-%m-%d'
    days = 90
    start_date = (now - (timedelta(days=days+1))).strftime(date_format)
    end_date = (now - (timedelta(days=1))).strftime(date_format)
    transactions_response = pc.fetch('/transaction/getUserTransactions', {
        'sort_cols': 'transactionTime',
        'sort_rev': 'true',
        'page': '0',
        'rows_per_page': '100',
        'startDate': start_date,
        'endDate': end_date,
        'component': 'DATAGRID'
    })
    pc.save_session()

    accounts = accounts_response.json()['spData']
    print('Networth: {0}'.format(accounts['networth']))

    transactions = transactions_response.json()['spData']
    print('Number of transactions between {0} and {1}: {2}'.format(transactions['startDate'], transactions['endDate'], len(transactions['transactions'])))
    return pc

if __name__ == '__main__':
    pc = main()
