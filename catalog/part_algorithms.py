"""Original ACM adaptations: graphs, search, stacks, heaps, greedy and DP."""
from collections import Counter
from textwrap import dedent

PROBLEMS = []
CHECKERS = {}

STARTER = '''import sys

input = sys.stdin.readline


def solve():
    # 按题目输入格式读取数据，计算答案并打印。
    pass


if __name__ == "__main__":
    solve()
'''


def _add(pid, title, slug, difficulty, category, description, input_format,
         output_format, constraints, cases, body, explanation, compare="tokens"):
    solution = ('import sys\nfrom collections import deque, Counter\n'
                'from bisect import bisect_left\nimport heapq\n\n'
                'input = sys.stdin.readline\n\n\ndef solve():\n')
    solution += ''.join('    ' + line + '\n' if line else '\n'
                        for line in dedent(body).strip().splitlines())
    solution += '\n\nif __name__ == "__main__":\n    solve()\n'
    tests = [{"input": a, "output": b} for a, b in cases]
    PROBLEMS.append(dict(id=pid, title=title, slug=slug, difficulty=difficulty,
                         category=category, description=description,
                         input_format=input_format, output_format=output_format,
                         constraints=constraints, tests=tests,
                         examples=[dict(test, explanation="按所述规则可得到以上结果。")
                                   for test in tests[:2]],
                         starter=STARTER, solution=solution,
                         explanation=explanation, compare=compare))


def _collection_checker(sort_items=False):
    """Compare complete enumerations, allowing either order of solution lines."""
    def parse(text):
        lines = text.strip().splitlines()
        if not lines:
            raise ValueError("missing count")
        count = int(lines[0].strip())
        if count < 0 or len(lines) != count + 1:
            raise ValueError("incorrect line count")
        records = []
        for line in lines[1:]:
            parts = line.split()
            if not parts:
                raise ValueError("use - for an empty answer")
            records.append(tuple(sorted(parts) if sort_items else parts))
        return Counter(records)

    def check(stdin, actual, expected):
        try:
            return parse(actual) == parse(expected)
        except (ValueError, TypeError):
            return False
    return check


def _palindrome_checker(stdin, actual, expected):
    s = stdin.strip()
    answer = actual.strip()
    return (len(answer) == len(expected.strip()) and answer in s
            and answer == answer[::-1])


def _top_k_checker(stdin, actual, expected):
    try:
        data = list(map(int, stdin.split()))
        n, k = data[:2]
        freq = Counter(data[2:2 + n])
        answer = list(map(int, actual.split()))
        threshold = sorted(freq.values(), reverse=True)[k - 1]
        return (len(answer) == k and len(set(answer)) == k
                and all(x in freq and freq[x] >= threshold for x in answer)
                and all(x in answer for x, f in freq.items() if f > threshold))
    except (ValueError, IndexError, TypeError):
        return False


_add(200, "岛屿数量", "number-of-islands", "Medium", "图论",
     "一张矩形地图以 1 表示陆地、0 表示水域。上下左右相邻的陆地属于同一座岛，斜向接触不连通。计算岛屿总数。",
     "第一行两个整数 m n。随后 m 行，每行是长度为 n 的 01 字符串，字符之间没有空格。",
     "输出岛屿数量。", ["1 ≤ m,n ≤ 200"],
     [("4 5\n11110\n11010\n11000\n00000\n", "1\n"),
      ("4 5\n11000\n11000\n00100\n00011\n", "3\n"),
      ("1 1\n0\n", "0\n"), ("1 1\n1\n", "1\n"),
      ("3 3\n101\n010\n101\n", "5\n"),
      ("1 6\n110101\n", "3\n")], '''
    m, n = map(int, input().split())
    grid = [list(input().strip()) for _ in range(m)]
    answer = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] != '1':
                continue
            answer += 1
            grid[r][c] = '0'
            stack = [(r, c)]
            while stack:
                x, y = stack.pop()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == '1':
                        grid[nx][ny] = '0'
                        stack.append((nx, ny))
    print(answer)
''', "遍历地图；遇到尚未访问的陆地，答案加一并用栈淹没该连通块。入栈时立即标记，避免重复。时间 O(mn)，辅助空间 O(mn)。")

_add(994, "腐烂的橘子", "rotting-oranges", "Medium", "图论",
     "网格中的 0、1、2 分别表示空格、新鲜橘子和腐烂橘子。每分钟，所有腐烂橘子同时使上下左右的新鲜橘子腐烂。求不再有新鲜橘子所需的最少分钟数；无法全部腐烂时输出 -1。",
     "第一行 m n，随后 m 行，每行 n 个整数。", "输出最少分钟数或 -1。",
     ["1 ≤ m,n ≤ 100", "网格元素为 0、1 或 2"],
     [("3 3\n2 1 1\n1 1 0\n0 1 1\n", "4\n"),
      ("3 3\n2 1 1\n0 1 1\n1 0 1\n", "-1\n"),
      ("1 2\n0 2\n", "0\n"), ("1 1\n1\n", "-1\n"),
      ("1 5\n2 1 1 1 2\n", "2\n"), ("1 1\n0\n", "0\n")], '''
    m, n = map(int, input().split())
    grid = [list(map(int, input().split())) for _ in range(m)]
    queue = deque()
    fresh = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while fresh and queue:
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1
    print(minutes if fresh == 0 else -1)
''', "把所有初始腐烂橘子放入队列，进行多源 BFS。每处理一层代表经过一分钟，并维护新鲜橘子数。时间 O(mn)，空间 O(mn)。")

_add(207, "课程表", "course-schedule", "Medium", "图论",
     "有 n 门编号为 0 到 n-1 的课程。依赖 a b 表示修读 a 前必须完成 b。判断是否存在一个顺序可以修完全部课程。",
     "第一行 n m，表示课程数和依赖数。随后 m 行，每行 a b。",
     "可以完成时输出 true，否则输出 false。", ["1 ≤ n ≤ 2000", "0 ≤ m ≤ 5000", "依赖可包含自环，无重复依赖"],
     [("2 1\n1 0\n", "true\n"), ("2 2\n1 0\n0 1\n", "false\n"),
      ("1 0\n", "true\n"), ("1 1\n0 0\n", "false\n"),
      ("4 4\n1 0\n2 0\n3 1\n3 2\n", "true\n"),
      ("4 2\n1 2\n2 1\n", "false\n")], '''
    n, m = map(int, input().split())
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for _ in range(m):
        a, b = map(int, input().split())
        graph[b].append(a)
        indegree[a] += 1
    queue = deque(i for i in range(n) if indegree[i] == 0)
    finished = 0
    while queue:
        course = queue.popleft()
        finished += 1
        for nxt in graph[course]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    print('true' if finished == n else 'false')
''', "用入度为零的课程开始拓扑排序。删除课程后降低后继入度；最终处理了全部课程就说明无环。时间 O(n+m)，空间 O(n+m)。")

_add(208, "实现 Trie（前缀树）", "implement-trie-prefix-tree", "Medium", "图论",
     "实现一个初始为空的单词集合，支持插入、查询完整单词和查询前缀。重复插入不会改变查询结果。",
     "第一行操作数 q。随后 q 行，格式为 insert word、search word 或 startsWith prefix。所有单词和前缀非空。",
     "每个 search 和 startsWith 操作输出一行 true 或 false；insert 不输出。",
     ["1 ≤ q ≤ 10000", "单词仅含小写英文字母，长度 1 到 100", "至少有一次查询"],
     [("6\ninsert apple\nsearch apple\nsearch app\nstartsWith app\ninsert app\nsearch app\n", "true\nfalse\ntrue\ntrue\n"),
      ("2\nsearch a\nstartsWith a\n", "false\nfalse\n"),
      ("5\ninsert a\ninsert a\nsearch a\nsearch aa\nstartsWith a\n", "true\nfalse\ntrue\n"),
      ("5\ninsert cat\ninsert car\nstartsWith ca\nsearch ca\nsearch car\n", "true\nfalse\ntrue\n"),
      ("4\ninsert hello\nstartsWith he\nstartsWith hi\nsearch hello\n", "true\nfalse\ntrue\n")], '''
    q = int(input())
    root = {}
    output = []
    for _ in range(q):
        operation, word = input().split()
        node = root
        if operation == 'insert':
            for char in word:
                node = node.setdefault(char, {})
            node['#'] = True
            continue
        for char in word:
            if char not in node:
                node = None
                break
            node = node[char]
        found = node is not None and (operation == 'startsWith' or '#' in node)
        output.append('true' if found else 'false')
    print('\\n'.join(output))
''', "每个节点用字典保存字符到子节点的映射，用 # 标记完整单词结尾。单次操作时间 O(L)，总空间 O(S)，S 为插入单词长度总和。")

_add(46, "全排列", "permutations", "Medium", "回溯",
     "给出 n 个互不相同的整数，列出使用每个整数恰好一次的所有排列。各排列的输出顺序不限。",
     "第一行 n，第二行 n 个互不相同的整数。",
     "第一行输出排列数。随后每行一个排列，含 n 个整数。各行顺序不限，不可遗漏或重复。",
     ["1 ≤ n ≤ 7", "-100 ≤ 整数 ≤ 100"],
     [("3\n1 2 3\n", "6\n1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1\n"),
      ("2\n0 1\n", "2\n0 1\n1 0\n"), ("1\n5\n", "1\n5\n"),
      ("2\n-1 2\n", "2\n-1 2\n2 -1\n"),
      ("3\n3 0 -2\n", "6\n3 0 -2\n3 -2 0\n0 3 -2\n0 -2 3\n-2 3 0\n-2 0 3\n")], '''
    n = int(input())
    nums = list(map(int, input().split()))
    used = [False] * n
    path, answers = [], []
    def dfs():
        if len(path) == n:
            answers.append(' '.join(map(str, path)))
            return
        for i, value in enumerate(nums):
            if not used[i]:
                used[i] = True
                path.append(value)
                dfs()
                path.pop()
                used[i] = False
    dfs()
    print(len(answers))
    print('\\n'.join(answers))
''', "路径中每一位选择一个未使用的数；递归返回后恢复 used 和 path。时间 O(n·n!)，除保存输出外辅助空间 O(n)。")
CHECKERS[46] = _collection_checker()

_add(78, "子集", "subsets", "Medium", "回溯",
     "给出 n 个互不相同的整数，输出全部子集，包括空集。子集内元素顺序及各子集顺序都不限。",
     "第一行 n；第二行 n 个整数。n 为 0 时第二行可以为空。",
     "第一行子集数。随后每行一个子集，元素以空格分隔；空集单独输出 -。不可遗漏或重复。",
     ["0 ≤ n ≤ 12", "整数互不相同，范围 -100 到 100"],
     [("3\n1 2 3\n", "8\n-\n1\n2\n3\n1 2\n1 3\n2 3\n1 2 3\n"),
      ("1\n0\n", "2\n-\n0\n"), ("0\n\n", "1\n-\n"),
      ("2\n-1 2\n", "4\n-\n-1\n2\n-1 2\n"),
      ("2\n8 5\n", "4\n-\n8\n5\n8 5\n")], '''
    n = int(input())
    nums = list(map(int, input().split()))
    path, answers = [], []
    def dfs(start):
        answers.append(' '.join(map(str, path)) if path else '-')
        for i in range(start, n):
            path.append(nums[i])
            dfs(i + 1)
            path.pop()
    dfs(0)
    print(len(answers))
    print('\\n'.join(answers))
''', "每个递归节点对应一个子集，只向后选择元素从而避免重复。时间 O(n·2^n)，除保存输出外辅助空间 O(n)。")
CHECKERS[78] = _collection_checker(True)

_add(17, "电话号码的字母组合", "letter-combinations-of-a-phone-number", "Medium", "回溯",
     "按电话按键映射 2→abc、3→def、4→ghi、5→jkl、6→mno、7→pqrs、8→tuv、9→wxyz，为数字串的每一位选择一个字母，输出全部组合。",
     "一行由 2 到 9 组成的非空数字串。",
     "第一行组合数，随后每行一个组合，各行顺序不限。",
     ["数字串长度 1 到 4"],
     [("23\n", "9\nad\nae\naf\nbd\nbe\nbf\ncd\nce\ncf\n"),
      ("2\n", "3\na\nb\nc\n"), ("7\n", "4\np\nq\nr\ns\n"),
      ("9\n", "4\nw\nx\ny\nz\n"),
      ("22\n", "9\naa\nab\nac\nba\nbb\nbc\nca\ncb\ncc\n")], '''
    digits = input().strip()
    mapping = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
               '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}
    answers = ['']
    for digit in digits:
        answers = [prefix + char for prefix in answers for char in mapping[digit]]
    print(len(answers))
    print('\\n'.join(answers))
''', "逐位扩展已有前缀，每次添加当前按键的所有候选字母。设长度为 L，最多有 4^L 个结果，时间和保存输出的空间均为 O(L·4^L)。")
CHECKERS[17] = _collection_checker()

_add(39, "组合总和", "combination-sum", "Medium", "回溯",
     "给定若干互不相同的正整数和目标值 target，每个整数可以选任意次。输出和为 target 的全部不同组合；仅选择次数不同才视为不同组合。",
     "第一行 n target，第二行 n 个互不相同的正整数。",
     "第一行组合数。随后每行一个组合，元素以空格分隔。组合内元素顺序和各行顺序不限；没有答案时只输出 0。",
     ["1 ≤ n ≤ 15", "1 ≤ target ≤ 30", "2 ≤ 候选数 ≤ 40"],
     [("4 7\n2 3 6 7\n", "2\n2 2 3\n7\n"),
      ("3 8\n2 3 5\n", "3\n2 2 2 2\n2 3 3\n3 5\n"),
      ("1 1\n2\n", "0\n"), ("1 6\n3\n", "1\n3 3\n"),
      ("3 9\n9 4 5\n", "2\n9\n4 5\n")], '''
    n, target = map(int, input().split())
    nums = sorted(map(int, input().split()))
    path, answers = [], []
    def dfs(start, remain):
        if remain == 0:
            answers.append(' '.join(map(str, path)))
            return
        for i in range(start, n):
            if nums[i] > remain:
                break
            path.append(nums[i])
            dfs(i, remain - nums[i])
            path.pop()
    dfs(0, target)
    print(len(answers))
    if answers:
        print('\\n'.join(answers))
''', "先排序，再以不减下标选择候选数；递归仍传 i 允许重复使用。超过剩余目标即可剪枝。设最大深度 D=target/min(nums)，保守时间上界 O(n^(D+1)·D)，除输出外空间 O(n+D)。")
CHECKERS[39] = _collection_checker(True)

_add(22, "括号生成", "generate-parentheses", "Medium", "回溯",
     "用 n 对圆括号生成全部合法括号串。合法意味着任意前缀的右括号数不超过左括号数，且最终两者相等。",
     "一行整数 n。", "第一行答案数，随后每行一个括号串，顺序不限。",
     ["1 ≤ n ≤ 8"],
     [("3\n", "5\n((()))\n(()())\n(())()\n()(())\n()()()\n"),
      ("1\n", "1\n()\n"), ("2\n", "2\n(())\n()()\n"),
      ("4\n", "14\n(((())))\n((()()))\n((())())\n((()))()\n(()(()))\n(()()())\n(()())()\n(())(())\n(())()()\n()((()))\n()(()())\n()(())()\n()()(())\n()()()()\n"),
      ("5\n", "42\n((((()))))\n(((()())))\n(((())()))\n(((()))())\n(((())))()\n((()(())))\n((()()()))\n((()())())\n((()()))()\n((())(()))\n((())()())\n((())())()\n((()))(())\n((()))()()\n(()((())))\n(()(()()))\n(()(())())\n(()(()))()\n(()()(()))\n(()()()())\n(()()())()\n(()())(())\n(()())()()\n(())((()))\n(())(()())\n(())(())()\n(())()(())\n(())()()()\n()(((())))\n()((()()))\n()((())())\n()((()))()\n()(()(()))\n()(()()())\n()(()())()\n()(())(())\n()(())()()\n()()((()))\n()()(()())\n()()(())()\n()()()(())\n()()()()()\n")], '''
    n = int(input())
    answers = []
    def dfs(path, left, right):
        if len(path) == 2 * n:
            answers.append(path)
            return
        if left < n:
            dfs(path + '(', left + 1, right)
        if right < left:
            dfs(path + ')', left, right + 1)
    dfs('', 0, 0)
    print(len(answers))
    print('\\n'.join(answers))
''', "用已放入的左右括号数量限制分支：左括号未用完可添加，右括号少于左括号才可添加。若 C_n 为第 n 个卡特兰数，时间 O(n·C_n)；本实现递归字符串除输出外最多占 O(n²) 空间。")
CHECKERS[22] = _collection_checker()

_add(79, "单词搜索", "word-search", "Medium", "回溯",
     "在字符网格中寻找一个单词。路径每次只能上下左右移动，同一个格子在同一条路径里最多使用一次。判断是否存在这样的路径。",
     "第一行 m n，随后 m 行，每行长度为 n 的字母串；最后一行是待查找的非空单词。",
     "存在时输出 true，否则输出 false。", ["1 ≤ m,n ≤ 6", "1 ≤ 单词长度 ≤ 15", "只含大小写英文字母，区分大小写"],
     [("3 4\nABCE\nSFCS\nADEE\nABCCED\n", "true\n"),
      ("3 4\nABCE\nSFCS\nADEE\nABCB\n", "false\n"),
      ("1 1\na\na\n", "true\n"), ("1 1\na\naa\n", "false\n"),
      ("2 2\nab\ncd\nacdb\n", "true\n"),
      ("2 2\nab\ncd\nad\n", "false\n")], '''
    m, n = map(int, input().split())
    board = [list(input().strip()) for _ in range(m)]
    word = input().strip()
    def dfs(r, c, index):
        if board[r][c] != word[index]:
            return False
        if index == len(word) - 1:
            return True
        char = board[r][c]
        board[r][c] = '#'
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] != '#':
                if dfs(nr, nc, index + 1):
                    board[r][c] = char
                    return True
        board[r][c] = char
        return False
    found = any(dfs(r, c, 0) for r in range(m) for c in range(n))
    print('true' if found else 'false')
''', "从每个格子出发 DFS，临时改写字符防止重复使用，返回时还原。设单词长度 L，时间上界 O(mn·4^L)，除输入网格外辅助空间 O(L)。")

_add(131, "分割回文串", "palindrome-partitioning", "Medium", "回溯",
     "将一个字符串切成一个或多个连续非空片段，要求每个片段都是回文串。输出全部切分方案，片段拼接后必须等于原串。",
     "一行非空小写英文字符串。",
     "第一行方案数。随后每行一个方案，各片段按原串顺序以空格分隔；方案之间的顺序不限。",
     ["1 ≤ 字符串长度 ≤ 15"],
     [("aab\n", "2\na a b\naa b\n"), ("a\n", "1\na\n"),
      ("abc\n", "1\na b c\n"), ("aaa\n", "4\na a a\na aa\naa a\naaa\n"),
      ("abba\n", "3\na b b a\na bb a\nabba\n")], '''
    s = input().strip()
    n = len(s)
    palindrome = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            palindrome[i][j] = s[i] == s[j] and (j - i < 2 or palindrome[i + 1][j - 1])
    path, answers = [], []
    def dfs(start):
        if start == n:
            answers.append(' '.join(path))
            return
        for end in range(start, n):
            if palindrome[start][end]:
                path.append(s[start:end + 1])
                dfs(end + 1)
                path.pop()
    dfs(0)
    print(len(answers))
    print('\\n'.join(answers))
''', "先用区间 DP 预处理所有回文子串，再回溯选择当前片段的右端点。时间 O(n·2^n+n²)，除输出外辅助空间 O(n²)。")
CHECKERS[131] = _collection_checker()

_add(51, "N 皇后", "n-queens", "Hard", "回溯",
     "在 n×n 棋盘放 n 个皇后，使任意两个皇后不在同一行、同一列或同一条对角线上。输出全部方案。用每一行皇后所在的列号表示一个方案，列号从 1 开始。",
     "一行整数 n。",
     "第一行方案数。随后每行 n 个整数，第 i 个整数表示第 i 行的皇后列号。方案顺序不限；无解只输出 0。",
     ["1 ≤ n ≤ 9"],
     [("4\n", "2\n2 4 1 3\n3 1 4 2\n"), ("1\n", "1\n1\n"),
      ("2\n", "0\n"), ("3\n", "0\n"),
      ("5\n", "10\n1 3 5 2 4\n1 4 2 5 3\n2 4 1 3 5\n2 5 3 1 4\n3 1 4 2 5\n3 5 2 4 1\n4 1 3 5 2\n4 2 5 3 1\n5 2 4 1 3\n5 3 1 4 2\n")], '''
    n = int(input())
    columns, diagonal1, diagonal2 = set(), set(), set()
    path, answers = [], []
    def dfs(row):
        if row == n:
            answers.append(' '.join(map(str, path)))
            return
        for col in range(n):
            if col in columns or row - col in diagonal1 or row + col in diagonal2:
                continue
            columns.add(col)
            diagonal1.add(row - col)
            diagonal2.add(row + col)
            path.append(col + 1)
            dfs(row + 1)
            path.pop()
            columns.remove(col)
            diagonal1.remove(row - col)
            diagonal2.remove(row + col)
    dfs(0)
    print(len(answers))
    if answers:
        print('\\n'.join(answers))
''', "逐行放置皇后，用三个集合维护列、行减列、行加列，常数时间判断冲突。本实现每个节点扫描 n 列，保守时间 O(n·n!)；除保存输出外空间 O(n)。")
CHECKERS[51] = _collection_checker()

_add(20, "有效的括号", "valid-parentheses", "Easy", "栈",
     "给定只含 ()[]{} 的字符串，判断括号类型和嵌套顺序是否匹配。空字符串也合法。",
     "一行括号字符串，可以为空行。", "合法输出 true，否则输出 false。",
     ["0 ≤ 字符串长度 ≤ 100000"],
     [("()[]{}\n", "true\n"), ("(]\n", "false\n"), ("([)]\n", "false\n"),
      ("{[]}\n", "true\n"), ("\n", "true\n"), ("((\n", "false\n"), ("}\n", "false\n")], '''
    s = input().strip()
    stack = []
    match = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in '([{':
            stack.append(char)
        elif not stack or stack.pop() != match[char]:
            print('false')
            return
    print('true' if not stack else 'false')
''', "左括号入栈；右括号必须和栈顶类型一致。扫描结束后栈必须为空。时间 O(n)，空间 O(n)。")

_add(155, "最小栈", "min-stack", "Medium", "栈",
     "维护一个支持压栈、弹栈、查询栈顶和查询最小值的栈，要求每种操作均为 O(1) 时间。",
     "第一行 q，随后 q 行操作：push x、pop、top 或 getMin。保证 pop、top、getMin 时栈非空。",
     "每个 top 或 getMin 输出一行整数，其他操作不输出。",
     ["1 ≤ q ≤ 100000", "-10^9 ≤ x ≤ 10^9", "至少有一次查询"],
     [("7\npush -2\npush 0\npush -3\ngetMin\npop\ntop\ngetMin\n", "-3\n0\n-2\n"),
      ("3\npush 5\ntop\ngetMin\n", "5\n5\n"),
      ("6\npush 2\npush 2\npop\ngetMin\ntop\npop\n", "2\n2\n"),
      ("7\npush 9\npush 1\ngetMin\npop\ngetMin\npush 3\ntop\n", "1\n9\n3\n"),
      ("6\npush -1000000000\ngetMin\npop\npush 1000000000\ngetMin\ntop\n", "-1000000000\n1000000000\n1000000000\n")], '''
    q = int(input())
    stack, output = [], []
    for _ in range(q):
        operation = input().split()
        if operation[0] == 'push':
            value = int(operation[1])
            minimum = min(value, stack[-1][1]) if stack else value
            stack.append((value, minimum))
        elif operation[0] == 'pop':
            stack.pop()
        elif operation[0] == 'top':
            output.append(str(stack[-1][0]))
        else:
            output.append(str(stack[-1][1]))
    print('\\n'.join(output))
''', "每个栈元素同时保存自身值和截至这一层的最小值。弹栈后前一层的最小值自然恢复。每次操作 O(1)，空间 O(q)。")

_add(394, "字符串解码", "decode-string", "Medium", "栈",
     "字符串使用 k[片段] 表示将片段重复 k 次，片段内部也可以包含嵌套编码。字母原样保留。将合法编码展开。",
     "一行合法编码，由小写字母、数字和方括号组成；数字只作为重复次数出现。",
     "输出完整解码字符串。", ["1 ≤ 编码长度 ≤ 200", "1 ≤ 重复次数 ≤ 100", "解码后长度不超过 100000"],
     [("3[a]2[bc]\n", "aaabcbc\n"), ("3[a2[c]]\n", "accaccacc\n"),
      ("2[abc]3[cd]ef\n", "abcabccdcdcdef\n"), ("abc\n", "abc\n"),
      ("10[x]\n", "xxxxxxxxxx\n"), ("a2[b3[c]]d\n", "abcccbcccd\n")], '''
    s = input().strip()
    stack = []
    current, number = '', 0
    for char in s:
        if char.isdigit():
            number = number * 10 + int(char)
        elif char == '[':
            stack.append((current, number))
            current, number = '', 0
        elif char == ']':
            prefix, repeat = stack.pop()
            current = prefix + current * repeat
        else:
            current += char
    print(current)
''', "遇到左括号时保存外层字符串和次数；右括号时展开当前层并接回外层。设编码长 n、解码长 L，字符串复制的保守时间上界 O(nL)，空间 O(n+L)。")

_add(739, "每日温度", "daily-temperatures", "Medium", "栈",
     "给定每天的温度，计算每一天至少再等几天才能遇到严格更高的温度。之后没有更高温度则填 0。",
     "第一行 n，第二行 n 个温度整数。", "输出 n 个整数，以空格分隔。",
     ["1 ≤ n ≤ 100000", "-100 ≤ 温度 ≤ 100"],
     [("8\n73 74 75 71 69 72 76 73\n", "1 1 4 2 1 1 0 0\n"),
      ("4\n30 40 50 60\n", "1 1 1 0\n"),
      ("3\n30 30 30\n", "0 0 0\n"), ("1\n5\n", "0\n"),
      ("4\n5 4 3 2\n", "0 0 0 0\n"), ("4\n-2 -3 -2 -1\n", "3 1 1 0\n")], '''
    n = int(input())
    temperatures = list(map(int, input().split()))
    answer = [0] * n
    stack = []
    for i, value in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < value:
            j = stack.pop()
            answer[j] = i - j
        stack.append(i)
    print(*answer)
''', "栈保存尚未找到更高温度的下标，对应温度单调不增。当前温度更高时，依次确定栈顶答案。每个下标进出栈一次，时间 O(n)，空间 O(n)。")

_add(84, "柱状图中最大的矩形", "largest-rectangle-in-histogram", "Hard", "栈",
     "柱状图由 n 根宽为 1、高度非负的相邻柱子组成。求完全位于柱状图内、边与坐标轴平行的矩形的最大面积。",
     "第一行 n，第二行 n 个高度。", "输出最大面积。",
     ["1 ≤ n ≤ 100000", "0 ≤ 高度 ≤ 10000"],
     [("6\n2 1 5 6 2 3\n", "10\n"), ("2\n2 4\n", "4\n"),
      ("1\n0\n", "0\n"), ("4\n3 3 3 3\n", "12\n"),
      ("5\n1 2 3 4 5\n", "9\n"), ("3\n2 0 2\n", "2\n")], '''
    n = int(input())
    heights = list(map(int, input().split())) + [0]
    stack = [-1]
    answer = 0
    for i, height in enumerate(heights):
        while stack[-1] != -1 and heights[stack[-1]] > height:
            h = heights[stack.pop()]
            width = i - stack[-1] - 1
            answer = max(answer, h * width)
        stack.append(i)
    print(answer)
''', "维护高度单调不减的下标栈。遇到更矮柱子时，出栈柱子的右边界已确定，出栈后的栈顶决定左边界；末尾补 0 完成结算。时间 O(n)，空间 O(n)。")

_add(215, "数组中的第 K 个最大元素", "kth-largest-element-in-an-array", "Medium", "堆",
     "求数组按从大到小排序后第 k 个元素，重复值也各占一个位置。",
     "第一行 n k，第二行 n 个整数。", "输出第 k 个最大元素。",
     ["1 ≤ k ≤ n ≤ 100000", "-10^9 ≤ 元素 ≤ 10^9"],
     [("6 2\n3 2 1 5 6 4\n", "5\n"),
      ("9 4\n3 2 3 1 2 4 5 5 6\n", "4\n"),
      ("1 1\n-8\n", "-8\n"), ("4 4\n7 7 7 7\n", "7\n"),
      ("4 3\n-1 -5 -2 -10\n", "-5\n"), ("3 1\n1 9 2\n", "9\n")], '''
    n, k = map(int, input().split())
    nums = list(map(int, input().split()))
    heap = nums[:k]
    heapq.heapify(heap)
    for value in nums[k:]:
        if value > heap[0]:
            heapq.heapreplace(heap, value)
    print(heap[0])
''', "维护容量为 k 的小根堆，堆内始终是已扫描元素中最大的 k 个。堆顶就是答案。时间 O(n log(k+1))，堆空间 O(k)，本实现读取数组占 O(n) 空间。")

_add(347, "前 K 个高频元素", "top-k-frequent-elements", "Medium", "堆",
     "从数组中选出出现频率最高的 k 个不同整数。输出顺序不限；若第 k 名处存在频率并列，可以任选并列元素，但不能遗漏频率更高的元素。",
     "第一行 n k，第二行 n 个整数。", "输出 k 个不同整数，顺序不限。",
     ["1 ≤ n ≤ 100000", "1 ≤ k ≤ 不同整数的数量", "-10^9 ≤ 元素 ≤ 10^9"],
     [("6 2\n1 1 1 2 2 3\n", "1 2\n"), ("1 1\n1\n", "1\n"),
      ("6 2\n4 4 5 5 6 6\n", "4 5\n"),
      ("7 2\n-1 -1 -1 0 0 2 3\n", "-1 0\n"),
      ("4 3\n7 8 9 7\n", "7 8 9\n"),
      ("7 2\n1 1 1 2 2 3 3\n", "1 2\n")], '''
    n, k = map(int, input().split())
    freq = Counter(map(int, input().split()))
    heap = []
    for value, count in freq.items():
        heapq.heappush(heap, (count, value))
        if len(heap) > k:
            heapq.heappop(heap)
    print(*(value for count, value in heap))
''', "先用哈希表计数，再用容量 k 的小根堆维护高频元素。并列时保留任意合法元素即可。设不同元素数为 u，时间 O(n+u log(k+1))，空间 O(u+k)。")
CHECKERS[347] = _top_k_checker

_add(295, "数据流的中位数", "find-median-from-data-stream", "Hard", "堆",
     "维护一个初始为空的数据流，支持添加整数和查询当前中位数。元素个数为偶数时，中位数为排序后中间两个数的平均值。",
     "第一行 q。随后 q 行为 addNum x 或 findMedian。保证每次查询时至少已有一个数。",
     "每次 findMedian 输出一行数值；绝对或相对误差不超过 10^-6 即可。",
     ["1 ≤ q ≤ 100000", "-10^9 ≤ x ≤ 10^9", "至少一次 findMedian"],
     [("5\naddNum 1\naddNum 2\nfindMedian\naddNum 3\nfindMedian\n", "1.5\n2\n"),
      ("2\naddNum -3\nfindMedian\n", "-3\n"),
      ("5\naddNum 4\naddNum 4\nfindMedian\naddNum 4\nfindMedian\n", "4\n4\n"),
      ("5\naddNum -5\naddNum -2\nfindMedian\naddNum 0\nfindMedian\n", "-3.5\n-2\n"),
      ("7\naddNum 10\naddNum 0\naddNum 8\nfindMedian\naddNum 2\nfindMedian\nfindMedian\n", "8\n5\n5\n")], '''
    q = int(input())
    low, high, output = [], [], []
    for _ in range(q):
        operation = input().split()
        if operation[0] == 'addNum':
            value = int(operation[1])
            heapq.heappush(low, -value)
            heapq.heappush(high, -heapq.heappop(low))
            if len(high) > len(low):
                heapq.heappush(low, -heapq.heappop(high))
        else:
            if len(low) > len(high):
                output.append(str(-low[0]))
            else:
                output.append(str((-low[0] + high[0]) / 2))
    print('\\n'.join(output))
''', "用大根堆 low 存较小一半，小根堆 high 存较大一半；low 的数量等于 high 或多一个。Python 大根堆通过存负数实现。插入 O(log n)，查询 O(1)，空间 O(n)。", "float")

_add(121, "买卖股票的最佳时机", "best-time-to-buy-and-sell-stock", "Easy", "贪心算法",
     "给定一只股票连续 n 天的价格，最多做一次先买后卖交易，且卖出日必须晚于买入日。求最大利润，也可以不交易。",
     "第一行 n，第二行 n 个价格。", "输出最大利润。",
     ["1 ≤ n ≤ 100000", "0 ≤ 价格 ≤ 100000"],
     [("6\n7 1 5 3 6 4\n", "5\n"), ("5\n7 6 4 3 1\n", "0\n"),
      ("1\n5\n", "0\n"), ("3\n2 2 2\n", "0\n"),
      ("5\n1 2 3 4 5\n", "4\n"), ("5\n3 0 8 1 9\n", "9\n")], '''
    n = int(input())
    prices = list(map(int, input().split()))
    minimum, answer = prices[0], 0
    for price in prices:
        answer = max(answer, price - minimum)
        minimum = min(minimum, price)
    print(answer)
''', "扫描时维护此前最低价格，用当天价格减最低价格更新利润。时间 O(n)，除输入数组外辅助空间 O(1)。")

_add(55, "跳跃游戏", "jump-game", "Medium", "贪心算法",
     "你从数组下标 0 出发，位于 i 时可以向右跳 1 到 nums[i] 步；nums[i]=0 时无法继续。判断能否到达最后一个下标。长度为 1 时已到达终点。",
     "第一行 n，第二行 n 个非负整数。", "能到达输出 true，否则输出 false。",
     ["1 ≤ n ≤ 100000", "0 ≤ nums[i] ≤ 100000"],
     [("5\n2 3 1 1 4\n", "true\n"), ("5\n3 2 1 0 4\n", "false\n"),
      ("1\n0\n", "true\n"), ("2\n0 1\n", "false\n"),
      ("4\n1 1 1 0\n", "true\n"), ("3\n2 0 0\n", "true\n")], '''
    n = int(input())
    nums = list(map(int, input().split()))
    farthest = 0
    for i, jump in enumerate(nums):
        if i > farthest:
            print('false')
            return
        farthest = max(farthest, i + jump)
    print('true')
''', "维护所有已到达位置能够扩展出的最远下标。若当前下标超过最远范围，则此处及后续均不可达。时间 O(n)，除输入外辅助空间 O(1)。")

_add(45, "跳跃游戏 II", "jump-game-ii", "Medium", "贪心算法",
     "从数组第一个下标出发，位于 i 时最多向右跳 nums[i] 步。输入保证终点可达，求到达最后一个下标的最少跳跃次数。",
     "第一行 n，第二行 n 个非负整数。", "输出最少跳跃次数。",
     ["1 ≤ n ≤ 100000", "0 ≤ nums[i] ≤ 100000", "保证最后一个下标可达"],
     [("5\n2 3 1 1 4\n", "2\n"), ("5\n2 3 0 1 4\n", "2\n"),
      ("1\n0\n", "0\n"), ("4\n1 1 1 0\n", "3\n"),
      ("4\n5 0 0 0\n", "1\n"), ("6\n2 2 2 2 2 0\n", "3\n")], '''
    n = int(input())
    nums = list(map(int, input().split()))
    jumps = end = farthest = 0
    for i in range(n - 1):
        farthest = max(farthest, i + nums[i])
        if i == end:
            jumps += 1
            end = farthest
    print(jumps)
''', "把相同跳数能覆盖的下标视为一层。扫描当前层并计算下一层最远位置，走到层边界时跳数加一。只扫描到倒数第二个下标，避免终点多跳一次。时间 O(n)，辅助空间 O(1)。")

_add(763, "划分字母区间", "partition-labels", "Medium", "贪心算法",
     "把字符串切成尽可能多的连续片段，使每一种字母只出现在其中一个片段内。输出各片段按原串顺序排列的长度。",
     "一行非空小写英文字母串。", "第一行片段数；第二行各片段长度，以空格分隔。",
     ["1 ≤ 字符串长度 ≤ 100000"],
     [("ababcbacadefegdehijhklij\n", "3\n9 7 8\n"),
      ("eccbbbbdec\n", "1\n10\n"), ("a\n", "1\n1\n"),
      ("abc\n", "3\n1 1 1\n"), ("aaaa\n", "1\n4\n"),
      ("abaccbdeffed\n", "2\n6 6\n")], '''
    s = input().strip()
    last = {char: i for i, char in enumerate(s)}
    start = end = 0
    lengths = []
    for i, char in enumerate(s):
        end = max(end, last[char])
        if i == end:
            lengths.append(end - start + 1)
            start = i + 1
    print(len(lengths))
    print(*lengths)
''', "先记录每个字母最后出现的位置。扫描片段时不断扩展必要右边界，到达边界即可尽早切分。时间 O(n)，字母表固定时除输出外辅助空间 O(1)。")

_add(70, "爬楼梯", "climbing-stairs", "Easy", "动态规划",
     "走到 n 级楼梯顶端，每次可以上 1 级或 2 级。顺序不同算不同走法，求走法数。",
     "一行整数 n。", "输出走法数。", ["1 ≤ n ≤ 45"],
     [("2\n", "2\n"), ("3\n", "3\n"), ("1\n", "1\n"),
      ("5\n", "8\n"), ("10\n", "89\n"), ("45\n", "1836311903\n")], '''
    n = int(input())
    previous, current = 1, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    print(current)
''', "最后一步来自第 n-1 或 n-2 级，所以 f(n)=f(n-1)+f(n-2)，令 f(0)=f(1)=1。滚动维护两个状态，时间 O(n)，空间 O(1)。")

_add(118, "杨辉三角", "pascals-triangle", "Easy", "动态规划",
     "输出杨辉三角的前 n 行。每行两端都是 1，内部数字等于上一行相邻两个数字之和。",
     "一行整数 n。", "输出 n 行，第 i 行包含 i 个整数，以空格分隔。",
     ["1 ≤ n ≤ 30"],
     [("5\n", "1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1\n"),
      ("1\n", "1\n"), ("2\n", "1\n1 1\n"),
      ("3\n", "1\n1 1\n1 2 1\n"),
      ("6\n", "1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1\n1 5 10 10 5 1\n")], '''
    n = int(input())
    row = [1]
    for _ in range(n):
        print(*row)
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
''', "逐行生成，只需要上一行。输出共有 n(n+1)/2 个数，时间 O(n²)，辅助空间 O(n)。")

_add(198, "打家劫舍", "house-robber", "Medium", "动态规划",
     "一排房屋中各有非负金额。不能同时选择相邻两间房屋，求可以选取的最大金额总和。允许一间也不选。",
     "第一行 n，第二行 n 个非负整数。", "输出最大金额。",
     ["1 ≤ n ≤ 100000", "0 ≤ 金额 ≤ 100000"],
     [("4\n1 2 3 1\n", "4\n"), ("5\n2 7 9 3 1\n", "12\n"),
      ("1\n0\n", "0\n"), ("1\n9\n", "9\n"),
      ("3\n2 1 2\n", "4\n"), ("4\n0 0 0 0\n", "0\n")], '''
    n = int(input())
    nums = list(map(int, input().split()))
    previous, current = 0, 0
    for value in nums:
        previous, current = current, max(current, previous + value)
    print(current)
''', "处理当前房屋有两种选择：跳过它保留前一状态，或选它并加上前两间的最优值。时间 O(n)，除输入外辅助空间 O(1)。")

_add(279, "完全平方数", "perfect-squares", "Medium", "动态规划",
     "将正整数 n 表示为若干正完全平方数之和，允许重复使用同一个平方数，求最少需要几个平方数。",
     "一行整数 n。", "输出最少数量。", ["1 ≤ n ≤ 10000"],
     [("12\n", "3\n"), ("13\n", "2\n"), ("1\n", "1\n"),
      ("7\n", "4\n"), ("100\n", "1\n"), ("2\n", "2\n")], '''
    n = int(input())
    squares = [i * i for i in range(1, int(n ** 0.5) + 1)]
    dp = [0] + [n + 1] * n
    for total in range(1, n + 1):
        for square in squares:
            if square > total:
                break
            dp[total] = min(dp[total], dp[total - square] + 1)
    print(dp[n])
''', "dp[s] 表示凑成 s 的最少数量，枚举最后使用的平方数 x²，转移为 dp[s-x²]+1。时间 O(n√n)，空间 O(n)。")

_add(322, "零钱兑换", "coin-change", "Medium", "动态规划",
     "给定若干正整数面值，每种硬币可无限使用。求凑出金额 amount 的最少硬币数，无法凑出则输出 -1。金额为 0 时不需要硬币。",
     "第一行 n amount，第二行 n 个互不相同的正整数面值。", "输出最少硬币数或 -1。",
     ["1 ≤ n ≤ 20", "0 ≤ amount ≤ 10000", "1 ≤ 面值 ≤ 10^9"],
     [("3 11\n1 2 5\n", "3\n"), ("1 3\n2\n", "-1\n"),
      ("1 0\n1\n", "0\n"), ("2 6\n3 4\n", "2\n"),
      ("3 6\n1 3 4\n", "2\n"), ("2 7\n10 12\n", "-1\n")], '''
    n, amount = map(int, input().split())
    coins = list(map(int, input().split()))
    dp = [0] + [amount + 1] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total:
                dp[total] = min(dp[total], dp[total - coin] + 1)
    print(dp[amount] if dp[amount] <= amount else -1)
''', "dp[s] 表示凑出金额 s 的最少硬币数，枚举最后一枚硬币进行转移。用 amount+1 表示不可达。时间 O(n·amount)，空间 O(amount+n)。")

_add(139, "单词拆分", "word-break", "Medium", "动态规划",
     "给定字符串和一个单词字典，判断能否把字符串切分成若干字典单词。每个单词可以使用多次，切分后必须覆盖整个字符串。",
     "第一行非空字符串 s；第二行字典大小 n；随后 n 行，每行一个非空单词。",
     "能够拆分输出 true，否则输出 false。", ["1 ≤ len(s) ≤ 300", "1 ≤ n ≤ 1000", "只含小写字母，单词长度不超过 30，字典无重复"],
     [("leetcode\n2\nleet\ncode\n", "true\n"),
      ("applepenapple\n2\napple\npen\n", "true\n"),
      ("catsandog\n5\ncats\ndog\nsand\nand\ncat\n", "false\n"),
      ("a\n1\nb\n", "false\n"), ("aaaaaaa\n2\naaa\naaaa\n", "true\n"),
      ("aaaaab\n2\na\naa\n", "false\n")], '''
    s = input().strip()
    n = int(input())
    words = {input().strip() for _ in range(n)}
    lengths = sorted({len(word) for word in words})
    dp = [True] + [False] * len(s)
    for end in range(1, len(s) + 1):
        for length in lengths:
            if length > end:
                break
            if dp[end - length] and s[end - length:end] in words:
                dp[end] = True
                break
    print('true' if dp[-1] else 'false')
''', "dp[i] 表示前 i 个字符能否拆分。只枚举字典中出现的单词长度，再检查上一段是否可达及当前片段是否在字典中。设字符串长 L、最大单词长 W，考虑切片和哈希，时间上界 O(LW²+字典总长度)，空间 O(L+字典总长度)。")

_add(300, "最长递增子序列", "longest-increasing-subsequence", "Medium", "动态规划",
     "从数组中保留若干元素，保持原先顺序但不必连续，使其严格递增。求可保留元素的最大数量。相等的相邻选择不符合严格递增。",
     "第一行 n，第二行 n 个整数。", "输出最长严格递增子序列长度。",
     ["1 ≤ n ≤ 100000", "-10^9 ≤ 元素 ≤ 10^9"],
     [("8\n10 9 2 5 3 7 101 18\n", "4\n"),
      ("6\n0 1 0 3 2 3\n", "4\n"),
      ("4\n7 7 7 7\n", "1\n"), ("1\n-3\n", "1\n"),
      ("5\n5 4 3 2 1\n", "1\n"), ("5\n-2 -1 0 1 2\n", "5\n")], '''
    n = int(input())
    nums = list(map(int, input().split()))
    tails = []
    for value in nums:
        position = bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value
    print(len(tails))
''', "tails[i] 表示长度 i+1 的递增子序列的最小结尾。对每个数二分查找第一个不小于它的位置并替换；可放在末尾则长度增加。时间 O(n log n)，空间 O(n)。")

_add(152, "乘积最大子数组", "maximum-product-subarray", "Medium", "动态规划",
     "选择一个非空连续子数组，使其中所有元素的乘积最大，输出该乘积。数组可以包含负数和零。",
     "第一行 n，第二行 n 个整数。", "输出最大乘积。",
     ["1 ≤ n ≤ 20000", "-10 ≤ 元素 ≤ 10", "保证任意连续子数组的乘积在有符号 32 位整数范围内"],
     [("4\n2 3 -2 4\n", "6\n"), ("3\n-2 0 -1\n", "0\n"),
      ("3\n-2 3 -4\n", "24\n"), ("1\n-5\n", "-5\n"),
      ("3\n0 0 0\n", "0\n"), ("3\n-1 -2 -3\n", "6\n")], '''
    n = int(input())
    nums = list(map(int, input().split()))
    largest = smallest = answer = nums[0]
    for value in nums[1:]:
        a, b = largest * value, smallest * value
        largest = max(value, a, b)
        smallest = min(value, a, b)
        answer = max(answer, largest)
    print(answer)
''', "负数会使最大和最小乘积互换作用，因此同时维护以当前位置结尾的最大乘积与最小乘积。每次从独立开始、延续最大、延续最小三种状态转移。时间 O(n)，除输入外辅助空间 O(1)。")

_add(416, "分割等和子集", "partition-equal-subset-sum", "Medium", "动态规划",
     "判断能否把所有元素分成两个不相交的子集，使两边的元素和相等。每个元素必须恰好使用一次；相同数值的不同位置视为不同元素。",
     "第一行 n，第二行 n 个正整数。", "可以分割输出 true，否则输出 false。",
     ["1 ≤ n ≤ 200", "1 ≤ 元素 ≤ 100"],
     [("4\n1 5 11 5\n", "true\n"), ("4\n1 2 3 5\n", "false\n"),
      ("1\n2\n", "false\n"), ("2\n1 1\n", "true\n"),
      ("4\n2 2 3 5\n", "false\n"), ("4\n3 3 3 3\n", "true\n")], '''
    n = int(input())
    nums = list(map(int, input().split()))
    total = sum(nums)
    if total % 2:
        print('false')
        return
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True
    for value in nums:
        for current in range(target, value - 1, -1):
            dp[current] = dp[current] or dp[current - value]
    print('true' if dp[target] else 'false')
''', "总和为奇数必不可能；否则转化为能否选若干元素凑出总和的一半。背包容量倒序更新，确保每个元素只用一次。设总和 S，时间 O(nS)，空间 O(S+n)。")

_add(32, "最长有效括号", "longest-valid-parentheses", "Hard", "动态规划",
     "给定只包含左右圆括号的字符串，求其中最长的连续合法括号子串的长度。没有合法非空子串时输出 0。",
     "一行仅含 ( 和 ) 的字符串，可以为空行。", "输出最长长度。",
     ["0 ≤ 字符串长度 ≤ 100000"],
     [("(()\n", "2\n"), (")()())\n", "4\n"), ("\n", "0\n"),
      ("()(())\n", "6\n"), ("(((\n", "0\n"), ("()(()\n", "2\n")], '''
    s = input().strip()
    dp = [0] * len(s)
    answer = 0
    for i in range(1, len(s)):
        if s[i] == ')':
            left = i - dp[i - 1] - 1
            if left >= 0 and s[left] == '(':
                dp[i] = dp[i - 1] + 2
                if left > 0:
                    dp[i] += dp[left - 1]
                answer = max(answer, dp[i])
    print(answer)
''', "dp[i] 表示以 i 结尾的最长合法长度。右括号先跨过前一段合法串，检查更前面的左括号是否匹配，再接上左括号之前的合法段。时间 O(n)，空间 O(n)。")

_add(62, "不同路径", "unique-paths", "Medium", "多维动态规划",
     "机器人从 m 行 n 列网格的左上角出发，每次只能向右或向下移动一格，求到右下角的不同路径数。",
     "一行两个整数 m n。", "输出路径数，使用整数精确输出。",
     ["1 ≤ m,n ≤ 100", "结果可能超出 64 位整数，Python 整数可直接表示"],
     [("3 7\n", "28\n"), ("3 2\n", "3\n"), ("1 1\n", "1\n"),
      ("1 8\n", "1\n"), ("5 5\n", "70\n"), ("2 3\n", "3\n")], '''
    m, n = map(int, input().split())
    dp = [1] * n
    for _ in range(1, m):
        for col in range(1, n):
            dp[col] += dp[col - 1]
    print(dp[-1])
''', "到达一个格子的路径来自上方和左方。滚动数组更新前的 dp[col] 是上方，更新后的 dp[col-1] 是左方。进行 O(mn) 次整数加法，保存 O(n) 个整数。")

_add(64, "最小路径和", "minimum-path-sum", "Medium", "多维动态规划",
     "在非负整数网格中，从左上角走到右下角，每次只能向右或向下。路径代价是经过格子的数字之和，包含起点和终点，求最小代价。",
     "第一行 m n，随后 m 行，每行 n 个非负整数。", "输出最小路径和。",
     ["1 ≤ m,n ≤ 200", "0 ≤ 格子值 ≤ 100"],
     [("3 3\n1 3 1\n1 5 1\n4 2 1\n", "7\n"),
      ("2 3\n1 2 3\n4 5 6\n", "12\n"), ("1 1\n7\n", "7\n"),
      ("1 4\n1 0 2 3\n", "6\n"), ("2 2\n0 0\n0 0\n", "0\n"),
      ("3 1\n2\n3\n4\n", "9\n")], '''
    m, n = map(int, input().split())
    dp = [float('inf')] * n
    dp[0] = 0
    for row in range(m):
        values = list(map(int, input().split()))
        for col, value in enumerate(values):
            if col == 0:
                dp[col] += value
            else:
                dp[col] = min(dp[col], dp[col - 1]) + value
    print(dp[-1])
''', "当前位置最优值等于上方和左方最优值中的较小者加格子值。逐行读取并用一维数组压缩状态，时间 O(mn)，空间 O(n)。")

_add(5, "最长回文子串", "longest-palindromic-substring", "Medium", "多维动态规划",
     "从给定字符串中找出长度最大的连续回文子串。回文串从左向右和从右向左读相同。若有多个最长答案，输出其中任意一个。",
     "一行非空字符串，由大小写英文字母和数字组成，区分大小写。",
     "输出任意一个最长回文子串。", ["1 ≤ 字符串长度 ≤ 1000"],
     [("babad\n", "bab\n"), ("cbbd\n", "bb\n"), ("a\n", "a\n"),
      ("aaaa\n", "aaaa\n"), ("abc\n", "a\n"),
      ("forgeeksskeegfor\n", "geeksskeeg\n")], '''
    s = input().strip()
    start, longest = 0, 1
    for center in range(len(s)):
        for left, right in ((center, center), (center, center + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                length = right - left + 1
                if length > longest:
                    start, longest = left, length
                left -= 1
                right += 1
    print(s[start:start + longest])
''', "枚举奇数长度和偶数长度的中心，向两侧扩展相同字符。最长回文一定拥有某个这样的中心。时间 O(n²)，除输出切片外辅助空间 O(1)。也可用区间动态规划求解。")
CHECKERS[5] = _palindrome_checker

_add(1143, "最长公共子序列", "longest-common-subsequence", "Medium", "多维动态规划",
     "给定两个字符串，求它们最长公共子序列的长度。子序列可以删除任意字符，但保留字符的相对顺序必须不变。",
     "两行字符串，每行只含小写字母，任一行可以为空。", "输出最长公共子序列长度。",
     ["两个字符串长度均为 0 到 1000"],
     [("abcde\nace\n", "3\n"), ("abc\nabc\n", "3\n"),
      ("abc\ndef\n", "0\n"), ("\nabc\n", "0\n"),
      ("aaaa\naa\n", "2\n"), ("bsbininm\njmjkbkjkv\n", "1\n")], '''
    a = input().strip()
    b = input().strip()
    if len(a) < len(b):
        a, b = b, a
    dp = [0] * (len(b) + 1)
    for char_a in a:
        diagonal = 0
        for j, char_b in enumerate(b, 1):
            above = dp[j]
            if char_a == char_b:
                dp[j] = diagonal + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            diagonal = above
    print(dp[-1])
''', "前缀末尾字符相同时，在左上角状态上加一；否则取上方和左方较大值。一维数组压缩时额外保存更新前的左上角。时间 O(mn)，空间 O(min(m,n))。")

_add(72, "编辑距离", "edit-distance", "Medium", "多维动态规划",
     "将字符串 a 变为字符串 b，每步可插入一个字符、删除一个字符或替换一个字符，每步代价均为 1。求最少操作数。",
     "第一行字符串 a，第二行字符串 b；只含小写字母，任一行可以为空。",
     "输出最少操作数。", ["两个字符串长度均为 0 到 500"],
     [("horse\nros\n", "3\n"), ("intention\nexecution\n", "5\n"),
      ("\nabc\n", "3\n"), ("abc\nabc\n", "0\n"),
      ("a\nb\n", "1\n"), ("abc\n\n", "3\n")], '''
    a = input().strip()
    b = input().strip()
    if len(a) < len(b):
        a, b = b, a
    dp = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        diagonal = dp[0]
        dp[0] = i
        for j, char_b in enumerate(b, 1):
            above = dp[j]
            if char_a == char_b:
                dp[j] = diagonal
            else:
                dp[j] = 1 + min(diagonal, dp[j], dp[j - 1])
            diagonal = above
    print(dp[-1])
''', "dp[i][j] 表示把 a 的前 i 个字符变为 b 的前 j 个字符的最少操作。末尾相同则无需操作，否则枚举替换、删除、插入，取最小值加一。时间 O(mn)，压缩后空间 O(min(m,n))。")
