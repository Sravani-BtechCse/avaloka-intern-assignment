# Data Structures & Systems Design — Take-Home Assessment
**Candidate:** Sravani Karra  
**Position:** AI / Multi-Agent Systems Intern  
**Company:** Avaloka (Guruvai Sciences)  
**Submission Document:** `Sravani_Karra_Avaloka_Assignment.pdf`

---

## Repository Structure

```
├── lru_cache.py            # Problem 1: O(1) LRU Cache + ThreadSafeLRUCache extension
├── event_scheduler.py      # Problem 2: can_attend_all, min_rooms_required + Room assignment engine
├── test_assignment.py      # Full test suite (17 automated tests covering all edge cases)
├── document.html           # Source HTML for the formal report
├── build_submission_pdf.py # Build script converting document.html to submission PDF
├── Sravani_Karra_Avaloka_Assignment.pdf # Final compiled submission PDF
└── README.md               # Project documentation and architectural overview
```

---

## 1. Problem 1: LRU (Least Recently Used) Cache Implementation

### 1.1 Approach & Architectural Logic
An LRU cache retains a fixed capacity $C$ of items, evicting the least recently used item when space is exhausted. To achieve **guaranteed $O(1)$ worst-case time complexity** for both `get(key)` and `put(key, value)`:
- **Hash Map (`dict` in Python):** Maps `key -> Node`. Yields $O(1)$ average and amortized lookup for any node.
- **Doubly Linked List (DLL):** Maintains recency ordering. Each node stores `(key, value, prev, next)`. Direct node references allow unlinking and splicing in $O(1)$ time without scanning.
- **Sentinel Dummy Nodes (`head` and `tail`):** The Most Recently Used (MRU) item always sits at `head.next`, and the Least Recently Used (LRU) item always sits at `tail.prev`. Sentinels eliminate null checks and edge-case branching.
- **Key in Node:** When evicting `tail.prev`, having `node.key` enables immediate $O(1)$ deletion from the hash map.

### 1.2 Complexity
- **`get(key)`:** $O(1)$ Time | $O(1)$ Auxiliary Space
- **`put(key, value)`:** $O(1)$ Time | $O(1)$ Auxiliary Space
- **Total Space:** $O(C)$ where $C$ is cache capacity.

---

## 2. Problem 2: Event Scheduler

### 2.1 Approach & Algorithmic Logic
Given a list of event intervals `(start_time, end_time)` where adjacent events (`end == start`) do not conflict:

#### `can_attend_all(events)`
1. Sort intervals chronologically by `start_time` in $O(N \log N)$ time.
2. In a single linear pass ($O(N)$), verify that no consecutive events overlap: `curr_start < prev_end` indicates a conflict. If strictly less, return `False`. If all pass, return `True`.

#### `min_rooms_required(events)`
1. Sort intervals chronologically by `start_time`.
2. Maintain a **Min-Heap (Priority Queue)** of active meeting end times. The root (`heap[0]`) holds the earliest finishing meeting.
3. For each meeting `(start, end)`:
   - If `heap[0] <= start`, that room has become vacant and is reused via `heapq.heappop`.
   - If `heap[0] > start`, all active rooms are occupied, requiring a new room.
   - Push `end` to the heap via `heapq.heappush`.
4. The size of the heap after processing all events is the minimum number of rooms required.

---

## 3. Final Discussion & Systems Analysis

### Q1: Time & Space Complexity
| Function / Component | Time Complexity | Auxiliary Space |
| :--- | :--- | :--- |
| `LRUCache.get(key)` | $O(1)$ amortized | $O(1)$ |
| `LRUCache.put(key, value)` | $O(1)$ amortized | $O(1)$ |
| `LRUCache` (overall storage) | - | $O(C)$ where $C$ is capacity |
| `can_attend_all(events)` | $O(N \log N)$ | $O(N)$ (sorted copy) |
| `min_rooms_required(events)` | $O(N \log N)$ | $O(N)$ (heap + sorted copy) |
| `schedule_events_with_rooms(events)` | $O(N \log N)$ | $O(N)$ |

### Q2: Trade-offs (Hash Map + Doubly Linked List)
- **Arrays:** $O(1)$ index access, but arbitrary deletion / reordering shifts up to $N$ elements ($O(N)$).
- **Singly Linked Lists:** Cannot delete an arbitrary node in $O(1)$ because finding the predecessor requires $O(N)$ traversal.
- **Balanced BSTs:** Require $O(\log N)$ for both lookups and tree rebalancing.
- **Trade-off:** We invest a small, constant memory overhead per node (`prev` and `next` pointers) to achieve deterministic $O(1)$ latency.

### Q3: Future Proofing — Room Naming Engine
Implemented in `schedule_events_with_rooms`:
- Uses two heaps:
  - `busy_rooms_heap`: Tracks `(end_time, room_id)` to release rooms whose meetings finished.
  - `free_rooms_pool`: A min-heap of free room indices (`0 -> Room A`, `1 -> Room B`, etc.) ensuring lowest lexicographical room names are prioritized upon reuse.
- Minimizes total rooms allocated and guarantees zero conflicts per room.

### Q4: Concurrency & Multi-Agent Thread Safety
- **LRU Read-is-a-Write Trap:** In an LRU cache, `get()` updates node positions in the DLL. Without synchronization, concurrent readers corrupt DLL pointers.
- **Implementation:** `ThreadSafeLRUCache` uses `threading.RLock()` to guarantee thread safety.
- **High-Concurrency Architectures:**
  1. *Sharded / Striped Cache:* Partition cache into $M$ independent segments by `hash(key) % M`, dividing lock contention by $M$.
  2. *Asynchronous Buffer (Caffeine / Guava pattern):* `get()` acquires read-lock on dict and emits keys to a ring-buffer; a background thread updates DLL recency.

---

## 4. Running Tests

Run the full automated test suite (17 tests):
```bash
python -m unittest test_assignment.py -v
```

All 17 tests validate:
- Basic LRU cache operations
- Capacity limits and eviction sequence
- In-place key updates
- Single-capacity edge cases
- Event scheduler non-overlapping and overlapping intervals
- Adjacent event boundary conditions
- Multi-room allocations
- Dynamic room identifier reuse ("Room A", "Room B", ...)
- Multi-threaded stress test with 20 concurrent threads running 4,000 operations
