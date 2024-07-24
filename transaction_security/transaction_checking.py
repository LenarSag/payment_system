import hashlib

from config import TRANSACTION_KEY
from schemas.accounts_schema import InboxTransaction


secret_key = TRANSACTION_KEY


def hash_with_sha256(message):
    byte_message = message.encode()
    sha256_hash = hashlib.sha256()
    sha256_hash.update(byte_message)
    hex_digest = sha256_hash.hexdigest()
    return hex_digest


def signature_is_correct(transaction_data: InboxTransaction):
    string_to_hash = (
        str(transaction_data.account_id)
        + str(transaction_data.amount)
        + str(transaction_data.transaction_id)
        + str(transaction_data.user_id)
        + secret_key
    )
    hashed_message = hash_with_sha256(string_to_hash)

    return transaction_data.signature == hashed_message
