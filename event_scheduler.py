"""
Event Scheduler Implementation & Room Assignment Extension
Author: Sravani Karra
Role: AI / Multi-Agent Systems Intern
Company: Avaloka (Guruvai Sciences)
"""

import heapq
from typing import List, Tuple, Dict, Any


def can_attend_all(events: List[Tuple[int, int]]) -> bool:
    """
    Determines if a single person can attend all scheduled events without overlapping.
    
    Constraint:
        Adjacent events (where an event's start time equals the preceding event's end time)
        are NOT considered overlaps (e.g., (9, 10) and (10, 11) is valid).
    
    Time Complexity: O(N log N) due to sorting.
    Space Complexity: O(N) to store the sorted copy (or O(1) auxiliary if sorted in-place).
    
    Args:
        events: List of (start_time, end_time) tuples.
        
    Returns:
        True if all events can be attended without conflict, False otherwise.
    """
    if not events or len(events) <= 1:
        return True

    # Validate inputs
    for start, end in events:
        if start > end:
            raise ValueError(f"Invalid interval: start time ({start}) cannot be after end time ({end})")

    # Sort events chronologically by start time
    sorted_events = sorted(events, key=lambda x: (x[0], x[1]))

    # Check consecutive events for overlaps
    for i in range(1, len(sorted_events)):
        prev_start, prev_end = sorted_events[i - 1]
        curr_start, curr_end = sorted_events[i]

        # An overlap strictly occurs if the current event starts before the previous event ends
        if curr_start < prev_end:
            return False

    return True


def min_rooms_required(events: List[Tuple[int, int]]) -> int:
    """
    Calculates the minimum number of meeting rooms required to hold all events simultaneously.
    
    Algorithmic Approach (Min-Heap / Priority Queue):
    1. Sort events chronologically by their start times.
    2. Maintain a min-heap storing the end times of active meetings in occupied rooms.
    3. For each event:
       - If the earliest meeting in progress finishes at or before the current start time
         (earliest_end <= start), that room is freed and can be reused. We pop it from the heap.
       - Otherwise, a new room must be allocated.
       - Push the current event's end time onto the heap.
    4. The peak size of the min-heap (or its final size) represents the minimum number of rooms needed.
    
    Time Complexity: O(N log N) for sorting, plus O(N log K) for heap operations where K <= N is min rooms.
                     Overall: O(N log N).
    Space Complexity: O(N) in worst case (when all meetings overlap simultaneously).
    
    Args:
        events: List of (start_time, end_time) tuples.
        
    Returns:
        Integer representing the minimum number of rooms required.
    """
    if not events:
        return 0

    # Validate intervals
    for start, end in events:
        if start > end:
            raise ValueError(f"Invalid interval: start time ({start}) cannot be after end time ({end})")

    # Sort events by start time
    sorted_events = sorted(events, key=lambda x: (x[0], x[1]))

    # Min-heap to track the end times of ongoing meetings in each active room
    rooms_heap: List[int] = []

    for start, end in sorted_events:
        # If the earliest ending meeting has completed before or exactly when this meeting starts,
        # reuse that room by popping its previous end time.
        if rooms_heap and rooms_heap[0] <= start:
            heapq.heappop(rooms_heap)

        # Allocate the room (new or reused) by recording this meeting's end time
        heapq.heappush(rooms_heap, end)

    # The total number of rooms currently in the heap is the minimum rooms required
    return len(rooms_heap)


def _room_id_to_name(room_idx: int) -> str:
    """Helper to convert 0 -> Room A, 1 -> Room B, ... 25 -> Room Z, 26 -> Room AA, etc."""
    name = ""
    idx = room_idx
    while True:
        name = chr(ord('A') + (idx % 26)) + name
        idx = (idx // 26) - 1
        if idx < 0:
            break
    return f"Room {name}"


def schedule_events_with_rooms(events: List[Tuple[int, int]]) -> List[Dict[str, Any]]:
    """
    Future-Proofing Extension (Question 3):
    Assigns specific room names (e.g. 'Room A', 'Room B') to each event such that:
    1. No two overlapping events share the same room.
    2. Available rooms are eagerly reused with smallest lexicographical room names.
    3. The total number of distinct rooms allocated is minimized.
    
    Returns a list of dictionaries with event details, preserving original input order:
    [
        {"original_index": 0, "start": 9, "end": 10, "room": "Room A"},
        ...
    ]
    """
    if not events:
        return []

    # Store events with their original index to return results in original sequence
    indexed_events = [(event[0], event[1], idx) for idx, event in enumerate(events)]
    # Sort events by start time
    sorted_events = sorted(indexed_events, key=lambda x: (x[0], x[1]))

    # Min-heap of busy rooms: stores tuples of (end_time, room_index)
    busy_rooms_heap: List[Tuple[int, int]] = []

    # Min-heap of available/freed room indices: guarantees reusing smallest room index first
    free_rooms_pool: List[int] = []

    next_new_room_idx = 0
    assigned_schedule = [None] * len(events)

    for start, end, orig_idx in sorted_events:
        # Release all rooms that have finished before or at the current start time
        while busy_rooms_heap and busy_rooms_heap[0][0] <= start:
            _, freed_room_idx = heapq.heappop(busy_rooms_heap)
            heapq.heappush(free_rooms_pool, freed_room_idx)

        # Assign room: reuse from free pool if available; otherwise allocate next new room
        if free_rooms_pool:
            room_idx = heapq.heappop(free_rooms_pool)
        else:
            room_idx = next_new_room_idx
            next_new_room_idx += 1

        room_name = _room_id_to_name(room_idx)
        # Push to busy rooms heap with current meeting's end time
        heapq.heappush(busy_rooms_heap, (end, room_idx))

        assigned_schedule[orig_idx] = {
            "original_index": orig_idx,
            "start": start,
            "end": end,
            "room": room_name
        }

    return assigned_schedule
