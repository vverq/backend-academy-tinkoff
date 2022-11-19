import pytest
from blockchain import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


class TestsBlockchain:
    def test_get_blockchain_with_first_block(self, client):
        response = client.get("/blockchain/chain")
        expected_block = response.json[0]
        assert response.status_code == 200
        assert len(response.json) == 1
        assert expected_block["index"] == 0
        assert expected_block["proof"] == 1
        assert expected_block["previous_hash"] == "0"
        assert expected_block["timestamp"] != ""

    def test_mine_block(self, client):
        index_new_block = 1
        response_mine_block = client.post("/blockchain/mine_block")
        assert response_mine_block.status_code == 200
        assert response_mine_block.json["id нового блока"] == index_new_block
        response_get_chain = client.get(f"/blockchain/block/{index_new_block}")
        assert response_get_chain.status_code == 200
        response_is_valid_chain = client.get(f"/blockchain/chain/is_valid")
        assert response_is_valid_chain.status_code == 200

    def test_get_chain(self, client):
        response_get_chain = client.get(f"/blockchain/chain")
        assert response_get_chain.status_code == 200
        assert len(response_get_chain.json) == 2

    def test_status_block_completed(self, client):
        response_get_status = client.get("/blockchain/block/1/status")
        assert response_get_status.status_code == 200
        assert response_get_status.json["status"] == "completed"

    def test_status_block_not_found(self, client):
        response_get_status = client.get("/blockchain/block/3/status")
        assert response_get_status.status_code == 200
        assert response_get_status.json["status"] == "not_found"
