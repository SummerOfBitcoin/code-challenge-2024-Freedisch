import json
import os
import hashlib
import time
import re

def create_block_header(previous_block_hash, merkle_root, difficulty='0000ffff00000000000000000000000000000000000000000000000000000000'):
    version = 1
    timestamp = int(time.time())
    nonce = 0
    header = f'{version}{previous_block_hash}{merkle_root}{timestamp}{difficulty}{nonce}'
    return header


def create_coinbase_transaction(block_height, reward_address, reward_amount):
    inputs = {'block_height': block_height}
    outputs = {'recipient': reward_address, 'amount': reward_amount}
    coinbase_tx = {'txid': 'coinbase', 'inputs': [inputs], 'outputs': [outputs]}
    return coinbase_tx


def load_transactions():
    transactions = []
    print("test")
    for filename in os.listdir('mempool'):
        if filename.endswith('.json'):
            with open(f'mempool/{filename}', 'r') as file:
                try:
                    transaction = json.load(file)
                    if all('txid' in vin for vin in transaction.get('vin', [])):
                        #print(f"Valid transaction found in {filename}")
                        transactions.append(transaction)
                except json.JSONDecodeError:
                    continue
    return transactions


def validate_transaction(transaction):
    try:
        if not (isinstance(transaction['version'], int) and isinstance(transaction['locktime'], int)):
            return False
        
        total_input_value = 0
        for vin in transaction['vin']:
            if not re.match(r"^[a-f0-9]{64}$", vin['txid']):
                return False
            if not isinstance(vin['vout'], int):
                return False
            if vin['prevout']['value'] <= 0:
                return False
            total_input_value += vin['prevout']['value']
        total_output_value = 0
        for vout in transaction['vout']:
            if 'scriptpubkey_address' not in vout or not re.match(r"^bc1[a-z0-9]{25,39}$", vout['scriptpubkey_address']):
                return False
            if vout['value'] <= 0:
                return False
            total_output_value += vout['value']
        if total_input_value < total_output_value:
            return False

        return True
    except KeyError:
        return False

def extract_all_txids(transactions):
    transaction_ids = []
    for tx in transactions:
        if 'vin' in tx and tx['vin']:
            for vin in tx['vin']:
                if 'txid' in vin and vin['txid'] not in transaction_ids:
                    transaction_ids.append(vin['txid'])
    return transaction_ids

def mine_block(transactions, previous_block_hash, reward_address):

    transaction_ids = extract_all_txids(transactions)
    merkle_root = hashlib.sha256(''.join(transaction_ids).encode()).hexdigest()
    block_header = create_block_header(previous_block_hash, merkle_root)

    block_height = 1
    reward_amount = 12.5
    coin_tx = create_coinbase_transaction(block_height, reward_address, reward_amount)


    return block_header, coin_tx, transaction_ids

def calculate_hash(block_header, txids):
    content = block_header + ''.join(txids)
    return hashlib.sha256(content.encode()).hexdigest()



def write_output(block_header, coinbase_tx, txids):
    with open('output.txt', 'w') as file:
        file.write(block_header + '\n')
        file.write(json.dumps(coinbase_tx) + '\n')
        for txid in txids:
            file.write(txid + '\n')

def main():
    transactions = load_transactions()
    pvs_block_hash = '0000000000000000000000000000000000000000000000000000000000000000'
    rwrd_address = '1BitcoinAddressV1uuuuuuuuuuumZ1AWm'

    if pvs_block_hash and rwrd_address:
        block_header, coin_tx, txids = mine_block(transactions, pvs_block_hash, rwrd_address)
        print(txids)
        write_output(block_header, coin_tx, txids)
    else:
        print("Error: Missing previous block hash or reward address")


if __name__ == '__main__':
    main()