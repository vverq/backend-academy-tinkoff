import datetime
import hashlib
import json
import time
from multiprocessing import Process, Queue
from threading import Thread
from flask import Flask, jsonify, Response


def math_func(proof: int, previous_proof: int) -> int:
    return proof ** 2 - previous_proof ** 2


def get_sha256(proof, previous_proof):
    return hashlib.sha256(str(math_func(proof, previous_proof)).encode()).hexdigest()


class Block:
    def __init__(self, index, proof, previous_hash):
        self.index = index
        self.proof = proof
        self.previous_hash = previous_hash
        self.timestamp = str(datetime.datetime.now())


class BlockEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Blockchain:
    """
    BlockChain
        [data1] -> [data2, hash(data1)] -> [data3, hash(data2)]
        proof-of-work --
        blockchain - nodes(компы)
    """

    def __init__(self, calc_complex="000000"):
        self.chain = []
        self.create_block(0, 1, "0")
        self.complex = calc_complex

    def create_block(self, index, proof=None, previous_hash=None):
        block = Block(index, proof, previous_hash)
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, proof, previous_proof, start_proof=1, calc_step=2):
        new_proof = start_proof
        check_proof = False
        while check_proof is False:
            if proof.empty():
                hash_operation = get_sha256(new_proof, previous_proof)
                if self.is_hash_complex_valid(hash_operation):
                    check_proof = True
                else:
                    new_proof += calc_step
            else:
                break
        if proof.empty():
            proof.put(new_proof)

    def hash(self, block):
        encoded_block = json.dumps(block, cls=BlockEncoder).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_hash_complex_valid(self, hash_operation):
        return hash_operation[:len(self.complex)] == self.complex

    def chain_valid(self):
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block.previous_hash != self.hash(previous_block):
                return False

            previous_proof = previous_block.proof
            proof = block.proof
            hash_operation = get_sha256(proof, previous_proof)

            if not self.is_hash_complex_valid(hash_operation):
                return False

            previous_block = block
            block_index += 1

        return True


# user -> www.vk.ru -> login(eyes) - front -> POST username, password ==> backend - АПИ
app = Flask(__name__)
blockchain = Blockchain(calc_complex="0000")


# Graphql, GRPC

# Shop - product API - REST
# POST - create new product
# PUT - change product
# PATCH - change small product
# GET - get list product


@app.route("/blockchain/mine_block", methods=["POST"])
def start_mine_block():
    previous_block = blockchain.get_previous_block()
    block_index = previous_block.index + 1
    blockchain.create_block(block_index)
    thread = Thread(target=mine_block, args=(block_index,))
    thread.start()
    return jsonify({"id нового блока": block_index}), 200


def mine_block(block_index):
    previous_block = blockchain.chain[block_index-1]
    while not previous_block.proof:
        time.sleep(2)
    previous_proof = previous_block.proof
    previous_hash = blockchain.hash(previous_block)

    new_proof_queue = Queue()
    thread1 = Process(target=blockchain.proof_of_work, args=(new_proof_queue, previous_proof, 1))
    thread2 = Process(target=blockchain.proof_of_work, args=(new_proof_queue, previous_proof, 2))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    current_block = blockchain.chain[block_index]
    current_block.previous_hash = previous_hash
    proof = new_proof_queue.get()
    current_block.proof = proof


@app.route("/blockchain/chain/is_valid", methods=["GET"])
def valid():
    return jsonify(
        {"chain_valid": "OK" if blockchain.chain_valid() else "NOT OK"}
    ), 200


@app.route("/blockchain/chain", methods=["GET"])
def get_chain():
    return Response(
        json.dumps(blockchain.chain, cls=BlockEncoder),
        mimetype='application/json'
    ),  200


@app.route("/blockchain/block/<id>", methods=["GET"])
def get_block(id):
    id = int(id)
    if 1 <= id <= len(blockchain.chain):
        block = blockchain.chain[id - 1]
        return Response(
            json.dumps(block, cls=BlockEncoder),
            mimetype='application/json'
        ), 200
    return jsonify({"message": f"there is no block with {id}"}), 200


@app.route("/blockchain/block/<id>/status", methods=["GET"])
def get_block_status(id):
    id = int(id)
    if 1 <= id <= len(blockchain.chain):
        block = blockchain.chain[id - 1]
        status = "completed" if block.proof else "in_progress"
    else:
        status = "not_found"
    return jsonify({"status": status}), 200


if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True, port=5110)
