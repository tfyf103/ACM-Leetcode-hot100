"""Original ACM adaptations: linked lists and binary trees (29 problems)."""
from collections import deque
from textwrap import dedent

PROBLEMS = []
CHECKERS = {}

STARTER = '''import sys


def solve():
    # 按题目中的 ACM 输入格式读取数据，实现算法并打印答案。
    input = sys.stdin.readline
    pass


if __name__ == "__main__":
    solve()
'''

LINKED = '''import sys
from collections import deque
import heapq
input = sys.stdin.readline

class Node:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def make(values):
    dummy = Node()
    tail = dummy
    for value in values:
        tail.next = Node(value)
        tail = tail.next
    return dummy.next

def read_list():
    n = int(input())
    values = list(map(int, input().split()))
    return make(values)

def emit(head):
    values = []
    while head:
        values.append(head.val)
        head = head.next
    print(*values)

'''

TREE = '''import sys
from collections import deque
sys.setrecursionlimit(20000)
input = sys.stdin.readline

class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def read_tree():
    n = int(input())
    tokens = input().split()
    if not tokens or tokens[0] == 'null':
        return None
    root = Node(int(tokens[0]))
    queue = deque([root])
    index = 1
    while queue and index < len(tokens):
        node = queue.popleft()
        if tokens[index] != 'null':
            node.left = Node(int(tokens[index]))
            queue.append(node.left)
        index += 1
        if index < len(tokens):
            if tokens[index] != 'null':
                node.right = Node(int(tokens[index]))
                queue.append(node.right)
            index += 1
    return root

def emit_tree(root):
    if root is None:
        print('null')
        return
    queue = deque([root])
    tokens = []
    while queue:
        node = queue.popleft()
        if node is None:
            tokens.append('null')
        else:
            tokens.append(str(node.val))
            queue.extend([node.left, node.right])
    while tokens and tokens[-1] == 'null':
        tokens.pop()
    print(*tokens)

'''

LIST_INPUT = '第一行是长度 n；第二行是 n 个整数，按 next 顺序给出链表。n=0 时第二行为空行。'
LIST_OUTPUT = '输出结果链表的结点值，以空格分隔；空链表输出空行。'
TREE_INPUT = ('第一行是层序序列的 token 数 m；第二行是 m 个 token，整数表示结点、null 表示空孩子。'
              '从根开始，依次为队列中每个非空结点读取左、右孩子；末尾缺少的孩子均视为空，允许末尾多余的 null。'
              '空树写作 m=1、序列 null。')
TREE_OUTPUT = '输出结果树的层序序列，整数与 null 以空格分隔，不输出 token 数；允许省略末尾 null，空树输出 null。'


def _add(pid, title, slug, difficulty, category, description, input_format,
         output_format, constraints, cases, body, explanation, header=LINKED):
    tests = [{'input': i, 'output': o} for i, o in cases]
    PROBLEMS.append(dict(
        id=pid, title=title, slug=slug, difficulty=difficulty, category=category,
        description=description, input_format=input_format, output_format=output_format,
        constraints=constraints, examples=[dict(tests[0], explanation='按上述输入格式构造数据后，得到所示答案。')],
        tests=tests, starter=STARTER,
        solution=header + dedent(body).strip() + '\n', explanation=explanation, compare='tokens'))


def _list(values):
    return str(len(values)) + '\n' + ' '.join(map(str, values)) + '\n'


def _tree(tokens):
    return str(len(tokens.split())) + '\n' + tokens + '\n'


def _tree_tokens_match(stdin, actual, expected):
    def normalize(text):
        tokens = text.split()
        if not tokens:
            return None
        while len(tokens) > 1 and tokens[-1] == 'null':
            tokens.pop()
        return tokens
    return normalize(actual) == normalize(expected)


_add(160, '相交链表', 'intersection-of-two-linked-lists', 'Easy', '链表',
     '两条无环单链表可能在某个结点开始共享后缀。请用结点身份判断交点，输出第一个共享结点的值。不同结点即使值相同，也不算相交。',
     '第一行 a b c，分别是 A 独有前缀、B 独有前缀、共享后缀的长度。接下来三行依次给出这三段的值；长度为 0 时对应行为空。建链时让两个独有前缀的末尾连接到同一条共享后缀，c=0 表示不相交。',
     '有交点时输出第一个共享结点的值，否则输出 null。',
     ['0 ≤ a,b,c ≤ 1000', '-10000 ≤ 结点值 ≤ 10000'],
     [('2 3 3\n4 1\n5 6 1\n8 4 5\n', '8\n'),
      ('2 2 0\n1 2\n1 2\n\n', 'null\n'),
      ('0 0 1\n\n\n7\n', '7\n'),
      ('0 2 2\n\n3 4\n5 6\n', '5\n'),
      ('0 0 0\n\n\n\n', 'null\n')], '''
    a, b, c = map(int, input().split())
    av = list(map(int, input().split()))
    bv = list(map(int, input().split()))
    cv = list(map(int, input().split()))
    common = make(cv)
    def attach(values):
        dummy = Node()
        tail = dummy
        for value in values:
            tail.next = Node(value)
            tail = tail.next
        tail.next = common
        return dummy.next
    head_a, head_b = attach(av), attach(bv)
    p, q = head_a, head_b
    while p is not q:
        p = p.next if p else head_b
        q = q.next if q else head_a
    print(p.val if p else 'null')
''', '先按输入构建共享后缀；两个指针分别遍历 A+B 和 B+A，走过相同总长度后在交点或 None 相遇。算法按对象身份比较。寻找交点时间 O(a+b+c)，额外空间 O(1)，不计建链。ACM 输入显式编码了共享关系，练习时应完成建链和双指针过程。')

_add(206, '反转链表', 'reverse-linked-list', 'Easy', '链表',
     '将单链表的 next 指针全部反向，返回新的头结点。请练习使用指针原地反转。',
     LIST_INPUT, LIST_OUTPUT, ['0 ≤ n ≤ 3000', '-10000 ≤ 结点值 ≤ 10000'],
     [(_list([1,2,3,4,5]), '5 4 3 2 1\n'), (_list([]), '\n'), (_list([8]), '8\n'),
      (_list([1,2]), '2 1\n'), (_list([-1,0,-1]), '-1 0 -1\n')], '''
    current = read_list()
    previous = None
    while current:
        following = current.next
        current.next = previous
        previous, current = current, following
    emit(previous)
''', '维护已反转前缀 previous 与未处理结点 current。先保存 next，再把指针指向前驱。时间 O(n)，额外空间 O(1)，不计输入输出。标准输入输出判题只能检查最终值序列，无法强制验证指针是否原地修改。')

_add(234, '回文链表', 'palindrome-linked-list', 'Easy', '链表',
     '判断单链表从前往后与从后往前的值是否完全相同。空链表视为回文。尝试只使用常数额外空间。',
     LIST_INPUT, '是回文输出 true，否则输出 false。', ['0 ≤ n ≤ 3000', '0 ≤ 结点值 ≤ 9'],
     [(_list([1,2,2,1]), 'true\n'), (_list([1,2]), 'false\n'), (_list([]), 'true\n'),
      (_list([7]), 'true\n'), (_list([1,2,3,2,1]), 'true\n'), (_list([1,2,3,1]), 'false\n')], '''
    head = read_list()
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    previous = None
    while slow:
        following = slow.next
        slow.next = previous
        previous, slow = slow, following
    left, right = head, previous
    ok = True
    while right:
        if left.val != right.val:
            ok = False
            break
        left, right = left.next, right.next
    print('true' if ok else 'false')
''', '快慢指针定位中点，反转后半段，再逐结点比较。奇数长度时中点与自身比较不影响结果。时间 O(n)，额外空间 O(1)。若调用者要求保留原链表，可在比较后再次反转后半段；本题只输出判断结果。')

_CYCLE_INPUT = LIST_INPUT + '第三行是 pos：-1 表示尾结点指向空；否则尾结点指向从 0 开始编号的第 pos 个结点。'
_CYCLE_HEADER = LINKED + '''n = int(input())
values = list(map(int, input().split()))
pos = int(input())
nodes = [Node(value) for value in values]
for i in range(n - 1):
    nodes[i].next = nodes[i + 1]
if n and pos != -1:
    nodes[-1].next = nodes[pos]
head = nodes[0] if nodes else None
'''

_add(141, '环形链表', 'linked-list-cycle', 'Easy', '链表',
     '判断按给定连接关系构造的单链表是否存在环。请在建链后使用快慢指针判断。',
     _CYCLE_INPUT, '存在环输出 true，否则输出 false。',
     ['0 ≤ n ≤ 3000', 'pos=-1 或 0 ≤ pos < n；n=0 时 pos=-1'],
     [(_list([3,2,0,-4])+'1\n', 'true\n'), (_list([])+'-1\n', 'false\n'),
      (_list([1])+'0\n', 'true\n'), (_list([1])+'-1\n', 'false\n'),
      (_list([1,1,1])+'-1\n', 'false\n'), (_list([1,2])+'0\n', 'true\n')], '''
    slow = fast = head
    found = False
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            found = True
            break
    print('true' if found else 'false')
''', '慢指针走一步，快指针走两步。有环时它们最终按结点身份相遇；快指针先遇到空则无环。时间 O(n)，判环额外空间 O(1)。输入 pos 用于序列化指针结构，直接读取 pos 无法训练判环算法。', header=_CYCLE_HEADER)

_add(142, '环形链表 II', 'linked-list-cycle-ii', 'Medium', '链表',
     '返回单链表环入口结点在原始输入序列中的下标。如果没有环，返回 -1。建链后请用快慢指针寻找入口。',
     _CYCLE_INPUT, '输出环入口的 0-based 下标；无环输出 -1。',
     ['0 ≤ n ≤ 3000', 'pos=-1 或 0 ≤ pos < n；n=0 时 pos=-1'],
     [(_list([3,2,0,-4])+'1\n', '1\n'), (_list([])+'-1\n', '-1\n'),
      (_list([5])+'0\n', '0\n'), (_list([2,2,2])+'2\n', '2\n'),
      (_list([1,2,3])+'-1\n', '-1\n'), (_list([8,7])+'0\n', '0\n')], '''
    slow = fast = head
    meeting = None
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            meeting = slow
            break
    if meeting is None:
        print(-1)
    else:
        pointer = head
        index = 0
        while pointer is not meeting:
            pointer, meeting = pointer.next, meeting.next
            index += 1
        print(index)
''', '快慢指针相遇后，把一个指针放回头结点，两个指针每次都走一步，再次相遇的位置就是入口。返回头指针走过的步数。时间 O(n)，寻找入口额外空间 O(1)。pos 只是输入中的建链描述，stdio 判题不能强制要求使用快慢指针。', header=_CYCLE_HEADER)

_add(21, '合并两个有序链表', 'merge-two-sorted-lists', 'Easy', '链表',
     '把两个非递减单链表合并成一个非递减链表。重复值必须全部保留。',
     '依次输入两条链表，每条均按以下两行格式给出：'+LIST_INPUT,
     LIST_OUTPUT, ['每条链表长度 0 到 1500', '-10000 ≤ 结点值 ≤ 10000，输入各自非递减'],
     [(_list([1,2,4])+_list([1,3,4]), '1 1 2 3 4 4\n'), (_list([])+_list([]), '\n'),
      (_list([])+_list([0]), '0\n'), (_list([-3,-1])+_list([-2,2]), '-3 -2 -1 2\n'),
      (_list([1,1])+_list([1]), '1 1 1\n')], '''
    a, b = read_list(), read_list()
    dummy = tail = Node()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a if a else b
    emit(dummy.next)
''', '使用哑结点和尾指针，每次把较小头结点接到结果末尾。某条链表为空后接上另一条剩余部分。时间 O(n+m)，额外空间 O(1)，复用原结点。')

_add(2, '两数相加', 'add-two-numbers', 'Medium', '链表',
     '两条非空链表分别按低位在前存储两个非负整数，每个结点是一位十进制数字。返回相加结果的同样表示。除数字 0 外，输入最高位不为 0。',
     '依次输入两条链表，每条使用长度一行、数字序列一行的格式。', LIST_OUTPUT,
     ['1 ≤ 每条链表长度 ≤ 1000', '0 ≤ 每个结点值 ≤ 9'],
     [(_list([2,4,3])+_list([5,6,4]), '7 0 8\n'), (_list([0])+_list([0]), '0\n'),
      (_list([9,9])+_list([1]), '0 0 1\n'), (_list([1])+_list([8]), '9\n'),
      (_list([9,9,9])+_list([9,9]), '8 9 0 1\n')], '''
    a, b = read_list(), read_list()
    dummy = tail = Node()
    carry = 0
    while a or b or carry:
        total = carry
        if a:
            total += a.val
            a = a.next
        if b:
            total += b.val
            b = b.next
        carry, digit = divmod(total, 10)
        tail.next = Node(digit)
        tail = tail.next
    emit(dummy.next)
''', '模拟竖式加法，从最低位逐位处理，使用 carry 保存进位。任意一条链表或进位仍存在时继续。时间 O(max(n,m))，除输出链表外额外空间 O(1)。')

_add(19, '删除链表的倒数第 N 个结点', 'remove-nth-node-from-end-of-list', 'Medium', '链表',
     '删除单链表中倒数第 k 个结点，返回删除后的链表。倒数第 1 个就是尾结点。',
     LIST_INPUT+'第三行是整数 k。', LIST_OUTPUT, ['1 ≤ n ≤ 3000', '1 ≤ k ≤ n'],
     [(_list([1,2,3,4,5])+'2\n', '1 2 3 5\n'), (_list([1])+'1\n', '\n'),
      (_list([1,2])+'2\n', '2\n'), (_list([1,2])+'1\n', '1\n'),
      (_list([3,3,4])+'2\n', '3 4\n')], '''
    head = read_list()
    k = int(input())
    dummy = Node(0, head)
    fast = slow = dummy
    for _ in range(k + 1):
        fast = fast.next
    while fast:
        fast, slow = fast.next, slow.next
    slow.next = slow.next.next
    emit(dummy.next)
''', '哑结点统一处理删除头结点的情况。快指针先走 k+1 步，随后双指针同步前进；快指针到空时，慢指针是待删结点的前驱。时间 O(n)，额外空间 O(1)。')

_add(24, '两两交换链表中的结点', 'swap-nodes-in-pairs', 'Medium', '链表',
     '依次交换单链表中相邻的两结点，最后落单的结点保留。训练目标是调整 next 指针而不交换结点内的值。',
     LIST_INPUT, LIST_OUTPUT, ['0 ≤ n ≤ 3000'],
     [(_list([1,2,3,4]), '2 1 4 3\n'), (_list([]), '\n'), (_list([1]), '1\n'),
      (_list([1,2,3]), '2 1 3\n'), (_list([1,1,2,2,3]), '1 1 2 2 3\n')], '''
    head = read_list()
    dummy = previous = Node(0, head)
    while previous.next and previous.next.next:
        first = previous.next
        second = first.next
        first.next = second.next
        second.next = first
        previous.next = second
        previous = first
    emit(dummy.next)
''', '保存待交换的 first 与 second，将前驱连接 second、second 连接 first、first 连接下一段。时间 O(n)，额外空间 O(1)。stdio 判题检查值序列，不能验证是否真的交换了结点身份。')

_add(25, 'K 个一组翻转链表', 'reverse-nodes-in-k-group', 'Hard', '链表',
     '每 k 个结点为一组，原地反转每个完整组的 next 指针。剩余不足 k 个结点时保持该段顺序。',
     LIST_INPUT+'第三行是整数 k。', LIST_OUTPUT, ['0 ≤ n ≤ 3000', '1 ≤ k ≤ 3000'],
     [(_list([1,2,3,4,5])+'2\n', '2 1 4 3 5\n'), (_list([1,2,3,4,5])+'3\n', '3 2 1 4 5\n'),
      (_list([])+'2\n', '\n'), (_list([1,2])+'3\n', '1 2\n'),
      (_list([1,2,3])+'1\n', '1 2 3\n'), (_list([1,2,3,4])+'4\n', '4 3 2 1\n')], '''
    head = read_list()
    k = int(input())
    dummy = group_previous = Node(0, head)
    while True:
        kth = group_previous
        for _ in range(k):
            kth = kth.next
            if kth is None:
                break
        if kth is None:
            break
        group_next = kth.next
        current = group_previous.next
        previous = group_next
        while current is not group_next:
            following = current.next
            current.next = previous
            previous, current = current, following
        old_first = group_previous.next
        group_previous.next = kth
        group_previous = old_first
    emit(dummy.next)
''', '先检查当前段是否有 k 个结点，记录下一组头结点，再只反转这一段，最后接回前驱并推进。时间 O(n)，额外空间 O(1)。stdio 仅检查最终序列，不能强制原地修改；参考代码实际执行指针反转。')

_add(138, '随机链表的复制', 'copy-list-with-random-pointer', 'Medium', '链表',
     '每个结点除了 next 还有 random 指针，可指向任意结点或空。构造结构相同但结点全部新建的深拷贝，并输出拷贝的结构。ACM 输出只能检查结构，不能证明新旧结点在内存中相互独立。',
     '第一行 n；第二行 n 个结点值，按 next 顺序排列；第三行 n 个 random 下标，-1 表示空，否则是 0-based 下标。n=0 时后两行为空。',
     '输出三行：结点数 n；拷贝链表按 next 顺序的值；拷贝链表中每个 random 指向的 0-based 下标或 -1。空表仍输出 0 和两个空行。',
     ['0 ≤ n ≤ 1000', '-10000 ≤ 结点值 ≤ 10000', 'random 下标为 -1 或 [0,n)'],
     [('5\n7 13 11 10 1\n-1 0 4 2 0\n', '5\n7 13 11 10 1\n-1 0 4 2 0\n'),
      ('0\n\n\n', '0\n\n\n'), ('1\n8\n0\n', '1\n8\n0\n'),
      ('1\n-2\n-1\n', '1\n-2\n-1\n'), ('3\n1 1 1\n2 0 1\n', '3\n1 1 1\n2 0 1\n')], '''
    n = int(input())
    values = list(map(int, input().split()))
    random_indices = list(map(int, input().split()))
    originals = [Node(value) for value in values]
    for i, node in enumerate(originals):
        node.next = originals[i + 1] if i + 1 < n else None
        node.random = originals[random_indices[i]] if random_indices[i] != -1 else None
    copies = {None: None}
    for node in originals:
        copies[node] = Node(node.val)
    for node in originals:
        copies[node].next = copies[node.next]
        copies[node].random = copies[node.random]
    head = copies[originals[0]] if originals else None
    cloned = []
    while head:
        cloned.append(head)
        head = head.next
    positions = {node: index for index, node in enumerate(cloned)}
    print(len(cloned))
    print(*(node.val for node in cloned))
    print(*(positions[node.random] if node.random else -1 for node in cloned))
''', '第一遍为每个原结点新建副本，哈希表记录“原对象→新对象”；第二遍用该表连接 next 和 random。这样即使值相同也不会混淆身份。时间 O(n)，辅助空间 O(n)。输入输出必然呈现相同结构，但参考代码完成了真正深拷贝；想验证独立性还应在函数级测试中修改原链表并检查副本。')

_add(148, '排序链表', 'sort-list', 'Medium', '链表',
     '将单链表按结点值升序排序。建议使用适合链表的归并排序，训练不依赖数组下标的排序方法。',
     LIST_INPUT, LIST_OUTPUT, ['0 ≤ n ≤ 3000', '-10000 ≤ 结点值 ≤ 10000'],
     [(_list([4,2,1,3]), '1 2 3 4\n'), (_list([]), '\n'), (_list([1]), '1\n'),
      (_list([-1,5,3,4,0]), '-1 0 3 4 5\n'), (_list([2,2,1,2]), '1 2 2 2\n')], '''
    def merge(a, b):
        dummy = tail = Node()
        while a and b:
            if a.val <= b.val:
                tail.next, a = a, a.next
            else:
                tail.next, b = b, b.next
            tail = tail.next
        tail.next = a if a else b
        return dummy.next
    def sort(head):
        if not head or not head.next:
            return head
        slow, fast = head, head.next
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
        right = slow.next
        slow.next = None
        return merge(sort(head), sort(right))
    emit(sort(read_list()))
''', '快慢指针把链表断成两半，递归排序后用双指针合并。时间 O(n log n)，递归栈 O(log n)。若要 O(1) 算法辅助空间，可改用自底向上的迭代归并，每轮合并长度为 1、2、4… 的相邻段。')

_add(23, '合并 K 个升序链表', 'merge-k-sorted-lists', 'Hard', '链表',
     '给定 k 条非递减链表，合并为一条非递减链表，保留所有重复值。',
     '第一行 k；之后每条链表占两行，第一行长度 n，第二行 n 个值（空表也保留空行）。',
     LIST_OUTPUT, ['0 ≤ k ≤ 100', '所有链表结点总数 ≤ 3000', '每条链表非递减'],
     [('3\n'+_list([1,4,5])+_list([1,3,4])+_list([2,6]), '1 1 2 3 4 4 5 6\n'),
      ('0\n', '\n'), ('2\n'+_list([])+_list([]), '\n'),
      ('1\n'+_list([-2,0,7]), '-2 0 7\n'),
      ('3\n'+_list([1,1])+_list([])+_list([1]), '1 1 1\n')], '''
    k = int(input())
    heap = []
    for index in range(k):
        head = read_list()
        if head:
            heapq.heappush(heap, (head.val, index, head))
    dummy = tail = Node()
    while heap:
        value, index, node = heapq.heappop(heap)
        following = node.next
        tail.next = node
        tail = node
        if following:
            heapq.heappush(heap, (following.val, index, following))
    if tail is not dummy:
        tail.next = None
    emit(dummy.next)
''', '最小堆保存每条非空链表当前的头结点。弹出全局最小值后，加入该结点的后继。堆中附带链表编号，避免相同值时比较 Node 对象。总长度 N，时间 O(N log(max(2,k)))，辅助空间 O(k)。')

_add(146, 'LRU 缓存', 'lru-cache', 'Medium', '链表',
     '实现容量为 capacity 的最近最少使用缓存。GET key：存在则返回值并更新为最近使用，否则返回 -1；PUT key value：新增或更新并标记最近使用，超容量时删除最久未使用项。',
     '第一行 capacity q；之后 q 行操作，每行是 GET key 或 PUT key value。',
     '每个 GET 操作输出一行返回值；PUT 不输出。',
     ['1 ≤ capacity ≤ 1000', '1 ≤ q ≤ 5000', '0 ≤ key,value ≤ 100000'],
     [('2 9\nPUT 1 1\nPUT 2 2\nGET 1\nPUT 3 3\nGET 2\nPUT 4 4\nGET 1\nGET 3\nGET 4\n','1\n-1\n-1\n3\n4\n'),
      ('1 5\nGET 8\nPUT 8 3\nPUT 8 5\nGET 8\nGET 9\n','-1\n5\n-1\n'),
      ('1 4\nPUT 1 7\nPUT 2 8\nGET 1\nGET 2\n','-1\n8\n'),
      ('2 6\nPUT 1 1\nPUT 2 2\nPUT 1 9\nPUT 3 3\nGET 1\nGET 2\n','9\n-1\n'),
      ('3 3\nGET 1\nGET 2\nGET 3\n','-1\n-1\n-1\n')], '''
    class Entry:
        def __init__(self, key=0, value=0):
            self.key, self.value = key, value
            self.previous = self.next = None
    capacity, q = map(int, input().split())
    cache = {}
    first, last = Entry(), Entry()
    first.next, last.previous = last, first
    def remove(node):
        node.previous.next = node.next
        node.next.previous = node.previous
    def append(node):
        node.previous, node.next = last.previous, last
        last.previous.next = node
        last.previous = node
    for _ in range(q):
        parts = input().split()
        key = int(parts[1])
        node = cache.get(key)
        if parts[0] == 'GET':
            if node is None:
                print(-1)
            else:
                remove(node)
                append(node)
                print(node.value)
        else:
            value = int(parts[2])
            if node:
                node.value = value
                remove(node)
            else:
                node = Entry(key, value)
                cache[key] = node
            append(node)
            if len(cache) > capacity:
                oldest = first.next
                remove(oldest)
                del cache[oldest.key]
''', '哈希表按 key 查结点，双向链表维护从最旧到最新的顺序。成功访问或写入就把结点移到尾部，超容量删除头部真实结点。每次操作平均 O(1)，空间 O(capacity)。')


_add(94, '二叉树的中序遍历', 'binary-tree-inorder-traversal', 'Easy', '二叉树',
     '按左子树、根、右子树的顺序访问二叉树，输出访问到的值。', TREE_INPUT,
     '输出中序遍历的值，以空格分隔；空树输出空行。', ['0 ≤ 结点数 ≤ 3000'],
     [(_tree('1 null 2 3'), '1 3 2\n'), (_tree('null'), '\n'), (_tree('8'), '8\n'),
      (_tree('2 1 3'), '1 2 3\n'), (_tree('3 2 null 1'), '1 2 3\n')], '''
    root = read_tree()
    stack, answer = [], []
    while root or stack:
        while root:
            stack.append(root)
            root = root.left
        root = stack.pop()
        answer.append(root.val)
        root = root.right
    print(*answer)
''', '栈保存尚未访问根结点的祖先，不断向左走；无法再向左时弹出访问，然后转向右子树。时间 O(n)，栈空间 O(h)，h 为树高，不计输出序列。', header=TREE)

_add(104, '二叉树的最大深度', 'maximum-depth-of-binary-tree', 'Easy', '二叉树',
     '深度是从根到最远叶子经过的结点数。求给定树的最大深度，空树深度为 0。', TREE_INPUT,
     '输出一个整数，表示最大深度。', ['0 ≤ 结点数 ≤ 3000'],
     [(_tree('3 9 20 null null 15 7'), '3\n'), (_tree('null'), '0\n'), (_tree('1'), '1\n'),
      (_tree('1 null 2 null 3 null 4'), '4\n'), (_tree('1 2 3 4 5 6 7'), '3\n')], '''
    root = read_tree()
    def depth(node):
        if node is None:
            return 0
        return 1 + max(depth(node.left), depth(node.right))
    print(depth(root))
''', '空结点返回 0，非空结点的深度等于两侧最大深度加 1。时间 O(n)，递归栈 O(h)。', header=TREE)

_add(226, '翻转二叉树', 'invert-binary-tree', 'Easy', '二叉树',
     '交换树中每个结点的左右孩子，输出翻转后的树。', TREE_INPUT, TREE_OUTPUT,
     ['0 ≤ 结点数 ≤ 3000'],
     [(_tree('4 2 7 1 3 6 9'), '4 7 2 9 6 3 1\n'), (_tree('null'), 'null\n'),
      (_tree('1'), '1\n'), (_tree('1 2 null 3'), '1 null 2 null 3\n'),
      (_tree('1 2 3 null 4'), '1 3 2 null null 4\n')], '''
    root = read_tree()
    def invert(node):
        if node:
            node.left, node.right = invert(node.right), invert(node.left)
        return node
    emit_tree(invert(root))
''', '递归翻转两棵子树，并交换左右孩子。时间 O(n)，递归栈 O(h)。判题接受等价的末尾 null 表示。', header=TREE)
CHECKERS[226] = _tree_tokens_match

_add(101, '对称二叉树', 'symmetric-tree', 'Easy', '二叉树',
     '判断二叉树沿根结点的竖直轴是否镜像对称。镜像要求值与空孩子的位置都对应。空树对称。',
     TREE_INPUT, '对称输出 true，否则输出 false。', ['0 ≤ 结点数 ≤ 3000'],
     [(_tree('1 2 2 3 4 4 3'), 'true\n'), (_tree('1 2 2 null 3 null 3'), 'false\n'),
      (_tree('null'), 'true\n'), (_tree('1'), 'true\n'), (_tree('1 2 3'), 'false\n'),
      (_tree('1 2 2 null 3 3 null'), 'true\n')], '''
    root = read_tree()
    def mirror(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)
    print('true' if root is None or mirror(root.left, root.right) else 'false')
''', '同时比较一对镜像结点：值相同，且外侧子树互为镜像、内侧子树互为镜像。空结点必须成对出现。时间 O(n)，递归栈 O(h)。', header=TREE)

_add(543, '二叉树的直径', 'diameter-of-binary-tree', 'Easy', '二叉树',
     '树中任意两个结点之间最长简单路径的边数称为直径，路径不一定经过根。空树和单结点树的直径均为 0。',
     TREE_INPUT, '输出直径（边数）。', ['0 ≤ 结点数 ≤ 3000'],
     [(_tree('1 2 3 4 5'), '3\n'), (_tree('null'), '0\n'), (_tree('1'), '0\n'),
      (_tree('1 null 2 null 3 null 4'), '3\n'), (_tree('1 2 3 4 5 6 7'), '4\n')], '''
    root = read_tree()
    answer = 0
    def depth(node):
        global answer
        if node is None:
            return 0
        left, right = depth(node.left), depth(node.right)
        answer = max(answer, left + right)
        return max(left, right) + 1
    depth(root)
    print(answer)
''', '递归返回以结点数计的子树深度。通过当前结点的最长路径边数为 left_depth+right_depth，遍历所有结点取最大。时间 O(n)，递归栈 O(h)。', header=TREE)

_add(102, '二叉树的层序遍历', 'binary-tree-level-order-traversal', 'Medium', '二叉树',
     '从根开始逐层访问二叉树，每层按从左到右的顺序输出。', TREE_INPUT,
     '第一行输出层数 L；接下来 L 行，每行先输出本层结点数，再输出本层的值。空树只输出 0。',
     ['0 ≤ 结点数 ≤ 3000'],
     [(_tree('3 9 20 null null 15 7'), '3\n1 3\n2 9 20\n2 15 7\n'),
      (_tree('null'), '0\n'), (_tree('8'), '1\n1 8\n'),
      (_tree('1 null 2 null 3'), '3\n1 1\n1 2\n1 3\n'),
      (_tree('1 2 3 4 5 6 7'), '3\n1 1\n2 2 3\n4 4 5 6 7\n')], '''
    root = read_tree()
    queue = deque([root]) if root else deque()
    levels = []
    while queue:
        values = []
        for _ in range(len(queue)):
            node = queue.popleft()
            values.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(values)
    print(len(levels))
    for values in levels:
        print(len(values), *values)
''', 'BFS 使用队列。进入每层时固定当前队列长度，只弹出这一批结点并加入其孩子。时间 O(n)，队列 O(w)，保存输出层次 O(n)，w 为最大层宽。', header=TREE)


def _balanced_bst_checker(stdin, actual, expected):
    """Accept every balanced strict BST containing exactly the input values."""
    try:
        incoming = stdin.split()
        n = int(incoming[0])
        values = list(map(int, incoming[1:]))
        tokens = actual.split()
        if n != len(values) or not tokens or len(tokens) > 2 * n + 10:
            return False
        if tokens[0] == 'null':
            return n == 0 and all(token == 'null' for token in tokens)
        if n == 0:
            return False
        # Node records are [value, left_index, right_index].
        nodes = [[int(tokens[0]), None, None]]
        queue = deque([0])
        cursor = 1
        while queue and cursor < len(tokens):
            index = queue.popleft()
            for side in (1, 2):
                if cursor >= len(tokens):
                    break
                token = tokens[cursor]
                cursor += 1
                if token != 'null':
                    nodes[index][side] = len(nodes)
                    queue.append(len(nodes))
                    nodes.append([int(token), None, None])
        if any(token != 'null' for token in tokens[cursor:]) or len(nodes) != n:
            return False
        # Iterative inorder simultaneously verifies strict BST and exact content.
        order, stack, current = [], [], 0
        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = nodes[current][1]
            current = stack.pop()
            order.append(nodes[current][0])
            current = nodes[current][2]
        if order != values:
            return False
        heights = [0] * n
        for index in range(n - 1, -1, -1):
            _, left, right = nodes[index]
            a = heights[left] if left is not None else 0
            b = heights[right] if right is not None else 0
            if abs(a - b) > 1:
                return False
            heights[index] = max(a, b) + 1
        return True
    except (ValueError, IndexError, TypeError):
        return False


_add(108, '将有序数组转换为二叉搜索树', 'convert-sorted-array-to-binary-search-tree', 'Easy', '二叉树',
     '将严格递增数组构造成高度平衡的二叉搜索树。高度平衡要求每个结点的左右子树高度差不超过 1；搜索树要求左侧值严格小于根、右侧值严格大于根。任意满足条件的结果都会通过。',
     '第一行 n；第二行 n 个严格递增的整数，n=0 时第二行为空。', TREE_OUTPUT,
     ['0 ≤ n ≤ 3000', '-100000 ≤ 数组元素 ≤ 100000', '数组严格递增，无重复元素'],
     [(_list([-10,-3,0,5,9]), '0 -3 9 -10 null 5\n'), (_list([]), 'null\n'),
      (_list([1]), '1\n'), (_list([1,2]), '2 1\n'),
      (_list([1,2,3,4,5,6,7]), '4 2 6 1 3 5 7\n')], '''
    n = int(input())
    values = list(map(int, input().split()))
    def build(left, right):
        if left >= right:
            return None
        middle = (left + right) // 2
        return Node(values[middle], build(left, middle), build(middle + 1, right))
    emit_tree(build(0, n))
''', '选择区间中点作为根，递归处理左右半区间；左右长度相差至多 1，所以整棵树高度平衡。时间 O(n)，除输出树外递归栈 O(log n)。特殊判题检查结点值完整、中序顺序正确、每个结点平衡，不限定某一种中点选择。', header=TREE)
CHECKERS[108] = _balanced_bst_checker

_add(98, '验证二叉搜索树', 'validate-binary-search-tree', 'Medium', '二叉树',
     '判断每个结点是否满足：左子树所有值严格小于该结点，右子树所有值严格大于该结点。值相等不合法，空树合法。',
     TREE_INPUT, '合法输出 true，否则输出 false。', ['0 ≤ 结点数 ≤ 3000', '-10^9 ≤ 结点值 ≤ 10^9'],
     [(_tree('2 1 3'), 'true\n'), (_tree('5 1 4 null null 3 6'), 'false\n'),
      (_tree('null'), 'true\n'), (_tree('2 2 3'), 'false\n'),
      (_tree('5 4 6 null null 3 7'), 'false\n'), (_tree('0 -1 1'), 'true\n')], '''
    root = read_tree()
    def valid(node, lower, upper):
        if node is None:
            return True
        if not lower < node.val < upper:
            return False
        return valid(node.left, lower, node.val) and valid(node.right, node.val, upper)
    print('true' if valid(root, float('-inf'), float('inf')) else 'false')
''', '递归传递所有祖先共同决定的开区间。向左收紧上界、向右收紧下界，因此能发现只比较父子结点时漏掉的违规值。时间 O(n)，递归栈 O(h)。', header=TREE)

_add(230, '二叉搜索树中第 K 小的元素', 'kth-smallest-element-in-a-bst', 'Medium', '二叉树',
     '给定无重复值的合法二叉搜索树，找到第 k 小的结点值，k 从 1 开始。',
     TREE_INPUT+'第三行是 k。', '输出第 k 小的值。',
     ['1 ≤ 结点数 ≤ 3000', '1 ≤ k ≤ 结点数', '输入保证为严格二叉搜索树'],
     [(_tree('3 1 4 null 2')+'1\n','1\n'), (_tree('5 3 6 2 4 null null 1')+'3\n','3\n'),
      (_tree('9')+'1\n','9\n'), (_tree('2 1 3')+'3\n','3\n'),
      (_tree('0 -3 5 null -1 2 8')+'4\n','2\n')], '''
    root = read_tree()
    k = int(input())
    stack = []
    while root or stack:
        while root:
            stack.append(root)
            root = root.left
        root = stack.pop()
        k -= 1
        if k == 0:
            print(root.val)
            break
        root = root.right
''', '搜索树中序遍历严格递增，访问到第 k 个结点即可停止。时间 O(h+k)，最坏 O(n)，辅助栈 O(h)。', header=TREE)

_add(199, '二叉树的右视图', 'binary-tree-right-side-view', 'Medium', '二叉树',
     '从树的右侧观察，每层只能看到最右边的非空结点。按从上到下的顺序输出这些值。',
     TREE_INPUT, '输出右视图的值，以空格分隔；空树输出空行。', ['0 ≤ 结点数 ≤ 3000'],
     [(_tree('1 2 3 null 5 null 4'), '1 3 4\n'), (_tree('null'), '\n'),
      (_tree('1'), '1\n'), (_tree('1 2 null 3'), '1 2 3\n'),
      (_tree('1 2 3 4 null null null 5'), '1 3 4 5\n')], '''
    root = read_tree()
    queue = deque([root]) if root else deque()
    answer = []
    while queue:
        size = len(queue)
        for i in range(size):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
            if i == size - 1:
                answer.append(node.val)
    print(*answer)
''', '逐层 BFS，按左到右入队，每层最后出队的结点就是可见结点。时间 O(n)，队列空间 O(w)，输出 O(h)。不能只沿右孩子走，因为某层右侧可能由左子树提供。', header=TREE)

_add(114, '二叉树展开为链表', 'flatten-binary-tree-to-linked-list', 'Medium', '二叉树',
     '原地把二叉树展开成仅用 right 指针连接的链。展开后的顺序应等于原树的前序遍历，所有 left 指针为空。stdio 判题仅能检查输出值顺序，不能证明原地修改或所有 left 已清空；参考解法实际修改树指针。',
     TREE_INPUT, '沿展开后的 right 链输出所有值，以空格分隔；空树输出空行。', ['0 ≤ 结点数 ≤ 3000'],
     [(_tree('1 2 5 3 4 null 6'), '1 2 3 4 5 6\n'), (_tree('null'), '\n'),
      (_tree('7'), '7\n'), (_tree('1 2 null 3'), '1 2 3\n'),
      (_tree('1 null 2 null 3'), '1 2 3\n')], '''
    root = read_tree()
    current = root
    while current:
        if current.left:
            previous = current.left
            while previous.right:
                previous = previous.right
            previous.right = current.right
            current.right = current.left
            current.left = None
        current = current.right
    answer = []
    while root:
        answer.append(root.val)
        root = root.right
    print(*answer)
''', '有左子树时，找到左子树最右结点，把原右子树接到该结点后面，再把左子树移到右侧并清空 left。随后沿 right 继续。寻找前驱访问的原右边总计 O(n)，总时间 O(n)，修改算法额外空间 O(1)，不计输出数组。', header=TREE)

_add(105, '从前序与中序遍历序列构造二叉树', 'construct-binary-tree-from-preorder-and-inorder-traversal', 'Medium', '二叉树',
     '给出同一棵树的前序和中序遍历，所有值互不重复。重建这棵唯一确定的二叉树。',
     '第一行 n；第二行 n 个前序遍历值；第三行 n 个中序遍历值。n=0 时后两行为空。', TREE_OUTPUT,
     ['0 ≤ n ≤ 3000', '遍历保证合法，值互不重复'],
     [('5\n3 9 20 15 7\n9 3 15 20 7\n','3 9 20 null null 15 7\n'),
      ('0\n\n\n','null\n'), ('1\n-1\n-1\n','-1\n'),
      ('3\n1 2 3\n3 2 1\n','1 2 null 3\n'),
      ('3\n1 2 3\n1 2 3\n','1 null 2 null 3\n')], '''
    n = int(input())
    preorder = list(map(int, input().split()))
    inorder = list(map(int, input().split()))
    positions = {value: index for index, value in enumerate(inorder)}
    cursor = 0
    def build(left, right):
        global cursor
        if left >= right:
            return None
        value = preorder[cursor]
        cursor += 1
        middle = positions[value]
        node = Node(value)
        node.left = build(left, middle)
        node.right = build(middle + 1, right)
        return node
    emit_tree(build(0, n))
''', '前序下一个未使用元素是当前根，在中序中的位置划分左右子树。哈希表使定位为 O(1)，递归用区间下标避免切片。时间 O(n)，哈希表 O(n)、递归栈 O(h)。', header=TREE)
CHECKERS[105] = _tree_tokens_match

_add(437, '路径总和 III', 'path-sum-iii', 'Medium', '二叉树',
     '统计和为 target 的非空向下路径条数。路径可从任意结点开始，在任意后代结束，但每一步必须从父结点走向孩子。',
     TREE_INPUT+'第三行是 target。', '输出符合条件的路径条数。',
     ['0 ≤ 结点数 ≤ 3000', '-10^6 ≤ 结点值,target ≤ 10^6'],
     [(_tree('10 5 -3 3 2 null 11 3 -2 null 1')+'8\n','3\n'),
      (_tree('null')+'0\n','0\n'), (_tree('0')+'0\n','1\n'),
      (_tree('0 0 0')+'0\n','5\n'), (_tree('1 -1 1')+'0\n','1\n'),
      (_tree('1 null 1 null 1')+'2\n','2\n')], '''
    root = read_tree()
    target = int(input())
    counts = {0: 1}
    def dfs(node, current):
        if node is None:
            return 0
        current += node.val
        answer = counts.get(current - target, 0)
        counts[current] = counts.get(current, 0) + 1
        answer += dfs(node.left, current) + dfs(node.right, current)
        counts[current] -= 1
        if counts[current] == 0:
            del counts[current]
        return answer
    print(dfs(root, 0))
''', '哈希表只保存当前祖先路径上各前缀和的出现次数。当前前缀和为 s 时，之前出现过的 s-target 都对应一条以当前结点结束的合法路径。递归返回时撤销当前前缀，防止混入兄弟分支。时间平均 O(n)，辅助空间 O(h)。', header=TREE)

_add(236, '二叉树的最近公共祖先', 'lowest-common-ancestor-of-a-binary-tree', 'Medium', '二叉树',
     '结点值互不重复，指定值为 p、q 的两个结点。求它们距离根最远的公共祖先；一个结点也可以是自己的祖先。',
     TREE_INPUT+'第三行是 p q，保证两个值都存在于树中，允许 p=q。',
     '输出最近公共祖先的结点值。', ['1 ≤ 结点数 ≤ 3000', '结点值互不重复'],
     [(_tree('3 5 1 6 2 0 8 null null 7 4')+'5 1\n','3\n'),
      (_tree('3 5 1 6 2 0 8 null null 7 4')+'5 4\n','5\n'),
      (_tree('1')+'1 1\n','1\n'), (_tree('1 2 3')+'2 3\n','1\n'),
      (_tree('1 2 null 3')+'2 3\n','2\n')], '''
    root = read_tree()
    p, q = map(int, input().split())
    def lca(node):
        if node is None or node.val == p or node.val == q:
            return node
        left, right = lca(node.left), lca(node.right)
        if left and right:
            return node
        return left if left else right
    print(lca(root).val)
''', '遇到目标结点或空结点直接返回。如果左右子树都返回非空，当前结点就是分叉处；只有一侧非空则把该侧结果向上传。目标之一是另一个的祖先时会返回该祖先。时间 O(n)，递归栈 O(h)。', header=TREE)

_add(124, '二叉树中的最大路径和', 'binary-tree-maximum-path-sum', 'Hard', '二叉树',
     '一条路径由相邻结点组成且不能重复经过同一结点，可以从任意结点开始、在任意结点结束。求非空路径上的最大结点值之和。',
     TREE_INPUT, '输出最大路径和。', ['1 ≤ 结点数 ≤ 3000', '-1000 ≤ 结点值 ≤ 1000'],
     [(_tree('1 2 3'), '6\n'), (_tree('-10 9 20 null null 15 7'), '42\n'),
      (_tree('-3'), '-3\n'), (_tree('-2 -1 -3'), '-1\n'),
      (_tree('2 -1'), '2\n'), (_tree('1 -2 3 4 5 -6 2'), '9\n')], '''
    root = read_tree()
    answer = float('-inf')
    def gain(node):
        global answer
        if node is None:
            return 0
        left = max(0, gain(node.left))
        right = max(0, gain(node.right))
        answer = max(answer, node.val + left + right)
        return node.val + max(left, right)
    gain(root)
    print(answer)
''', '递归返回能够继续连接父结点的单侧最大贡献，负贡献舍弃为 0。以当前结点为转折点的完整路径可同时使用两侧，更新全局答案；返回父结点时只能选择一侧。全局答案初始为负无穷以处理全负树。时间 O(n)，递归栈 O(h)。', header=TREE)
