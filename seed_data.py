"""Seed content for the LeetCode SRS.

Three kinds of items:
  - DS_CARDS:      data-structure recall. ONE fact per card so a grade is
                   unambiguous: you either had that fact or you didn't.
  - PATTERN_CARDS: signal -> tool decision drills. Front is a problem-shape;
                   back is the TOOL ONLY (that's what you grade on). The "why"
                   is shown after the reveal as a reminder, never as the answer.
  - PROBLEMS:      pattern-organized re-solve backlog. The point is COLD re-solve
                   from memory, not first-time exposure.

Every card carries a `hint`: a nudge that points at the answer without
containing it. Hints are the only thing `?` reveals, so a hint never hands you
the back of the card. Problems get a per-pattern nudge (PATTERN_NUDGES) as
their first hint, then the pattern name, then your own note.

Edit freely, then re-run `srs.py import`: new cards are added, problems keep
their schedules, and ds/pattern cards that no longer appear here are retired.
"""

# {"front", "back", "hint", "why"?}
DS_CARDS = [
    # hash map / set
    {"front": "Hash map: insert / lookup / delete complexity?",
     "back": "Average O(1), worst case O(n).",
     "hint": "Two numbers: the usual case and the everything-collides case."},
    {"front": "Hash map: what does it NOT give you?",
     "back": "Ordering. Keys come back in no useful order.",
     "hint": "Think about what a sorted container has that this lacks."},
    {"front": "Hash set / map: three problem signals that call for it?",
     "back": "Fast membership, counting occurrences, last-seen index of a value.",
     "hint": "All three replace a nested 'have I seen this?' scan with one pass."},
    # heap
    {"front": "Binary heap: push and pop complexity?",
     "back": "Both O(log n).",
     "hint": "Think about the height of the tree."},
    {"front": "Binary heap: peek, and build-from-a-list, complexity?",
     "back": "Peek O(1). Build-heap from n items O(n), not O(n log n).",
     "hint": "One is free; the other is cheaper than n separate pushes."},
    {"front": "Heap: four problem shapes it is built for?",
     "back": "Repeatedly take the extreme element; top-K; merge K sorted lists; streaming median.",
     "hint": "What do you keep needing again and again as the set changes?"},
    {"front": "Python heapq: which kind of heap, and how do you get the other?",
     "back": "Min-heap only. Push negated values to fake a max-heap.",
     "hint": "There is only one flavor; you fake the other with arithmetic."},
    # stack
    {"front": "Stack: order, and complexity of push / pop / peek?",
     "back": "LIFO. All O(1).",
     "hint": "Last in, ... ?"},
    {"front": "Stack: problem signals that call for it?",
     "back": "Reversal, bracket matching, undo, hand-rolled recursion, and "
             "monotonic stack (next greater / smaller element).",
     "hint": "Anything where the most recent unresolved thing is handled first."},
    # queue / deque
    {"front": "Queue vs deque: what each allows, at what cost?",
     "back": "Queue: FIFO, push back / pop front, O(1). Deque: O(1) push and pop at BOTH ends.",
     "hint": "One end versus two ends."},
    {"front": "Deque: the two classic algorithms that need it?",
     "back": "BFS (as a plain queue) and sliding-window maximum (as a monotonic deque).",
     "hint": "One graph algorithm, one array algorithm."},
    {"front": "Python: the deque class, and why not a list?",
     "back": "collections.deque. A list's pop(0) is O(n).",
     "hint": "It lives in the standard library's containers module."},
    # balanced BST / sorted container
    {"front": "Balanced BST / sorted container: insert, search, delete complexity?",
     "back": "O(log n) each.",
     "hint": "Height of a balanced tree."},
    {"front": "Sorted container: what does it buy you that a hash map cannot?",
     "back": "Order: ordered iteration, floor / ceiling (predecessor / successor), range queries.",
     "hint": "Three operations, all about a value's neighbors."},
    {"front": "Python: sorted-container options?",
     "back": "No built-in. sortedcontainers.SortedList, or bisect on a list, "
             "or a heap if you only ever need the extreme.",
     "hint": "One third-party package, two standard-library workarounds."},
    # union-find
    {"front": "Union-Find: operations and amortized complexity?",
     "back": "find and union, near O(1) amortized (inverse Ackermann) with "
             "path compression + union by rank.",
     "hint": "Two operations, two optimizations that make them nearly free."},
    {"front": "Union-Find: problem signals?",
     "back": "Connected components, cycle detection in an UNDIRECTED graph, "
             "Kruskal's MST, dynamic connectivity as edges arrive.",
     "hint": "Groups that merge and never split."},
    {"front": "Union-Find: directed or undirected cycle detection?",
     "back": "Undirected only. Directed cycles need DFS with colors or a topological sort.",
     "hint": "It does not know which way an edge points."},
    # trie
    {"front": "Trie: insert / search / startsWith complexity?",
     "back": "O(L) in the key length, independent of how many keys are stored.",
     "hint": "What does the cost depend on, and what does it NOT depend on?"},
    {"front": "Trie: problem signals?",
     "back": "Prefix lookups, autocomplete, word search on a grid with a dictionary, "
             "'does any stored word start with ...'.",
     "hint": "The word 'prefix' is usually in the problem statement."},
    # graphs representation
    {"front": "Adjacency list: space, and the operation it is fast at?",
     "back": "O(V+E) space. Iterating a node's neighbors costs its degree.",
     "hint": "Space proportional to what is actually there."},
    {"front": "Adjacency matrix: space, and the one thing it does in O(1)?",
     "back": "O(V^2) space. 'Is there an edge u->v?' in O(1).",
     "hint": "A table lookup."},
    {"front": "Adjacency list vs matrix: when do you pick the matrix?",
     "back": "Dense graphs, or when you constantly test edge existence. Otherwise the list.",
     "hint": "Compare the number of edges to V^2."},
    # bisect / binary search
    {"front": "bisect_left vs bisect_right: what index does each return?",
     "back": "An insertion index in O(log n). left = before any equal elements, right = after them.",
     "hint": "They differ only when the value is already present."},
    {"front": "bisect on a sorted list: three things you can do with it?",
     "back": "Maintain a sorted list (insort), find floor / ceiling, count elements less than x.",
     "hint": "All three are 'where would x go?'"},
    {"front": "'Binary search on the answer': what makes it applicable?",
     "back": "A feasibility check isFeasible(x) that is monotonic in x. Binary-search x "
             "over its range: O(log range) checks.",
     "hint": "You are not searching an array. What property of the check lets you halve the space?"},
    # sorting as a tool
    {"front": "Sorting first: cost, and what it unlocks?",
     "back": "O(n log n). Unlocks two pointers, binary search, greedy-by-order, interval sweeps.",
     "hint": "Often step zero of a pattern."},
]

# front = the problem-shape signal; back = the TOOL (graded); why = reminder after reveal
PATTERN_CARDS = [
    {"front": "Fast membership, dedup, or counting occurrences of values.",
     "back": "Hash set / hash map.",
     "hint": "What replaces a 'have I seen this before?' scan with one pass?",
     "why": "O(1) lookup turns an O(n^2) scan into O(n). First thing to try on most array problems."},
    {"front": "Pair / triplet hitting a target, or a palindrome check, in a SORTED array.",
     "back": "Two pointers from both ends.",
     "hint": "Sorted means you can rule out one end at a time.",
     "why": "Sortedness lets you move the pointer that provably cannot be in the answer. O(n) after the sort."},
    {"front": "Longest / shortest CONTIGUOUS subarray or substring meeting a constraint.",
     "back": "Sliding window.",
     "hint": "Contiguous. Each element should enter and leave at most once.",
     "why": "Grow the right edge; shrink the left while the window is invalid. O(n)."},
    {"front": "Next greater / smaller element, bracket matching, a monotonic relationship.",
     "back": "Stack, usually a monotonic stack.",
     "hint": "The most recent unresolved element gets resolved first.",
     "why": "Pop while the new element breaks the invariant; what you pop is resolved by the current element."},
    {"front": "Search in sorted data, OR 'minimize the maximum' / 'smallest feasible X'.",
     "back": "Binary search, including binary search on the answer.",
     "hint": "Can one yes/no check halve the candidate space?",
     "why": "If isFeasible(x) is monotonic in x, binary-search x. O(log range)."},
    {"front": "Repeatedly need the min / max of a changing set, top-K, merge-K, running median.",
     "back": "Heap / priority queue.",
     "hint": "You keep asking for the extreme element after the set changes.",
     "why": "Median: balance two heaps. Top-K: a size-K heap gives O(n log k)."},
    {"front": "Reverse / reorder a linked list, detect a cycle, or find its middle.",
     "back": "Slow and fast pointers.",
     "hint": "No random access. Two walkers at different speeds.",
     "why": "Fast moves 2x. A cycle means they meet; when fast hits the end, slow is at the middle."},
    {"front": "Hierarchical data: root-to-leaf paths, subtree properties, BST queries.",
     "back": "Tree DFS (recursion).",
     "hint": "What does each subtree need to report up to its parent?",
     "why": "Pick pre/in/post-order. Return values bubble subtree facts up; parameters push context down."},
    {"front": "Level-by-level processing, or shortest path in an UNWEIGHTED graph / grid.",
     "back": "BFS with a queue.",
     "hint": "Unweighted. First arrival wins.",
     "why": "First time you reach a node = fewest edges. Process one full level per loop iteration for depth."},
    {"front": "Connected components, flood fill, 'count the islands', undirected cycle check.",
     "back": "DFS / BFS flood fill, or Union-Find.",
     "hint": "Paint everything reachable, then move to the next unpainted cell.",
     "why": "Mark visited as you go. Union-Find shines when edges arrive incrementally."},
    {"front": "Generate ALL subsets / permutations / combinations, or 'all ways to ...'.",
     "back": "Backtracking.",
     "hint": "The output itself is exponential. What does that say about the algorithm?",
     "why": "choose -> recurse -> un-choose. Prune dead branches early. Exponential by nature."},
    {"front": "Lookups or insertions keyed by string PREFIX.",
     "back": "Trie.",
     "hint": "A tree where the path spells the key.",
     "why": "O(L) per operation regardless of how many words are stored."},
    {"front": "Optimal value (min / max / count ways) over choices with OVERLAPPING subproblems.",
     "back": "Dynamic programming.",
     "hint": "The same subproblem keeps coming back.",
     "why": "Define the state, the recurrence, and base cases. Memoize top-down or tabulate bottom-up."},
    {"front": "DP over a grid, or over TWO sequences (edit distance, LCS, alignment).",
     "back": "2-D DP table.",
     "hint": "Two indices that move independently.",
     "why": "dp[i][j] relates cell (i,j) to its neighbors or previous characters. Watch the base row / column."},
    {"front": "Weighted shortest path with NON-negative edges.",
     "back": "Dijkstra (min-heap of (dist, node)).",
     "hint": "BFS, except a plain queue is not enough because edges have weights.",
     "why": "Negative edges: Bellman-Ford. All-pairs on a small graph: Floyd-Warshall."},
    {"front": "Ordering tasks under dependencies, or 'can this be finished given prerequisites?'.",
     "back": "Topological sort.",
     "hint": "A directed graph where the answer is an order.",
     "why": "Kahn's (BFS on in-degree) or DFS post-order. A cycle means no valid ordering."},
    {"front": "Overlapping ranges: merge them, insert one, count rooms / removals.",
     "back": "Sort by start, then sweep.",
     "hint": "What order makes overlaps adjacent?",
     "why": "For 'how many overlap at once' keep a min-heap of end times (meeting rooms)."},
    {"front": "A locally optimal choice that you can PROVE is globally optimal.",
     "back": "Greedy.",
     "hint": "No table, no recursion. One pass of best-now choices, plus a proof.",
     "why": "Cheaper than DP but you must justify the exchange argument: interval scheduling, jump game, gas station."},
    {"front": "'Single number', subset enumeration by mask, parity / dedup with no extra space.",
     "back": "Bit manipulation.",
     "hint": "What operation cancels a value against itself?",
     "why": "XOR cancels pairs; (1<<i) tests / sets bits; iterate subsets with sub=(sub-1)&mask."},
    {"front": "Kth largest / smallest, but a full sort is wasteful.",
     "back": "Size-K heap (O(n log k)), or quickselect (average O(n), in place).",
     "hint": "You only need one element's rank, not everyone's.",
     "why": "Both avoid sorting everything."},
    {"front": "Two strings / arrays, comparing or transforming one into the other.",
     "back": "2-D DP (LCS / edit distance); two pointers if sorted or a subsequence check; "
             "hash map of counts for anagrams.",
     "hint": "Which relation is being asked: alignment, order, or multiset?",
     "why": "The signal is which relation the problem is about."},
    {"front": "The answer is a count of ways and small subproblems repeat.",
     "back": "DP, or plain combinatorics if the choices are independent.",
     "hint": "Do the choices interact, or is it just multiplication?",
     "why": "Sanity-check whether choices interact before building a table."},
]

# First hint for a problem, by pattern: a nudge that does not name the tool.
# (Second hint = the pattern name, third = your own insight note.)
PATTERN_NUDGES = {
    "Arrays & Hashing": "What would one pass with O(1) lookups buy you?",
    "Two Pointers": "Is the input sorted, or can you sort it? Then what can you rule out from an end?",
    "Sliding Window": "The answer is contiguous. Each element should enter and leave once.",
    "Stack": "The most recent unresolved element is the one that gets resolved next.",
    "Binary Search": "Can a single yes/no check halve the candidate space?",
    "Linked List": "No random access. Think about pointers that move at different speeds, or a dummy head.",
    "Trees": "What must each subtree report to its parent for the answer to fall out?",
    "Tries": "The word 'prefix' is the signal. A tree where the path spells the key.",
    "Heap": "You keep needing the extreme element while the set keeps changing.",
    "Backtracking": "The output is every valid arrangement. Choose, recurse, un-choose.",
    "Graphs": "Reachability or distance. Which traversal, and what do you mark?",
    "Advanced Graphs": "Weights or ordering constraints. A queue alone is not enough.",
    "1-D DP": "The answer for position i depends only on answers for earlier positions.",
    "2-D DP": "Two indices that move independently. Draw the table.",
    "Greedy": "A best-now choice that you could defend with an exchange argument.",
    "Intervals": "Sort by start. What becomes adjacent?",
    "Bit Manipulation": "Which bit operation cancels or isolates what you need?",
}

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
