import json
import os
import hashlib
import time
import re

import struct

def create_block_header(version, previous_block_hash, merkle_root, bits, nonce):
    # Convert hash strings to binary
    target = int(bits, 16)
    
    # Initial nonce
    nonce = 0
    
    # Pack the initial block header without the nonce
    timestamp = int(time.time())
    prev_block_hash_bin = bytes.fromhex(previous_block_hash)
    merkle_root_bin = bytes.fromhex(merkle_root)
    header_format = '<L32s32sLL'
    initial_header = struct.pack(header_format, version, prev_block_hash_bin, merkle_root_bin, timestamp, int(bits, 16))
    
    # Start mining
    while True:
        # Pack the nonce and complete the header
        header = initial_header + struct.pack('<L', nonce)
        
        # Calculate the double SHA-256 hash of the header
        hash_result = hashlib.sha256(hashlib.sha256(header).digest()).digest()
        
        # Convert the hash to an integer to compare against the target
        hash_int = int.from_bytes(hash_result, byteorder='big')
        
        # Check if the hash is less than the target
        if hash_int < target:
            print(f"Nonce found: {nonce}")
            print(f"Hash: {hash_result.hex()}")
            break
        
        # Increment the nonce and try again
        nonce += 1
    
    return header


def create_coinbase_transaction(block_height, reward_address, reward_amount):
    inputs = {'block_height': block_height}
    outputs = {'recipient': reward_address, 'amount': reward_amount}
    coinbase_tx = {'txid': 'coinbase', 'inputs': [inputs], 'outputs': [outputs]}
    return coinbase_tx


def load_transactions():
    transactions = []
    count = 0
    print("test")
    for filename in os.listdir('mempool'):
        if filename.endswith('.json') and count != 7:
            with open(f'mempool/{filename}', 'r') as file:
                try:
                    transaction = json.load(file)
                    if all('txid' in vin for vin in transaction.get('vin', [])):
                        #print(f"Valid transaction found in {filename}")
                        transactions.append(transaction)
                        count += 1
                except json.JSONDecodeError:
                    continue
    return transactions


def validate_transaction(transaction):
    try:
        if not (isinstance(transaction['version'], int) and isinstance(transaction['locktime'], int)):
            return False

        # Validate inputs
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
    # Extract all transaction IDs from the transactions
    transaction_ids = extract_all_txids(transactions)
    # Calculate the Merkle root from the concatenated txids
    merkle_root = hashlib.sha256(''.join(transaction_ids).encode()).hexdigest()
    
    # Define the block header parameters
    version = 2  # Set the version of the block
    bits = '1d00ffff'  # This is a placeholder for the difficulty target bits
    nonce = 0  # Starting nonce, this will typically be incremented in the mining process

    # Call create_block_header with all the required parameters
    block_header = create_block_header(version, previous_block_hash, merkle_root, bits, nonce)

    # Calculate the block height and reward amount
    block_height = 1  # Example block height, this should be dynamically determined
    reward_amount = 12.5  # Reward amount for mining the block

    # Create the coinbase transaction
    coin_tx = create_coinbase_transaction(block_height, reward_address, reward_amount)

    return block_header, coin_tx, transaction_ids

def calculate_hash(block_header, txids):
    content = block_header + ''.join(txids)
    return hashlib.sha256(content.encode()).hexdigest()


# def calculate_merkle_root(transactions):
#     # Placeholder for Merkle root calculation; implement your actual logic
#     if not transactions:
#         return '0' * 64  # Return a default merkle root if no transactions
#     # Simple example to simulate a merkle root calculation
#     return hashlib.sha256(''.join(tx['txid'] for tx in transactions).encode()).hexdigest()


def write_output(block_header, coin_tx, txids):
    with open('output.txt', 'w') as file:
        # Convert the binary block_header to a hex string and write it to file
        file.write(block_header.hex() + '\n')
        # Assuming coin_tx['txid'] is a string
        file.write(coin_tx['txid'] + '\n')
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
