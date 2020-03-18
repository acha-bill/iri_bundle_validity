from iota import ProposedTransaction, Bundle, Iota, TryteString, Address, Transaction, TransactionHash
from typing import List
from pprint import pprint
import time

api = Iota('http://localhost:14265', testnet=True)


def prepare_bundle():
    message = TryteString.from_unicode('Bang')
    address = 'ZQGVEQ9JUZZWCZXLWVNTHBDX9G9KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'

    transfers = [ProposedTransaction(
        address=Address(address),
        value=0
    ),
        ProposedTransaction(
        address=Address(address),
        value=0
    ),
        ProposedTransaction(
        address=Address(address),
        value=0
    )]
    trytes = api.prepare_transfer(transfers=transfers).get('trytes')
    return trytes


def send_bundle(trytes):
    gtta = api.get_transactions_to_approve(depth=3)
    trunk = str(gtta['trunkTransaction']) # set a non-tail to fail rule 1
    branch = str(gtta['branchTransaction']) #set a non-tail to fail rule 1

    attached_trytes = api.attach_to_tangle(
        trunk, branch, trytes, 9).get('trytes')
    api.broadcast_and_store(attached_trytes)
    bundle = Bundle.from_tryte_strings(attached_trytes)
    pprint('Bundle is:')
    pprint(bundle.as_json_compatible())
    return attached_trytes


trytes = prepare_bundle()
attached_trytes = send_bundle(trytes)

# hashes
# rule 1 (a bundle must only approve a tail)
# TJYJ9RWNHDXDZZJLOZTQJHQVAUEUYIVLSQXKEGLHQJKSWWTZHZPZXDRLUTVLFYJYUFVBZJAH9PWBKQZFC (trunk = tail, branch = tail) true
# REC9XHGH9OWPYECRDPACAIKHQEHRL9GHHFILCRKGZPUOSJYUJKVYPRZKJBIYSFYVZTITXFQUCRHUIHLN9 (branch = trunk = non tail) missing
# OEDWHCPLOUICY9VGBBIIVQQFWCFXGOKCKZYNIECSFGKSUI9TBCJ9HALDEFKQUFLTJSTXYQPQGQDDOGGCB (trunk = non tail, branch = non tail) invalid bundle
# RMSJIIDQGJKJHAEQ9WJAUDYQFHNXDVBBAAYSEKR9DYNZCUCLEQQKJQ9AXAUCDECRLGOSG9HTX9BJHGJUY (trunk = tail, branch = non tail) invalid bundle