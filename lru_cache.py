"""
LRU (Least Recently Used) Cache Implementation
Author: Sravani Karra
Role: AI / Multi-Agent Systems Intern
Company: Avaloka (Guruvai Sciences)
"""

from typing import Any, Optional
import threading


class Node:
    """
    Doubly Linked List node storing key, value, and pointers to prev and next nodes.
    Storing the key inside the node allows O(1) removal from the hash map upon eviction.
    """
    __slots__ = ('key', 'value', 'prev', 'next')

    def __init__(self, key: Any = None, value: Any = None):
        self.key: Any = key
        self.value: Any = value
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None


class LRUCache:
    """
    A Least Recently Used (LRU) Cache with O(1) get and put operations.
    
    Data Structure Composition:
    1. Doubly Linked List (DLL): Tracks recency of access.
       - Head (dummy node): Most recently used (MRU) items are placed immediately after head.
       - Tail (dummy node): Least recently used (LRU) items are positioned immediately before tail.
    2. Hash Map (dict): Maps key -> Node.
       - Provides O(1) direct access to any node in the DLL.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError(f"Capacity must be a positive integer, got: {capacity}")
        self.capacity: int = capacity
        self.map: dict[Any, Node] = {}

        # Sentinel dummy nodes to eliminate edge cases for empty list boundaries
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Removes an existing node from the doubly linked list in O(1) time."""
        prev_node = node.prev
        next_node = node.next
        if prev_node:
            prev_node.next = next_node
        if next_node:
            next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Inserts a node right after the dummy head (marks as Most Recently Used) in O(1) time."""
        node.next = self.head.next
        node.prev = self.head
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def _move_to_front(self, node: Node) -> None:
        """Moves an existing node to the front (MRU position) in O(1) time."""
        self._remove(node)
        self._add_to_front(node)

    def _pop_tail(self) -> Node:
        """Pops and returns the least recently used node (immediately before dummy tail) in O(1) time."""
        lru_node = self.tail.prev
        if lru_node is None or lru_node == self.head:
            raise IndexError("Cannot pop from an empty cache")
        self._remove(lru_node)
        return lru_node

    def get(self, key: Any) -> Any:
        """
        Returns the value associated with the key if it exists, otherwise returns -1.
        Marks the key as most recently used if found.
        Time Complexity: O(1)
        """
        if key not in self.map:
            return -1

        node = self.map[key]
        self._move_to_front(node)
        return node.value

    def put(self, key: Any, value: Any) -> None:
        """
        Adds or updates the key-value pair.
        If cache is at capacity, evicts the least recently used item before adding.
        Time Complexity: O(1)
        """
        if key in self.map:
            # Update existing node's value and move to MRU position
            node = self.map[key]
            node.value = value
            self._move_to_front(node)
        else:
            # Create a brand new node
            new_node = Node(key, value)
            self.map[key] = new_node
            self._add_to_front(new_node)

            # Evict LRU item if capacity is exceeded
            if len(self.map) > self.capacity:
                lru_node = self._pop_tail()
                del self.map[lru_node.key]

    def __len__(self) -> int:
        return len(self.map)

    def keys_by_recency(self) -> list[Any]:
        """Helper method for debugging/testing: returns keys from MRU to LRU."""
        keys = []
        curr = self.head.next
        while curr and curr != self.tail:
            keys.append(curr.key)
            curr = curr.next
        return keys


class ThreadSafeLRUCache(LRUCache):
    """
    Thread-Safe extension of LRUCache using a Reentrant Lock (RLock).
    Ensures safe concurrent access across multi-threaded applications and multi-agent workers.
    """

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._lock = threading.RLock()

    def get(self, key: Any) -> Any:
        with self._lock:
            return super().get(key)

    def put(self, key: Any, value: Any) -> None:
        with self._lock:
            super().put(key, value)

    def __len__(self) -> int:
        with self._lock:
            return super().__len__()

    def keys_by_recency(self) -> list[Any]:
        with self._lock:
            return super().keys_by_recency()
