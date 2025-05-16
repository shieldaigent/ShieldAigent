import os
import logging
from dotenv import load_dotenv
from flask import Flask, request
from web3 import Web3
from solcx import compile_source
import json

# Load environment variables
load_dotenv()
INFURA_URL = os.getenv('INFURA_URL')
OWNER_ADDRESS = os.getenv('OWNER_ADDRESS')
OWNER_PRIVATE_KEY = os.getenv('OWNER_PRIVATE_KEY')
SECONDARY_ADDRESS = os.getenv('SECONDARY_ADDRESS')

# Set up logging (reusing ShieldAigent's logging setup)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("OnchainSecurity starting up...")

# Initialize Flask app
app = Flask(__name__)

# Connect to Ethereum node (e.g., Sepolia testnet via Infura)
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not w3.is_connected():
    logger.error("Failed to connect to Ethereum node")
    exit(1)
logger.info("Connected to Ethereum node")

# Compile the smart contract
def compile_contract():
    with open('contracts/SecurityLayer.sol', 'r') as file:
        contract_source = file.read()
    compiled = compile_source(contract_source, output_values=['abi', 'bin'])
    contract_id, contract_interface = compiled.popitem()
    return contract_interface['abi'], contract_interface['bin']

# Deploy the smart contract
def deploy_contract():
    global CONTRACT_ADDRESS, CONTRACT_ABI
    abi, bytecode = compile_contract()
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Build the deployment transaction
    daily_limit = w3.to_wei(1, 'ether')  # Daily limit of 1 ETH (adjust as needed)
    construct_txn = contract.constructor(SECONDARY_ADDRESS, daily_limit).build_transaction({
        'from': OWNER_ADDRESS,
        'nonce': w3.eth.get_transaction_count(OWNER_ADDRESS),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price
    })

    # Sign and send the transaction
    signed_txn = w3.eth.account.sign_transaction(construct_txn, OWNER_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    CONTRACT_ADDRESS = tx_receipt.contractAddress
    CONTRACT_ABI = abi
    logger.info(f"Contract deployed at address: {CONTRACT_ADDRESS}")

    # Save the contract address and ABI to a file for later use
    with open('contract_info.json', 'w') as f:
        json.dump({'address': CONTRACT_ADDRESS, 'abi': CONTRACT_ABI}, f)

# Load contract info if already deployed
CONTRACT_ADDRESS = None
CONTRACT_ABI = None
try:
    with open('contract_info.json', 'r') as f:
        contract_info = json.load(f)
        CONTRACT_ADDRESS = contract_info['address']
        CONTRACT_ABI = contract_info['abi']
    logger.info(f"Loaded contract at address: {CONTRACT_ADDRESS}")
except FileNotFoundError:
    logger.info("Contract not deployed yet. Deploying now...")
    deploy_contract()

# Initialize the contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Flask routes
@app.route("/")
def home():
    return "OnchainSecurity is running!"

@app.route("/request-transaction", methods=["POST"])
def request_transaction():
    data = request.get_json()
    to_address = data.get("to")
    value = int(data.get("value"))  # In wei
    if not to_address or not value:
        return {"error": "Missing to address or value"}, 400
    try:
        # Call the smart contract to request a transaction
        txn = contract.functions.requestTransaction(to_address, value).build_transaction({
            'from': OWNER_ADDRESS,
            'nonce': w3.eth.get_transaction_count(OWNER_ADDRESS),
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })
        signed_txn = w3.eth.account.sign_transaction(txn, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(f"Transaction requested: {to_address}, {value} wei - Tx Hash: {tx_hash.hex()}")
        return {"status": "Transaction requested", "to": to_address, "value": value, "tx_hash": tx_hash.hex()}, 200
    except Exception as e:
        logger.error(f"Error requesting transaction: {e}")
        return {"error": str(e)}, 500

@app.route("/approve-transaction", methods=["POST"])
def approve_transaction():
    data = request.get_json()
    tx_hash = data.get("tx_hash")
    if not tx_hash:
        return {"error": "Missing transaction hash"}, 400
    try:
        # Call the smart contract to approve the transaction (from secondary approver)
        txn = contract.functions.approveTransaction(tx_hash).build_transaction({
            'from': SECONDARY_ADDRESS,
            'nonce': w3.eth.get_transaction_count(SECONDARY_ADDRESS),
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })
        # Note: You'll need the secondary private key to sign this transaction
        # For now, this is a placeholder
        logger.info(f"Transaction approval placeholder for tx_hash: {tx_hash}")
        return {"status": "Transaction approval requested", "tx_hash": tx_hash}, 200
    except Exception as e:
        logger.error(f"Error approving transaction: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))  # Use a different port than ShieldAigent (8080)
    app.run(host="0.0.0.0", port=port)