import json
import hashlib
import os

def calculate_block_header(transactions):
    # Assume valid transactions are already filtered
    version = 1
    prev_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    merkle_root = hashlib.sha256("merkle_root_data".encode()).hexdigest()
    timestamp = 1630425600  # Example timestamp (Unix timestamp for September 1, 2021)
    difficulty_target = "0000ffff00000000000000000000000000000000000000000000000000000000"
    nonce = 12345  # Example nonce

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

# Validate transactions (dummy validation for demonstration)
def validate_transaction(transaction):
    # Implement your validation logic here
    # For demonstration purposes, assume all transactions are valid
    return True

def extract_all_txids(transactions):
    transaction_ids = []
    for tx in transactions:
        if 'vin' in tx and tx['vin']:
            for vin in tx['vin']:
                if 'txid' in vin and vin['txid'] not in transaction_ids:
                    transaction_ids.append(vin['txid'])
    return transaction_ids

# Create the coinbase transaction (dummy for demonstration)
def create_coinbase_transaction():
    return "coinbase_txid"

# Mine the block (dummy for demonstration)
def mine_block(transactions):
    # Arrange transactions into a block (for demonstration, just use all valid transactions)
    txids = extract_all_txids(transactions)
    # Calculate the block header (dummy hash for demonstration)
    block_hash = calculate_block_header(transactions)
    #block_header = hashlib.sha256("block_data".encode()).hexdigest()
    return block_hash, txids

# Write output to output.txt
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
