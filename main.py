import json
import hashlib
import os

def calculate_block_header(transactions):
    version = 1
    prev_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    merkle_root = hashlib.sha256("merkle_root_data".encode()).hexdigest()
    timestamp = 1630425600
    difficulty_target = "0000ffff00000000000000000000000000000000000000000000000000000000"
    nonce = 12345

    block_header = (
        f"{version:08x}"
        f"{prev_block_hash}"
        f"{merkle_root}"
        f"{timestamp:08x}"
        f"{difficulty_target}"
        f"{nonce:08x}"
    )
    block_hash = hashlib.sha256(hashlib.sha256(block_header.encode()).digest()).hexdigest()
    return block_hash

def read_transactions():
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
    return True

def extract_all_txids(transactions):
    transaction_ids = []
    for tx in transactions:
        if 'vin' in tx and tx['vin']:
            for vin in tx['vin']:
                if 'txid' in vin and vin['txid'] not in transaction_ids:
                    transaction_ids.append(vin['txid'])
    return transaction_ids

def create_coinbase_transaction():
    return "coinbase_txid"

def mine_block(transactions):
    txids = extract_all_txids(transactions)
    block_hash = calculate_block_header(transactions)
    return block_hash, txids

def write_output(block_header, coinbase_txid, txids):
    with open("output.txt", "w") as f:
        f.write(block_header + "\n")
        f.write(coinbase_txid + "\n")
        for txid in txids:
            f.write(txid + "\n")

if __name__ == "__main__":
    transactions = read_transactions()
    valid_transactions = [tx for tx in transactions if validate_transaction(tx)]
    coinbase_txid = create_coinbase_transaction()
    block_header, txids = mine_block(valid_transactions)
    write_output(block_header, coinbase_txid, txids)
    print("Block mined successfully! Check output.txt for details.")
