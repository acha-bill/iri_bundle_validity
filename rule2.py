from iota import Iota, ProposedTransaction, Address, Bundle, TransactionHash, \
    TransactionTrytes, Transaction, TryteString
from typing import List
from pprint import pprint


def custom_attach(
    trytes: List[TransactionTrytes],
    mwm: int,
):
    """
    Custom attach to to tangle.

    Takes already attached bundle trytes, and except for the the head transaction,
    updates `attachment_timestamp` and re-does the pow, resulting in a new
    nonce and transaction hash.

    The head transaction remains the same as in the original bundle.

    """
    # Install the pow package together with pyota:
    # $ pip install pyota[pow]
    from pow.ccurl_interface import get_powed_tx_trytes, get_hash_trytes, \
        get_current_ms

    previoustx = None

    # Construct bundle object
    bundle = Bundle.from_tryte_strings(trytes)

    # and we need the head tx first
    for txn in reversed(bundle.transactions):        
        if (not previoustx): # this is the head transaction
            # head tx stays the same, it is the original
            previoustx = txn.hash
            continue

        #we only want to mess with tx at index 1
        if txn.current_index != 1:
            continue

        # set any old tx so that this bundles head.trunk != tx
        txn.branch_transaction_hash = 'TBLBTVTHAMPGMGQBUETQSOYHXLCDKSFRTLECTRKSTCHCEHJLCCRPGCUK9VUJNWGQCQNZCUM9IVVIOB999' # the previous transaction
        txn.attachment_timestamp = get_current_ms()
        
        # Let's do the pow locally
        txn_string = txn.as_tryte_string().__str__()
        # returns a python unicode string
        powed_txn_string = get_powed_tx_trytes(txn_string, mwm)
        # construct trytestring from python string
        powed_txn_trytes = TryteString(powed_txn_string)
        # compute transaction hash
        hash_string = get_hash_trytes(powed_txn_string)
        hash_trytes = TryteString(hash_string)
        hash_= TransactionHash(hash_trytes)

        # Create powed txn object
        powed_txn = Transaction.from_tryte_string(
            trytes=powed_txn_trytes,
            hash_=hash_
        )

        previoustx = powed_txn.hash
        # put that back in the bundle
        bundle.transactions[txn.current_index] = powed_txn
    return bundle.as_tryte_strings()


api = Iota('http://localhost:14265', testnet=True, local_pow=True)

addys = [
    Address(b'UPYQLREUEUETMRIGNNYLHVJSUKJZCEOGMO9OPXSY9ZNWWKDTTNOGVOJVZBNCBLLXZZWLWWJMUQPADKES9'),
    Address(b'NDGHOGDRXEXNFQOW9XQIYKYAUIEZMTZDQMPEQTSDHTQEKCIYYANZMGDOJBSRCNT9RBC9CJDTBVBFDQF99'),
    Address(b'NZRHABYULAZM9KEXRQODGUZBLURTOKSGWWMOPIAJSTJFVAHNCCMJSVULRKGD9PLBMKOEGBNZRJHQSVVCA'),
    Address(b'EECOCPAECTETNWT9ERFUJCFXQWRVXFZDWHSPSOOSLTDKKNYSVKTVZJASDV9HAYTNZSQIW99JLUYLQSFMY')
]

# Prepare the original bundle
original_trytes = api.prepare_transfer(
    transfers=[
        ProposedTransaction(
            address=addys[0],
            value=0
        ),
                ProposedTransaction(
            address=addys[1],
            value=0
        ),
                ProposedTransaction(
            address=addys[2],
            value=0
        ),
                ProposedTransaction(
            address=addys[3],
            value=0
        ),
    ]
).get('trytes')

gtta_response = api.get_transactions_to_approve(3)

trunk = gtta_response.get('trunkTransaction')
branch = gtta_response.get('branchTransaction')

attached_original_trytes = api.attach_to_tangle(trunk, branch, original_trytes).get('trytes')

# So we have the original bundle attached, time to construct the new one
# We need to re-attach, but take special care, so we dont use the api, rather we do it ourself

re_attached_trytes = custom_attach(attached_original_trytes, 9)

original_bundle = Bundle.from_tryte_strings(attached_original_trytes)

re_attached_bundle = Bundle.from_tryte_strings(re_attached_trytes)

pprint('Original bundle is:')
pprint(original_bundle.as_json_compatible())

pprint('Reattached bundle is:')
pprint(re_attached_bundle.as_json_compatible())

#api.broadcast_and_store(attached_original_trytes)
api.broadcast_and_store(re_attached_trytes)


# bundles
# BJRYHWKLREEUQCAZSUQFDNQAIL9LFRBZVEFFWPQZ99GNKATZBUZKFJYJIRYTFBPPESFJYDQRAYHNHH9LW good
# UYBVN9EZKNA9KGGCSILJJGRTNGI9ZHVIUEYB9VXZXHLKZBTFGPHGJPJ9OHCUILSRBAA9XYSDKIXHYVLJW bad