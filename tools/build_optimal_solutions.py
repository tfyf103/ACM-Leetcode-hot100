"""Write authored standalone reference programs; no solution is executed here."""
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
SOLUTIONS = {}


def add(pid, source):
    SOLUTIONS[str(pid)] = dedent(source).strip() + '\n'


add(5, '''
import sys

def solve():
    s = sys.stdin.readline().strip()
    # Separators unify odd and even palindromes; input is alphanumeric.
    transformed = '^#' + '#'.join(s) + '#$'
    radius = [0] * len(transformed)
    center = right = best_center = best_radius = 0
    for i in range(1, len(transformed) - 1):
        if i < right:
            radius[i] = min(right - i, radius[2 * center - i])
        while transformed[i - radius[i] - 1] == transformed[i + radius[i] + 1]:
            radius[i] += 1
        if i + radius[i] > right:
            center, right = i, i + radius[i]
        if radius[i] > best_radius:
            best_center, best_radius = i, radius[i]
    start = (best_center - best_radius) // 2
    print(s[start:start + best_radius])

if __name__ == '__main__':
    solve()
''')

add(215, '''
import sys

def select(values, rank):
    # Median of medians guarantees a sufficiently balanced pivot.
    while True:
        if len(values) <= 5:
            return sorted(values)[rank]
        medians = []
        for start in range(0, len(values), 5):
            group = sorted(values[start:start + 5])
            medians.append(group[len(group) // 2])
        pivot = select(medians, len(medians) // 2)
        lower, upper, equal = [], [], 0
        for value in values:
            if value < pivot:
                lower.append(value)
            elif value > pivot:
                upper.append(value)
            else:
                equal += 1
        if rank < len(lower):
            values = lower
        elif rank < len(lower) + equal:
            return pivot
        else:
            rank -= len(lower) + equal
            values = upper

def solve():
    n, k = map(int, sys.stdin.readline().split())
    values = list(map(int, sys.stdin.readline().split()))
    print(select(values, n - k))

if __name__ == '__main__':
    solve()
''')

add(347, '''
import sys
from collections import Counter

def solve():
    n, k = map(int, sys.stdin.readline().split())
    frequency = Counter(map(int, sys.stdin.readline().split()))
    buckets = [[] for _ in range(n + 1)]
    for value, count in frequency.items():
        buckets[count].append(value)
    answer = []
    for count in range(n, 0, -1):
        for value in buckets[count]:
            answer.append(value)
            if len(answer) == k:
                print(*answer)
                return

if __name__ == '__main__':
    solve()
''')

add(279, '''
import sys
from math import isqrt

def is_square(value):
    root = isqrt(value)
    return root * root == value

def solve():
    n = int(sys.stdin.readline())
    if is_square(n):
        print(1)
        return
    reduced = n
    while reduced % 4 == 0:
        reduced //= 4
    if reduced % 8 == 7:
        print(4)
        return
    for first in range(1, isqrt(n) + 1):
        if is_square(n - first * first):
            print(2)
            return
    print(3)

if __name__ == '__main__':
    solve()
''')

add(148, '''
import sys

class Node:
    def __init__(self, value=0, following=None):
        self.val, self.next = value, following

def cut(head, size):
    if head is None:
        return None
    for _ in range(size - 1):
        if head.next is None:
            break
        head = head.next
    following = head.next
    head.next = None
    return following

def merge(left, right):
    dummy = tail = Node()
    while left or right:
        if right is None or (left is not None and left.val <= right.val):
            tail.next, left = left, left.next
        else:
            tail.next, right = right, right.next
        tail = tail.next
    return dummy.next, tail

def solve():
    n = int(sys.stdin.readline())
    dummy = tail = Node()
    for value in map(int, sys.stdin.readline().split()):
        tail.next = Node(value)
        tail = tail.next
    width = 1
    while width < n:
        current, previous = dummy.next, dummy
        while current:
            left = current
            right = cut(left, width)
            current = cut(right, width)
            merged, tail = merge(left, right)
            previous.next = merged
            previous = tail
        width *= 2
    answer, current = [], dummy.next
    while current:
        answer.append(current.val)
        current = current.next
    print(*answer)

if __name__ == '__main__':
    solve()
''')

add(32, '''
import sys

def solve():
    s = sys.stdin.readline().strip()
    answer = 0
    for reverse in (False, True):
        left = right = 0
        indexes = range(len(s) - 1, -1, -1) if reverse else range(len(s))
        for i in indexes:
            if s[i] == '(':
                left += 1
            else:
                right += 1
            if left == right:
                answer = max(answer, 2 * left)
            elif (left > right if reverse else right > left):
                left = right = 0
    print(answer)

if __name__ == '__main__':
    solve()
''')

add(62, '''
import sys

def solve():
    m, n = map(int, sys.stdin.readline().split())
    total = m + n - 2
    k = min(m - 1, n - 1)
    answer = 1
    for i in range(1, k + 1):
        # C(total-k+i, i); division is exact at each step.
        answer = answer * (total - k + i) // i
    print(answer)

if __name__ == '__main__':
    solve()
''')

add(416, '''
import sys

def solve():
    n = int(sys.stdin.readline())
    values = list(map(int, sys.stdin.readline().split()))
    total = sum(values)
    if total % 2:
        print('false')
        return
    target = total // 2
    reachable = 1
    mask = (1 << (target + 1)) - 1
    for value in values:
        reachable = (reachable | (reachable << value)) & mask
        if (reachable >> target) & 1:
            print('true')
            return
    print('false')

if __name__ == '__main__':
    solve()
''')

add(22, r'''
import sys

def solve():
    n = int(sys.stdin.readline())
    path, answers = [], []
    def dfs(left, right):
        if right == n:
            answers.append(''.join(path))
            return
        if left < n:
            path.append('(')
            dfs(left + 1, right)
            path.pop()
        if right < left:
            path.append(')')
            dfs(left, right + 1)
            path.pop()
    dfs(0, 0)
    print(len(answers))
    print('\n'.join(answers))

if __name__ == '__main__':
    solve()
''')

add(51, r'''
import sys

def solve():
    n = int(sys.stdin.readline())
    full = (1 << n) - 1
    path, answers = [], []
    def dfs(columns, left_diagonal, right_diagonal):
        if columns == full:
            answers.append(' '.join(map(str, path)))
            return
        available = full & ~(columns | left_diagonal | right_diagonal)
        while available:
            bit = available & -available
            available -= bit
            path.append(bit.bit_length())
            dfs(columns | bit, (left_diagonal | bit) << 1,
                (right_diagonal | bit) >> 1)
            path.pop()
    dfs(0, 0, 0)
    print(len(answers))
    if answers:
        print('\n'.join(answers))

if __name__ == '__main__':
    solve()
''')

add(394, '''
import sys

def solve():
    encoded = sys.stdin.readline().strip()
    root, current, stack, number = [], [], [], 0
    root = current
    for char in encoded:
        if char.isdigit():
            number = number * 10 + int(char)
        elif char == '[':
            stack.append((current, number))
            current, number = [], 0
        elif char == ']':
            parent, repeat = stack.pop()
            if current:
                if repeat == 1 and len(current) == 1:
                    item = current[0]  # Remove unary wrappers.
                elif len(current) == 1 and isinstance(current[0], tuple):
                    child_repeat, children = current[0]
                    item = (repeat * child_repeat, children)
                else:
                    item = (repeat, current)
                parent.append(item)
            current = parent
        else:
            current.append(char)
    output, work = [], [(root, 0, 1)]
    while work:
        items, index, repeats = work.pop()
        if index == len(items):
            if repeats > 1:
                work.append((items, 0, repeats - 1))
            continue
        work.append((items, index + 1, repeats))
        item = items[index]
        if isinstance(item, str):
            output.append(item)
        else:
            repeat, children = item
            work.append((children, 0, repeat))
    print(''.join(output))

if __name__ == '__main__':
    solve()
''')

add(138, '''
import sys

class Node:
    def __init__(self, value):
        self.val, self.next, self.random = value, None, None

def clone(head):
    current = head
    while current:
        following = current.next
        copy = Node(current.val)
        current.next, copy.next = copy, following
        current = following
    current = head
    while current:
        current.next.random = current.random.next if current.random else None
        current = current.next.next
    new_head = head.next if head else None
    current = head
    while current:
        copy = current.next
        current.next = copy.next
        copy.next = copy.next.next if copy.next else None
        current = current.next
    return new_head

def solve():
    n = int(sys.stdin.readline())
    originals = [Node(value) for value in map(int, sys.stdin.readline().split())]
    indexes = list(map(int, sys.stdin.readline().split()))
    for i, current in enumerate(originals):
        current.next = originals[i + 1] if i + 1 < n else None
        current.random = originals[indexes[i]] if indexes[i] >= 0 else None
    current = clone(originals[0] if n else None)
    copies = []
    while current:
        copies.append(current)
        current = current.next
    positions = {item: i for i, item in enumerate(copies)}
    print(n)
    print(*(item.val for item in copies))
    print(*(positions.get(item.random, -1) for item in copies))

if __name__ == '__main__':
    solve()
''')

add(70, '''
import sys

def solve():
    n = int(sys.stdin.readline())
    index = n + 1
    a, b = 0, 1  # F(k), F(k+1), initially k=0.
    for shift in range(index.bit_length() - 1, -1, -1):
        even = a * (2 * b - a)
        odd = a * a + b * b
        if (index >> shift) & 1:
            a, b = odd, even + odd
        else:
            a, b = even, odd
    print(a)

if __name__ == '__main__':
    solve()
''')

add(139, '''
import sys

def solve():
    s = sys.stdin.readline().strip()
    n = int(sys.stdin.readline())
    trie, longest = {}, 0
    for _ in range(n):
        word = sys.stdin.readline().strip()
        longest = max(longest, len(word))
        current = trie
        for char in word:
            current = current.setdefault(char, {})
        current['#'] = True
    reachable = [False] * (len(s) + 1)
    reachable[0] = True
    for start in range(len(s)):
        if not reachable[start]:
            continue
        current = trie
        for end in range(start, min(len(s), start + longest)):
            if s[end] not in current:
                break
            current = current[s[end]]
            if '#' in current:
                reachable[end + 1] = True
    print('true' if reachable[-1] else 'false')

if __name__ == '__main__':
    solve()
''')

if __name__ == '__main__':
    for pid, source in SOLUTIONS.items():
        compile(source, 'problem-' + pid, 'exec')
    (ROOT / 'catalog/optimal_solutions.json').write_text(
        json.dumps(SOLUTIONS, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Wrote %d optimized standalone programs.' % len(SOLUTIONS))
