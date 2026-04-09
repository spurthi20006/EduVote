import hashlib
import json
import time
from datetime import datetime


class Block:
    """A single block in the blockchain."""

    def __init__(self, index, user_id_hash, candidate, timestamp=None, previous_hash='0'):
        self.index = index
        self.user_id_hash = user_id_hash  # SHA-256 hash of the student's ID
        self.candidate = candidate
        self.timestamp = timestamp or time.time()
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'user_id_hash': self.user_id_hash,
            'candidate': self.candidate,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'user_id_hash': self.user_id_hash,
            'candidate': self.candidate,
            'timestamp': self.timestamp,
            'timestamp_readable': datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'previous_hash': self.previous_hash,
            'hash': self.hash,
        }


class Blockchain:
    """A simple blockchain for storing votes."""

    def __init__(self):
        self.chain = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = Block(
            index=0,
            user_id_hash='0' * 64,
            candidate='GENESIS',
            timestamp=0,
            previous_hash='0',
        )
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_vote(self, user_id: str, candidate: str) -> Block:
        """Hash the user ID and append a new block."""
        user_id_hash = hashlib.sha256(user_id.encode()).hexdigest()
        block = Block(
            index=len(self.chain),
            user_id_hash=user_id_hash,
            candidate=candidate,
            previous_hash=self.last_block.hash,
        )
        self.chain.append(block)
        return block

    def is_chain_valid(self) -> bool:
        """Verify integrity of the entire chain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.compute_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def get_votes_for_candidate(self, candidate: str) -> int:
        return sum(1 for b in self.chain[1:] if b.candidate == candidate)

    def get_all_votes(self) -> list:
        return [b.to_dict() for b in self.chain[1:]]


def hash_user_id(user_id: str) -> str:
    """Utility: hash a student ID for storage/display."""
    return hashlib.sha256(user_id.encode()).hexdigest()


# Global blockchain instance — loaded from DB on startup via apps.py
_blockchain_instance = None


def get_blockchain() -> Blockchain:
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = Blockchain()
    return _blockchain_instance


def reset_blockchain():
    """Re-initialise the in-memory chain (used after loading from DB)."""
    global _blockchain_instance
    _blockchain_instance = Blockchain()
    return _blockchain_instance
