"""
Comprehensive Unit Tests for LRU Cache and Event Scheduler
Author: Sravani Karra
Company: Avaloka (Guruvai Sciences)
"""

import unittest
import threading
import time
from lru_cache import LRUCache, ThreadSafeLRUCache
from event_scheduler import can_attend_all, min_rooms_required, schedule_events_with_rooms


class TestLRUCache(unittest.TestCase):

    def test_basic_operations(self):
        cache = LRUCache(2)
        cache.put(1, 100)
        cache.put(2, 200)
        self.assertEqual(cache.get(1), 100)
        cache.put(3, 300)  # Evicts key 2
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(3), 300)
        self.assertEqual(cache.get(1), 100)

    def test_update_existing_key(self):
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        cache.put(1, 99)  # Update key 1 without increasing size or evicting key 2
        self.assertEqual(cache.get(1), 99)
        cache.put(3, 30)  # Should evict key 2, NOT key 1
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(1), 99)
        self.assertEqual(cache.get(3), 30)

    def test_capacity_one(self):
        cache = LRUCache(1)
        cache.put(1, "A")
        self.assertEqual(cache.get(1), "A")
        cache.put(2, "B")
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(2), "B")

    def test_nonexistent_key(self):
        cache = LRUCache(3)
        self.assertEqual(cache.get("missing"), -1)

    def test_lru_recency_order(self):
        cache = LRUCache(3)
        cache.put("A", 1)
        cache.put("B", 2)
        cache.put("C", 3)
        # Order MRU -> LRU is C, B, A
        self.assertEqual(cache.keys_by_recency(), ["C", "B", "A"])
        # Access A
        cache.get("A")
        # Order MRU -> LRU is now A, C, B
        self.assertEqual(cache.keys_by_recency(), ["A", "C", "B"])
        # Add D -> should evict B
        cache.put("D", 4)
        self.assertEqual(cache.keys_by_recency(), ["D", "A", "C"])
        self.assertEqual(cache.get("B"), -1)


class TestThreadSafeLRUCache(unittest.TestCase):

    def test_concurrent_access(self):
        cache = ThreadSafeLRUCache(50)
        num_threads = 20
        ops_per_thread = 200

        def worker(thread_id: int):
            for i in range(ops_per_thread):
                key = (thread_id * 10 + i) % 100
                cache.put(key, f"val_{key}")
                _ = cache.get(key)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # The cache size should not exceed 50 despite heavy concurrent modifications
        self.assertLessEqual(len(cache), 50)


class TestEventScheduler(unittest.TestCase):

    def test_can_attend_all_no_conflicts(self):
        events = [(9, 10), (10, 11), (11, 12)]
        self.assertTrue(can_attend_all(events))

    def test_can_attend_all_adjacent_events(self):
        # Adjacent events are NOT overlaps
        events = [(1, 2), (2, 3), (3, 4), (4, 5)]
        self.assertTrue(can_attend_all(events))

    def test_can_attend_all_with_overlap(self):
        events = [(9, 11), (10, 12)]
        self.assertFalse(can_attend_all(events))

    def test_can_attend_all_unsorted_input(self):
        events = [(13, 14), (9, 10), (11, 12), (10, 11)]
        self.assertTrue(can_attend_all(events))

    def test_can_attend_all_empty_and_single(self):
        self.assertTrue(can_attend_all([]))
        self.assertTrue(can_attend_all([(9, 10)]))

    def test_min_rooms_required_basic(self):
        # [(0, 30), (5, 10), (15, 20)] requires 2 rooms
        events = [(0, 30), (5, 10), (15, 20)]
        self.assertEqual(min_rooms_required(events), 2)

    def test_min_rooms_required_adjacent_no_extra_room(self):
        # Adjacent events do not need separate rooms
        events = [(9, 10), (10, 11), (11, 12)]
        self.assertEqual(min_rooms_required(events), 1)

    def test_min_rooms_required_fully_overlapping(self):
        # All 3 happen simultaneously
        events = [(1, 5), (2, 6), (3, 7)]
        self.assertEqual(min_rooms_required(events), 3)

    def test_min_rooms_required_empty(self):
        self.assertEqual(min_rooms_required([]), 0)


class TestRoomAssignmentExtension(unittest.TestCase):

    def test_room_assignment_reuse(self):
        events = [(9, 10), (9, 11), (10, 12)]
        # Event 0: (9, 10) -> Room A
        # Event 1: (9, 11) -> Room B (overlaps with 0)
        # Event 2: (10, 12) -> Event 0 finished at 10, so Room A is free and should be reused!
        schedule = schedule_events_with_rooms(events)
        self.assertEqual(schedule[0]["room"], "Room A")
        self.assertEqual(schedule[1]["room"], "Room B")
        self.assertEqual(schedule[2]["room"], "Room A")

    def test_room_assignment_no_conflicts_per_room(self):
        events = [(1, 4), (2, 5), (6, 8), (5, 7), (3, 9)]
        schedule = schedule_events_with_rooms(events)

        # Check each room's assigned events for collisions
        room_events = {}
        for item in schedule:
            room = item["room"]
            room_events.setdefault(room, []).append((item["start"], item["end"]))

        for room, intervals in room_events.items():
            sorted_intervals = sorted(intervals)
            for i in range(1, len(sorted_intervals)):
                self.assertLessEqual(sorted_intervals[i - 1][1], sorted_intervals[i][0],
                                     f"Collision detected in {room}")


if __name__ == "__main__":
    unittest.main()
