from ethereum.utils import sha3
from plasma_core.constants import NULL_HASH
from .exceptions import NonexistentMemberException


class Node(object):
    """Represents a node in a Merkle tree.

    Attributes:
        data (bytes): Data stored at this node.
        left (Node): Left child of this node.
        right (Node): Right child of this node.
    """

    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right


class FixedMerkle(object):
    """Represents a fixed depth Merkle tree.

    Attributes:
        depth (int): Depth of the tree.
        leaves (bytes[]): List of hashed leaves in this tree.
        tree (Node[]): How much value is being exited.
    """

    def __init__(self, depth, leaves=[]):
        if depth < 1:
            raise ValueError('depth should be at least 1')

        self.depth = depth

        leaf_count = 2 ** depth
        if len(leaves) > leaf_count:
            raise ValueError('too many leaves for the specified depth')

        hashed_leaves = [sha3(leaf) for leaf in leaves]
        self.leaves = hashed_leaves + [sha3(NULL_HASH)] * (leaf_count - len(hashed_leaves))
        self.tree = [[Node(leaf) for leaf in self.leaves]]
        self._create_tree(self.tree[0])

    def check_membership(self, leaf, index, proof):
        """Checks the validity of a Merkle proof.

        Args:
            leaf (bytes): Data at the given leaf.
            index (int): Index of the leaf in the tree.
            proof (bytes): A proof for that leaf.

        Returns:
            bool: True if the leaf is in the tree, False otherwise.
        """

        leaf = sha3(leaf)
        computed_hash = leaf
        for i in range(0, self.depth * 32, 32):
            segment = proof[i:i + 32]
            if index % 2 == 0:
                computed_hash = sha3(computed_hash + segment)
            else:
                computed_hash = sha3(segment + computed_hash)
            index = index // 2
        return computed_hash == self.root

    def create_membership_proof(self, leaf):
        """Creates a membership proof for a leaf.

        Args:
            leaf (bytes): Data for some leaf in the tree.

        Returns:
            bytes: A Merkle proof for the leaf.
        """

        leaf = sha3(leaf)
        if not self._is_member(leaf):
            raise NonexistentMemberException('leaf is not in the merkle tree')

        index = self.leaves.index(leaf)
        proof = b''
        for i in range(0, self.depth, 1):
            sibling_index = index + (1 if index % 2 == 0 else -1)
            index = index // 2
            proof += self.tree[i][sibling_index].data
        return proof

    def _create_tree(self, nodes):
        """Recursively creates the tree given a set of nodes.

        Args:
            nodes (Node[]): A set of nodes for a specific depth.
        """

        if len(nodes) == 1:
            self.root = nodes[0].data
            return self.root

        next_level = len(nodes)
        tree_level = []
        for i in range(0, next_level, 2):
            combined = sha3(nodes[i].data + nodes[i + 1].data)
            next_node = Node(combined, nodes[i], nodes[i + 1])
            tree_level.append(next_node)

        self.tree.append(tree_level)
        self._create_tree(tree_level)

    def _is_member(self, leaf):
        """Checks if a leaf is in the set of stored leaves.

        Args:
            leaves (bytes): A set of nodes for a specific depth.

        Returns:
            bool: True if the leaf is in the set, False otherwise
        """

        return leaf in self.leaves
