const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

function createBlockHeader(previousBlockHash, merkleRoot, difficulty = '0000ffff00000000000000000000000000000000000000000000000000000000') {
    const version = 1;
    const timestamp = Math.floor(Date.now() / 1000);
    const nonce = 0;
    const header = `${version}${previousBlockHash}${merkleRoot}${timestamp}${difficulty}${nonce}`;
    return header;
}

function createCoinbaseTransaction(blockHeight, rewardAddress, rewardAmount) {
    const inputs = { block_height: blockHeight };
    const outputs = { recipient: rewardAddress, amount: rewardAmount };
    const coinbaseTx = { txid: 'coinbase', inputs: [inputs], outputs: [outputs] };
    return coinbaseTx;
}

function loadTransactions() {
    const transactions = [];
    const files = fs.readdirSync('mempool');
    files.forEach(file => {
        if (file.endsWith('.json')) {
            try {
                const data = fs.readFileSync(path.join('mempool', file), 'utf8');
                const transaction = JSON.parse(data);
                if (transaction.vin.every(vin => 'txid' in vin)) {
                    transactions.push(transaction);
                }
            } catch (error) {
                console.error(`Failed to read or parse ${file}: ${error}`);
            }
        }
    });
    return transactions;
}

function validateTransaction(transaction) {
    try {
        if (typeof transaction.version !== 'number' || typeof transaction.locktime !== 'number') {
            return false;
        }

        let totalInputValue = 0;
        for (const vin of transaction.vin) {
            if (!/^[a-f0-9]{64}$/.test(vin.txid) || typeof vin.vout !== 'number' || vin.prevout.value <= 0) {
                return false;
            }
            totalInputValue += vin.prevout.value;
        }

        let totalOutputValue = 0;
        for (const vout of transaction.vout) {
            if (!('scriptpubkey_address' in vout) || !/^bc1[a-z0-9]{25,39}$/.test(vout.scriptpubkey_address) || vout.value <= 0) {
                return false;
            }
            totalOutputValue += vout.value;
        }

        return totalInputValue >= totalOutputValue;
    } catch (error) {
        return false;
    }
}

function extractAllTxids(transactions) {
    const transactionIds = [];
    transactions.forEach(tx => {
        if (tx.vin && Array.isArray(tx.vin)) {
            tx.vin.forEach(vin => {
                if (vin.txid && !transactionIds.includes(vin.txid)) {
                    transactionIds.push(vin.txid);
                }
            });
        }
    });
    return transactionIds; // Always an array, even if empty.
}


function mineBlock(transactions, previousBlockHash, rewardAddress) {
    const transactionIds = extractAllTxids(transactions);
    if (!transactionIds || !Array.isArray(transactionIds)) {
        console.error('Failed to extract transaction IDs or result is not an array');
        return { blockHeader: null, coinTx: null, transactionIds: [] }; // Return an empty array for transactionIds
    }

    const merkleRoot = crypto.createHash('sha256').update(transactionIds.join('')).digest('hex');
    const blockHeader = createBlockHeader(previousBlockHash, merkleRoot);

    const blockHeight = 1;
    const rewardAmount = 12.5;
    const coinTx = createCoinbaseTransaction(blockHeight, rewardAddress, rewardAmount);

    return { blockHeader, coinTx, transactionIds };
}


function writeOutput(blockHeader, coinbaseTx, txids) {
    const fileContent = [
        blockHeader,
        JSON.stringify(coinbaseTx),
        ...(Array.isArray(txids) ? txids : [])  // Ensure txids is an array before trying to spread it
    ].join('\n');
    fs.writeFileSync('output.txt', fileContent);
}


function main() {
    const transactions = loadTransactions();
    const previousBlockHash = '0000000000000000000000000000000000000000000000000000000000000000';
    const rewardAddress = '1BitcoinAddressV1uuuuuuuuuuumZ1AWm';

    if (previousBlockHash && rewardAddress) {
        const { blockHeader, coinTx, txids } = mineBlock(transactions, previousBlockHash, rewardAddress);
        console.log(txids);
        writeOutput(blockHeader, coinTx, txids);
    } else {
        console.error("Error: Missing previous block hash or reward address");
    }
}

main();
