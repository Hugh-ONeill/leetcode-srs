"""Seed content for the LeetCode SRS.

Three kinds of items:
  - DS_CARDS:      data-structure recall (API + complexity). Fixes "can't recall
                   the structure itself on the fly."
  - PATTERN_CARDS: signal -> pattern/structure decision drills. Fixes "I don't
                   know *which* tool a problem wants." Front is a problem-shape;
                   back is the tool + why. No coding.
  - PROBLEMS:      pattern-organized re-solve backlog. The point is COLD re-solve
                   from memory, not first-time exposure.

Edit freely, then re-run `srs.py import` to add anything new (existing items and
their schedules are left untouched).
"""

# (front, back)
DS_CARDS = [
    ("Hash map / hash set — operations and complexity?",
     "insert / lookup / delete: avg O(1), worst O(n). No ordering. "
     "Reach for it when you need fast membership, counting, or last-seen-index."),
    ("Binary heap (priority queue) — operations and complexity?",
     "push O(log n), pop-min/max O(log n), peek O(1), build-from-list O(n). "
     "Use for: repeatedly get extreme element, top-K, merge-K, streaming median. "
     "Python: heapq is a MIN-heap; push negatives for a max-heap."),
    ("Stack — behavior, ops, when to reach for it?",
     "LIFO. push/pop/peek all O(1). Use for: reversal, matching/brackets, "
     "backtracking-by-hand, undo, and monotonic-stack (next greater/smaller)."),
    ("Queue / deque — behavior, ops, uses?",
     "Queue = FIFO. deque = O(1) push/pop at BOTH ends. "
     "Use for: BFS (queue), sliding-window-maximum (monotonic deque). "
     "Python: collections.deque."),
    ("Balanced BST / sorted container — ops and what it buys you?",
     "insert / search / delete O(log n) AND ordered iteration / "
     "floor / ceiling / range queries. Use when you need a hash map's speed "
     "but ALSO order. Python has no built-in; use sortedcontainers or a heap/bisect."),
    ("Union-Find (disjoint set) — ops, complexity, uses?",
     "union + find: ~O(1) amortized with path-compression + union-by-rank. "
     "Use for: connected components, cycle detection in UNDIRECTED graphs, "
     "Kruskal's MST, dynamic connectivity."),
    ("Trie (prefix tree) — ops, complexity, uses?",
     "insert / search / startsWith: O(L) in the key length, independent of #keys. "
     "Use for: prefix lookups, autocomplete, word-search-by-prefix, "
     "dictionary problems."),
    ("Adjacency list vs adjacency matrix — when each?",
     "List: O(V+E) space, fast to iterate neighbors — default for sparse graphs. "
     "Matrix: O(V^2) space, O(1) edge lookup — only for dense graphs or when you "
     "constantly test 'is there an edge u->v?'."),
    ("bisect (binary search on a sorted list) — what does it give you?",
     "bisect_left/right find an insertion index in O(log n). Use to maintain a "
     "sorted list, find floor/ceiling, or count elements < x. The building block "
     "of 'binary search on the answer'."),
]

# (front = the problem-shape signal, back = the tool + why)
PATTERN_CARDS = [
    ("You need fast membership, dedup, or to count occurrences of values.",
     "HASH SET / HASH MAP. O(1) lookup turns an O(n^2) scan into O(n). "
     "First thing to try on most array problems."),
    ("Find a pair/triplet hitting a target, or check a palindrome, in a SORTED array.",
     "TWO POINTERS from both ends. Sortedness lets you move the pointer that "
     "provably can't be in the answer. O(n) after the sort."),
    ("Longest / shortest CONTIGUOUS subarray or substring meeting a constraint.",
     "SLIDING WINDOW. Grow the right edge; shrink the left while the window is "
     "invalid. O(n) — each element enters and leaves once."),
    ("'Next greater/smaller element', bracket matching, or a monotonic relationship.",
     "STACK (often a MONOTONIC stack). Pop while the new element breaks the "
     "invariant; what you pop is resolved by the current element."),
    ("Search in sorted data, OR 'minimize the maximum' / 'find the smallest feasible X'.",
     "BINARY SEARCH — including binary search on the ANSWER. If you can write "
     "isFeasible(x) that's monotonic in x, binary-search x. O(log range)."),
    ("Repeatedly need the min/max of a changing set, top-K, merge-K, or a running median.",
     "HEAP / PRIORITY QUEUE. For median, balance two heaps. For top-K, a size-K "
     "heap gives O(n log k)."),
    ("Reverse / reorder a linked list, detect a cycle, or find its middle.",
     "SLOW & FAST POINTERS on the linked list. Fast moves 2x; cycle => they meet, "
     "and when fast hits the end slow is at the middle."),
    ("Hierarchical data: all root-to-leaf paths, subtree properties, BST queries.",
     "TREE DFS (recursion). Decide pre/in/post-order. Return value bubbles "
     "subtree facts up; parameters push context down."),
    ("Level-by-level processing, or shortest path in an UNWEIGHTED graph/grid.",
     "BFS with a QUEUE. First time you reach a node = fewest edges. Process one "
     "full level per loop iteration when you need distance/depth."),
    ("Connected components, flood fill, 'count the islands', undirected cycle check.",
     "DFS/BFS flood fill, or UNION-FIND. Mark visited as you go. Union-Find shines "
     "when edges arrive incrementally."),
    ("Generate ALL subsets / permutations / combinations, or 'all ways to ...'.",
     "BACKTRACKING. choose -> recurse -> un-choose. Prune dead branches early. "
     "Exponential by nature; that's expected."),
    ("Lookups or insertions keyed by string PREFIX.",
     "TRIE. O(L) per operation regardless of how many words are stored."),
    ("Optimal value (min/max/count-ways) over choices with OVERLAPPING subproblems.",
     "DYNAMIC PROGRAMMING. Define the state, the recurrence, and base cases. "
     "Memoize top-down or build a table bottom-up."),
    ("DP over a grid, or over TWO sequences (edit distance, LCS, alignment).",
     "2-D DP table. dp[i][j] relates cell (i,j) to its neighbors / previous chars. "
     "Watch the base row/column."),
    ("Weighted shortest path with NON-negative edges.",
     "DIJKSTRA (min-heap of (dist, node)). Negative edges instead? Bellman-Ford. "
     "All-pairs small graph? Floyd-Warshall."),
    ("Ordering tasks under dependencies, or 'can this be finished given prerequisites?'.",
     "TOPOLOGICAL SORT. Kahn's (BFS on in-degree) or DFS post-order. "
     "A cycle => no valid ordering."),
    ("Overlapping ranges: merge them, insert one, count rooms / removals.",
     "SORT BY START, then sweep. For 'how many overlap at once' keep a MIN-HEAP "
     "of end times (meeting rooms)."),
    ("A locally-optimal choice that you can PROVE is globally optimal.",
     "GREEDY. Cheaper than DP but you must justify the exchange argument — "
     "interval scheduling, jump game, gas station."),
    ("'Single number', subset enumeration by mask, parity/dedup with no extra space.",
     "BIT MANIPULATION. XOR cancels pairs; (1<<i) tests/sets bits; iterate "
     "subsets with for sub in range(mask): sub=(sub-1)&mask."),
    ("Kth largest/smallest, but a full sort is wasteful.",
     "HEAP of size K (O(n log k)), or QUICKSELECT (avg O(n), in place)."),
    ("Two strings/arrays and you're comparing or transforming one into the other.",
     "Think 2-D DP (LCS/edit distance) OR two pointers if one is sorted/a "
     "subsequence check. Anagram/frequency compare => hash map of counts."),
    ("The answer is a count of ways and small subproblems repeat.",
     "DP, almost always. If choices are independent, it may be plain "
     "combinatorics/math instead — sanity-check before building a table."),
]

# (title, leetcode-slug, pattern, difficulty)
PROBLEMS = [
    # Arrays & Hashing
    ("Two Sum", "two-sum", "Arrays & Hashing", "Easy"),
    ("Contains Duplicate", "contains-duplicate", "Arrays & Hashing", "Easy"),
    ("Valid Anagram", "valid-anagram", "Arrays & Hashing", "Easy"),
    ("Group Anagrams", "group-anagrams", "Arrays & Hashing", "Medium"),
    ("Top K Frequent Elements", "top-k-frequent-elements", "Arrays & Hashing", "Medium"),
    ("Product of Array Except Self", "product-of-array-except-self", "Arrays & Hashing", "Medium"),
    ("Longest Consecutive Sequence", "longest-consecutive-sequence", "Arrays & Hashing", "Medium"),
    # Two Pointers
    ("Valid Palindrome", "valid-palindrome", "Two Pointers", "Easy"),
    ("Two Sum II", "two-sum-ii-input-array-is-sorted", "Two Pointers", "Medium"),
    ("3Sum", "3sum", "Two Pointers", "Medium"),
    ("Container With Most Water", "container-with-most-water", "Two Pointers", "Medium"),
    # Sliding Window
    ("Best Time to Buy and Sell Stock", "best-time-to-buy-and-sell-stock", "Sliding Window", "Easy"),
    ("Longest Substring Without Repeating Characters", "longest-substring-without-repeating-characters", "Sliding Window", "Medium"),
    ("Longest Repeating Character Replacement", "longest-repeating-character-replacement", "Sliding Window", "Medium"),
    ("Minimum Window Substring", "minimum-window-substring", "Sliding Window", "Hard"),
    # Stack
    ("Valid Parentheses", "valid-parentheses", "Stack", "Easy"),
    ("Min Stack", "min-stack", "Stack", "Medium"),
    ("Daily Temperatures", "daily-temperatures", "Stack", "Medium"),
    ("Car Fleet", "car-fleet", "Stack", "Medium"),
    ("Largest Rectangle in Histogram", "largest-rectangle-in-histogram", "Stack", "Hard"),
    # Binary Search
    ("Binary Search", "binary-search", "Binary Search", "Easy"),
    ("Search a 2D Matrix", "search-a-2d-matrix", "Binary Search", "Medium"),
    ("Koko Eating Bananas", "koko-eating-bananas", "Binary Search", "Medium"),
    ("Find Minimum in Rotated Sorted Array", "find-minimum-in-rotated-sorted-array", "Binary Search", "Medium"),
    ("Search in Rotated Sorted Array", "search-in-rotated-sorted-array", "Binary Search", "Medium"),
    # Linked List
    ("Reverse Linked List", "reverse-linked-list", "Linked List", "Easy"),
    ("Merge Two Sorted Lists", "merge-two-sorted-lists", "Linked List", "Easy"),
    ("Linked List Cycle", "linked-list-cycle", "Linked List", "Easy"),
    ("Reorder List", "reorder-list", "Linked List", "Medium"),
    ("Remove Nth Node From End of List", "remove-nth-node-from-end-of-list", "Linked List", "Medium"),
    ("LRU Cache", "lru-cache", "Linked List", "Medium"),
    # Trees
    ("Invert Binary Tree", "invert-binary-tree", "Trees", "Easy"),
    ("Maximum Depth of Binary Tree", "maximum-depth-of-binary-tree", "Trees", "Easy"),
    ("Same Tree", "same-tree", "Trees", "Easy"),
    ("Lowest Common Ancestor of a BST", "lowest-common-ancestor-of-a-binary-search-tree", "Trees", "Medium"),
    ("Binary Tree Level Order Traversal", "binary-tree-level-order-traversal", "Trees", "Medium"),
    ("Validate Binary Search Tree", "validate-binary-search-tree", "Trees", "Medium"),
    ("Kth Smallest Element in a BST", "kth-smallest-element-in-a-bst", "Trees", "Medium"),
    ("Binary Tree Maximum Path Sum", "binary-tree-maximum-path-sum", "Trees", "Hard"),
    # Tries
    ("Implement Trie (Prefix Tree)", "implement-trie-prefix-tree", "Tries", "Medium"),
    ("Design Add and Search Words Data Structure", "design-add-and-search-words-data-structure", "Tries", "Medium"),
    ("Word Search II", "word-search-ii", "Tries", "Hard"),
    # Heap / Priority Queue
    ("Kth Largest Element in a Stream", "kth-largest-element-in-a-stream", "Heap", "Easy"),
    ("Last Stone Weight", "last-stone-weight", "Heap", "Easy"),
    ("K Closest Points to Origin", "k-closest-points-to-origin", "Heap", "Medium"),
    ("Task Scheduler", "task-scheduler", "Heap", "Medium"),
    ("Find Median from Data Stream", "find-median-from-data-stream", "Heap", "Hard"),
    ("Merge k Sorted Lists", "merge-k-sorted-lists", "Heap", "Hard"),
    # Backtracking
    ("Subsets", "subsets", "Backtracking", "Medium"),
    ("Combination Sum", "combination-sum", "Backtracking", "Medium"),
    ("Permutations", "permutations", "Backtracking", "Medium"),
    ("Word Search", "word-search", "Backtracking", "Medium"),
    ("Palindrome Partitioning", "palindrome-partitioning", "Backtracking", "Medium"),
    # Graphs
    ("Number of Islands", "number-of-islands", "Graphs", "Medium"),
    ("Clone Graph", "clone-graph", "Graphs", "Medium"),
    ("Pacific Atlantic Water Flow", "pacific-atlantic-water-flow", "Graphs", "Medium"),
    ("Course Schedule", "course-schedule", "Graphs", "Medium"),
    ("Rotting Oranges", "rotting-oranges", "Graphs", "Medium"),
    ("Graph Valid Tree", "graph-valid-tree", "Graphs", "Medium"),
    # Advanced Graphs
    ("Network Delay Time", "network-delay-time", "Advanced Graphs", "Medium"),
    ("Min Cost to Connect All Points", "min-cost-to-connect-all-points", "Advanced Graphs", "Medium"),
    ("Cheapest Flights Within K Stops", "cheapest-flights-within-k-stops", "Advanced Graphs", "Medium"),
    # 1-D DP
    ("Climbing Stairs", "climbing-stairs", "1-D DP", "Easy"),
    ("House Robber", "house-robber", "1-D DP", "Medium"),
    ("Longest Increasing Subsequence", "longest-increasing-subsequence", "1-D DP", "Medium"),
    ("Coin Change", "coin-change", "1-D DP", "Medium"),
    ("Word Break", "word-break", "1-D DP", "Medium"),
    # 2-D DP
    ("Unique Paths", "unique-paths", "2-D DP", "Medium"),
    ("Longest Common Subsequence", "longest-common-subsequence", "2-D DP", "Medium"),
    ("Edit Distance", "edit-distance", "2-D DP", "Hard"),
    # Greedy
    ("Maximum Subarray", "maximum-subarray", "Greedy", "Medium"),
    ("Jump Game", "jump-game", "Greedy", "Medium"),
    ("Gas Station", "gas-station", "Greedy", "Medium"),
    # Intervals
    ("Insert Interval", "insert-interval", "Intervals", "Medium"),
    ("Merge Intervals", "merge-intervals", "Intervals", "Medium"),
    ("Non-overlapping Intervals", "non-overlapping-intervals", "Intervals", "Medium"),
    ("Meeting Rooms II", "meeting-rooms-ii", "Intervals", "Medium"),
    # Bit Manipulation
    ("Single Number", "single-number", "Bit Manipulation", "Easy"),
    ("Number of 1 Bits", "number-of-1-bits", "Bit Manipulation", "Easy"),
    ("Counting Bits", "counting-bits", "Bit Manipulation", "Easy"),
    ("Sum of Two Integers", "sum-of-two-integers", "Bit Manipulation", "Medium"),
]
