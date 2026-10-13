"""Original ACM adaptations: arrays, strings, matrices and binary search."""
from collections import Counter
from textwrap import dedent

PROBLEMS = []
CHECKERS = {}


def _add(pid, title, slug, difficulty, category, description, input_format,
         output_format, constraints, cases, solution, explanation, compare="tokens",
         output_limit=None, case_timeout=None):
    tests = [{"input": i, "output": o} for i, o in cases]
    PROBLEMS.append(dict(
        id=pid, title=title, slug=slug, difficulty=difficulty, category=category,
        description=description, input_format=input_format, output_format=output_format,
        constraints=constraints, tests=tests,
        examples=[dict(tests[0], explanation="按题目要求读取输入，输出上述结果。")],
        starter="import sys\n\ninput = sys.stdin.readline\n\ndef solve():\n    # 按左侧输入格式读取数据，在此完成算法并输出答案\n    pass\n\nif __name__ == \"__main__\":\n    solve()\n",
        solution=dedent(solution).strip() + "\n", explanation=explanation,
        compare=compare))
    if output_limit is not None:
        PROBLEMS[-1]["output_limit"] = output_limit
    if case_timeout is not None:
        PROBLEMS[-1]["case_timeout"] = case_timeout


def _two_sum(stdin, actual, expected):
    try:
        tokens = list(map(int, stdin.split()))
        n, target = tokens[:2]
        nums = tokens[2:]
        a, b = map(int, actual.split())
        return len(nums) == n and 0 <= a < n and 0 <= b < n and a != b and nums[a] + nums[b] == target
    except (ValueError, TypeError):
        return False


def _anagrams(stdin, actual, expected):
    try:
        src = stdin.splitlines()
        n = int(src[0])
        words = src[1:1+n]
        lines = actual.splitlines()
        group_count = int(lines[0].strip())
        if group_count < 0 or group_count > n:
            return False
        pos, seen_keys, got = 1, set(), []
        for _ in range(group_count):
            size = int(lines[pos].strip())
            pos += 1
            if size < 1 or size > n or pos + size > len(lines):
                return False
            group = lines[pos:pos+size]
            pos += size
            key = ''.join(sorted(group[0]))
            if key in seen_keys or any(''.join(sorted(s)) != key for s in group):
                return False
            seen_keys.add(key)
            got.extend(group)
        return len(words) == n and Counter(got) == Counter(words) and all(not s.strip() for s in lines[pos:])
    except (ValueError, IndexError, TypeError):
        return False


def _triples(stdin, actual, expected):
    try:
        def parse(text):
            values = list(map(int, text.split()))
            if not values or values[0] < 0 or len(values) != 1 + 3 * values[0]:
                return None
            triples = [tuple(sorted(values[i:i+3])) for i in range(1, len(values), 3)]
            if len(set(triples)) != len(triples):
                return None
            return set(triples)
        got, want = parse(actual), parse(expected)
        return got is not None and got == want
    except (ValueError, TypeError):
        return False


def _minimum_window(stdin, actual, expected):
    try:
        lines = stdin.splitlines()
        source, target = lines[0], lines[1]
        got = actual.rstrip('\r\n')
        want = expected.rstrip('\r\n')
        counts = Counter(got)
        return len(got) == len(want) and got in source and (not want or all(counts[c] >= n for c, n in Counter(target).items()))
    except (IndexError, TypeError):
        return False


CHECKERS.update({1: _two_sum, 49: _anagrams, 15: _triples, 76: _minimum_window})

_add(1, "两数之和", "two-sum", "Easy", "哈希",
     "给定整数数组和目标值，找到两个不同位置，使这两个位置上的数之和等于目标值。数据保证至少有一组答案，返回任意一组即可。",
     "第一行两个整数 n、target。第二行 n 个整数，表示数组。",
     "输出两个不同的下标，以空格分隔。下标从 0 开始，顺序任意。",
     ["2 ≤ n ≤ 100000", "数组元素和 target 的绝对值不超过 10^9"],
     [("4 9\n2 7 11 15\n", "0 1\n"), ("2 6\n3 3\n", "0 1\n"),
      ("4 -8\n-3 4 -5 9\n", "0 2\n"), ("3 0\n0 7 0\n", "0 2\n"),
      ("5 10\n1 2 3 4 6\n", "3 4\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, target = data[:2]
         seen = {}
         for i, x in enumerate(data[2:2+n]):
             if target-x in seen:
                 print(seen[target-x], i)
                 return
             seen[x] = i
     if __name__ == "__main__":
         solve()
     ''', "从左向右扫描，用字典保存已出现的数及其下标。先查询 target-x，再存入 x，可避免重复使用同一位置。平均时间 O(n)，额外空间 O(n)。")

_add(49, "字母异位词分组", "group-anagrams", "Medium", "哈希",
     "如果两个字符串的每种字母出现次数都相同，就把它们归入同一组。请对输入的所有字符串分组，重复字符串也必须保留。空字符串可以参与分组。",
     "第一行整数 n。随后 n 行，每行一个仅含小写英文字母的字符串；某一行可以为空，表示空字符串。",
     "第一行输出组数。对每一组，先单独一行输出该组字符串数量，再逐行输出组内字符串。组的顺序及组内顺序均任意。",
     ["0 ≤ n ≤ 10000", "每个字符串长度 0 至 100", "所有字符串总长度不超过 10^6"],
     [("6\neat\ntea\ntan\nate\nnat\nbat\n", "3\n3\neat\ntea\nate\n2\ntan\nnat\n1\nbat\n"),
      ("1\n\n", "1\n1\n\n"), ("3\na\na\nb\n", "2\n2\na\na\n1\nb\n"),
      ("0\n", "0\n"), ("4\n\nab\nba\n\n", "2\n2\n\n\n2\nab\nba\n")],
     '''
     from collections import defaultdict
     import sys
     def solve():
         n = int(sys.stdin.readline())
         groups = defaultdict(list)
         for _ in range(n):
             s = sys.stdin.readline().rstrip('\\r\\n')
             count = [0] * 26
             for c in s:
                 count[ord(c)-ord('a')] += 1
             groups[tuple(count)].append(s)
         print(len(groups))
         for group in groups.values():
             print(len(group))
             for s in group:
                 print(s)
     if __name__ == "__main__":
         solve()
     ''', "对每个字符串统计 26 个字母的出现次数，将计数列表转成 tuple 作为字典键，值为同类字符串列表。tuple 可哈希，list 不可作为字典键。用 readline().rstrip('\\r\\n') 保留空字符串。若总字符数为 L，时间 O(L+26n)，额外空间 O(L+26n)。")

_add(128, "最长连续序列", "longest-consecutive-sequence", "Medium", "哈希",
     "数组中元素顺序任意。把其中若干不同的整数排成每次增加 1 的连续序列，求能得到的最长序列长度。重复数字不会增加长度。",
     "第一行整数 n。第二行 n 个整数；n 为 0 时第二行可为空。",
     "输出最长连续序列的长度。空数组输出 0。",
     ["0 ≤ n ≤ 100000", "元素绝对值不超过 10^9", "请设计期望时间 O(n) 的算法"],
     [("6\n100 4 200 1 3 2\n", "4\n"), ("0\n\n", "0\n"),
      ("5\n2 2 2 2 2\n", "1\n"), ("6\n-3 -1 -2 0 8 9\n", "4\n"),
      ("1\n1000000000\n", "1\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         values = set(data[1:1+data[0]])
         answer = 0
         for x in values:
             if x-1 not in values:
                 y = x
                 while y in values:
                     y += 1
                 answer = max(answer, y-x)
         print(answer)
     if __name__ == "__main__":
         solve()
     ''', "用集合去重。只有 x-1 不在集合中时，才从 x 向右寻找整段连续序列，这保证每个数至多被向右扫描一次。期望时间 O(n)，空间 O(n)。")

_add(283, "移动零", "move-zeroes", "Easy", "双指针",
     "把数组中所有的 0 移到末尾，其他元素保持原有相对顺序。请直接在数组上修改，避免另建同等长度的数组。",
     "第一行整数 n，第二行 n 个整数。", "输出修改后的 n 个整数，以空格分隔。",
     ["1 ≤ n ≤ 100000", "元素绝对值不超过 10^9"],
     [("5\n0 1 0 3 12\n", "1 3 12 0 0\n"), ("1\n0\n", "0\n"),
      ("3\n1 2 3\n", "1 2 3\n"), ("4\n0 0 0 0\n", "0 0 0 0\n"),
      ("5\n0 -1 0 -2 0\n", "-1 -2 0 0 0\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         a = data[1:1+data[0]]
         write = 0
         for read in range(len(a)):
             if a[read] != 0:
                 a[write], a[read] = a[read], a[write]
                 write += 1
         print(*a)
     if __name__ == "__main__":
         solve()
     ''', "write 指向下一个非零元素应放的位置；read 扫描数组。遇到非零元素便与 write 交换并前移 write，非零元素相对次序不变。算法时间 O(n)，除输入存储外额外空间 O(1)。")

_add(11, "盛最多水的容器", "container-with-most-water", "Medium", "双指针",
     "在下标 i 处有一根高度为 height[i] 的竖线。选取两根竖线与横轴组成容器，其容量定义为两下标之差乘以两高度中的较小者，求最大容量。",
     "第一行整数 n。第二行 n 个非负整数表示高度。", "输出最大容量。",
     ["2 ≤ n ≤ 100000", "0 ≤ height[i] ≤ 100000"],
     [("9\n1 8 6 2 5 4 8 3 7\n", "49\n"), ("2\n1 1\n", "1\n"),
      ("4\n0 0 0 0\n", "0\n"), ("5\n5 5 5 5 5\n", "20\n"),
      ("5\n1 2 3 4 5\n", "6\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         h = data[1:1+data[0]]
         l, r, answer = 0, len(h)-1, 0
         while l < r:
             answer = max(answer, (r-l)*min(h[l], h[r]))
             if h[l] <= h[r]:
                 l += 1
             else:
                 r -= 1
         print(answer)
     if __name__ == "__main__":
         solve()
     ''', "从最宽的两端开始，记录容量后移动较短的一端。如果固定较短端只移动高端，宽度减小且有效高度不会变大，因此可直接排除这些组合。时间 O(n)，额外空间 O(1)。")

_add(15, "三数之和", "3sum", "Medium", "双指针",
     "从数组的三个不同下标取数，使三数之和为 0。输出所有不同的数值三元组；同一组三个数的排列视为同一答案。",
     "第一行整数 n。第二行 n 个整数。",
     "第一行输出三元组数量 k，随后 k 行每行三个整数。三元组之间及每组三个数的顺序均任意，不能输出重复的三元组。",
     ["0 ≤ n ≤ 3000", "元素绝对值不超过 100000"],
     [("6\n-1 0 1 2 -1 -4\n", "2\n-1 -1 2\n-1 0 1\n"),
      ("4\n0 0 0 0\n", "1\n0 0 0\n"), ("3\n1 2 3\n", "0\n"),
      ("2\n-1 1\n", "0\n"), ("5\n-2 -1 0 1 2\n", "2\n-2 0 2\n-1 0 1\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         a = sorted(data[1:1+data[0]])
         answer = []
         for i in range(len(a)-2):
             if i and a[i] == a[i-1]:
                 continue
             if a[i] > 0:
                 break
             l, r = i+1, len(a)-1
             while l < r:
                 total = a[i]+a[l]+a[r]
                 if total < 0:
                     l += 1
                 elif total > 0:
                     r -= 1
                 else:
                     answer.append((a[i], a[l], a[r]))
                     l += 1
                     r -= 1
                     while l < r and a[l] == a[l-1]:
                         l += 1
                     while l < r and a[r] == a[r+1]:
                         r -= 1
         # Batch output: a valid large input may have over a million triples.
         lines = [str(len(answer))]
         lines.extend(' '.join(map(str, triple)) for triple in answer)
         sys.stdout.write('\\n'.join(lines) + '\\n')
     if __name__ == "__main__":
         solve()
     ''', "先排序，再固定第一个数，用左右指针寻找剩余两数。和小则左移到更大值，和大则右移到更小值。固定数及成功匹配后的两端都跳过重复值。时间 O(n²)，排序空间 O(n)，答案另计。",
     output_limit=32 * 1024 * 1024, case_timeout=10.0)

_add(42, "接雨水", "trapping-rain-water", "Hard", "双指针",
     "数组表示一排宽度均为 1 的柱子高度。雨水会被左右较高的柱子拦住，求所有柱子之间能够存储的雨水总量。",
     "第一行整数 n。第二行 n 个非负整数表示柱高。", "输出雨水总量。",
     ["1 ≤ n ≤ 100000", "0 ≤ height[i] ≤ 100000"],
     [("12\n0 1 0 2 1 0 1 3 2 1 2 1\n", "6\n"), ("1\n7\n", "0\n"),
      ("5\n1 2 3 4 5\n", "0\n"), ("3\n3 0 3\n", "3\n"),
      ("6\n4 2 0 3 2 5\n", "9\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         h = data[1:1+data[0]]
         l, r = 0, len(h)-1
         left_max = right_max = answer = 0
         while l <= r:
             left_max = max(left_max, h[l])
             right_max = max(right_max, h[r])
             if left_max <= right_max:
                 answer += left_max-h[l]
                 l += 1
             else:
                 answer += right_max-h[r]
                 r -= 1
         print(answer)
     if __name__ == "__main__":
         solve()
     ''', "维护左右扫描过的最大高度。较小的边界高度已经决定该侧当前位置的水位，因为另一侧至少存在同样高的挡板。每次结算边界较小的一侧。时间 O(n)，额外空间 O(1)。")

_add(3, "无重复字符的最长子串", "longest-substring-without-repeating-characters", "Medium", "滑动窗口",
     "给定一个字符串，求其中没有重复字符的最长连续子串长度。空格也是字符，不能删除首尾空格。",
     "输入一整行字符串 s；空行表示空字符串。", "输出最长长度。",
     ["0 ≤ len(s) ≤ 100000", "字符为可打印 ASCII 字符，不含换行符"],
     [("abcabcbb\n", "3\n"), ("\n", "0\n"), ("bbbbb\n", "1\n"),
      ("abba\n", "2\n"), ("a b a\n", "3\n")],
     '''
     import sys
     def solve():
         s = sys.stdin.readline().rstrip('\\r\\n')
         last, left, answer = {}, 0, 0
         for right, ch in enumerate(s):
             if ch in last:
                 left = max(left, last[ch]+1)
             last[ch] = right
             answer = max(answer, right-left+1)
         print(answer)
     if __name__ == "__main__":
         solve()
     ''', "维护无重复的窗口及字符最近出现的位置。右端出现重复时，把左端移到其上次出现位置之后，但左端绝不能后退。时间 O(n)，额外空间 O(字符集大小)。")

_add(438, "找到字符串中所有字母异位词", "find-all-anagrams-in-a-string", "Medium", "滑动窗口",
     "在字符串 s 中寻找所有与字符串 p 字母数量完全一致的连续子串，返回这些子串的起始下标。",
     "第一行字符串 s，第二行非空字符串 p。字符串仅含小写英文字母，s 可以为空。",
     "第一行输出匹配数量 k。第二行按升序输出 k 个从 0 开始的下标；没有匹配时第二行为空。",
     ["0 ≤ len(s) ≤ 100000", "1 ≤ len(p) ≤ 100000"],
     [("cbaebabacd\nabc\n", "2\n0 6\n"), ("abab\nab\n", "3\n0 1 2\n"),
      ("a\naa\n", "0\n\n"), ("\na\n", "0\n\n"),
      ("aaaaa\naa\n", "4\n0 1 2 3\n")],
     '''
     import sys
     def solve():
         s = sys.stdin.readline().rstrip('\\r\\n')
         p = sys.stdin.readline().rstrip('\\r\\n')
         target, window = [0]*26, [0]*26
         for c in p:
             target[ord(c)-97] += 1
         answer, width = [], len(p)
         for right, c in enumerate(s):
             window[ord(c)-97] += 1
             if right >= width:
                 window[ord(s[right-width])-97] -= 1
             if right+1 >= width and window == target:
                 answer.append(right-width+1)
         print(len(answer))
         print(*answer)
     if __name__ == "__main__":
         solve()
     ''', "窗口长度固定为 len(p)。右端加入字符，超出长度时删除左端字符，比较两个 26 维计数数组。时间 O(26·len(s)+len(p))，字母表固定时为线性；除答案外空间 O(26)。")

_add(560, "和为 K 的子数组", "subarray-sum-equals-k", "Medium", "子串",
     "统计数组中元素之和恰好为 k 的非空连续子数组数量。数组可以包含负数和 0。",
     "第一行两个整数 n、k。第二行 n 个整数。", "输出符合条件的子数组数量。",
     ["1 ≤ n ≤ 100000", "元素和 k 的绝对值不超过 10^9"],
     [("3 2\n1 1 1\n", "2\n"), ("3 0\n0 0 0\n", "6\n"),
      ("3 0\n1 -1 0\n", "3\n"), ("1 5\n5\n", "1\n"),
      ("3 7\n1 2 3\n", "0\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, k = data[:2]
         counts, prefix, answer = {0: 1}, 0, 0
         for x in data[2:2+n]:
             prefix += x
             answer += counts.get(prefix-k, 0)
             counts[prefix] = counts.get(prefix, 0)+1
         print(answer)
     if __name__ == "__main__":
         solve()
     ''', "设当前前缀和为 prefix，之前出现的 prefix-k 每出现一次，就对应一个以当前位置结尾的答案。空前缀和 0 初始出现一次。先查询后计入当前前缀，避免计数空子数组。期望时间 O(n)，空间 O(n)。")

_add(239, "滑动窗口最大值", "sliding-window-maximum", "Hard", "子串",
     "长度为 k 的窗口从数组最左边逐格移动到最右边。按移动顺序输出每个窗口内的最大元素。",
     "第一行整数 n、k。第二行 n 个整数。", "输出 n-k+1 个最大值，以空格分隔。",
     ["1 ≤ k ≤ n ≤ 100000", "元素绝对值不超过 10^9"],
     [("8 3\n1 3 -1 -3 5 3 6 7\n", "3 3 5 5 6 7\n"),
      ("1 1\n-5\n", "-5\n"), ("4 4\n2 9 1 3\n", "9\n"),
      ("4 1\n4 3 2 1\n", "4 3 2 1\n"), ("5 2\n7 7 7 7 7\n", "7 7 7 7\n")],
     '''
     from collections import deque
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, k = data[:2]
         a, q, answer = data[2:2+n], deque(), []
         for i, x in enumerate(a):
             while q and q[0] <= i-k:
                 q.popleft()
             while q and a[q[-1]] <= x:
                 q.pop()
             q.append(i)
             if i >= k-1:
                 answer.append(a[q[0]])
         print(*answer)
     if __name__ == "__main__":
         solve()
     ''', "双端队列存下标，对应值严格递减。删除队首过期下标；新值加入前删掉队尾所有不大于新值的元素，它们更早过期且不可能优于新值。队首就是最大值。时间 O(n)，除答案外空间 O(k)。")

_add(76, "最小覆盖子串", "minimum-window-substring", "Hard", "子串",
     "找出 s 中包含 t 全部字符的最短连续子串。t 中重复的字符也必须覆盖足够次数。如果有多个同长度最优解，可以输出任意一个；无法覆盖时输出空行。",
     "第一行字符串 s，第二行字符串 t。仅含大小写英文字母；两行都可以为空。",
     "输出最短子串。无解或 t 为空时输出空行。",
     ["0 ≤ len(s), len(t) ≤ 100000", "大小写字符视为不同字符"],
     [("ADOBECODEBANC\nABC\n", "BANC\n"), ("a\na\n", "a\n"),
      ("a\naa\n", "\n"), ("AAABBC\nAABC\n", "AABBC\n"),
      ("abc\n\n", "\n"), ("\nA\n", "\n")],
     '''
     from collections import Counter
     import sys
     def solve():
         s = sys.stdin.readline().rstrip('\\r\\n')
         t = sys.stdin.readline().rstrip('\\r\\n')
         if not t:
             print()
             return
         need, missing, left = Counter(t), len(t), 0
         best_start, best_length = 0, len(s)+1
         for right, c in enumerate(s):
             if need[c] > 0:
                 missing -= 1
             need[c] -= 1
             while missing == 0:
                 if right-left+1 < best_length:
                     best_start, best_length = left, right-left+1
                 need[s[left]] += 1
                 if need[s[left]] > 0:
                     missing += 1
                 left += 1
         print(s[best_start:best_start+best_length] if best_length <= len(s) else '')
     if __name__ == "__main__":
         solve()
     ''', "need 表示每种字符还缺多少，missing 表示总共还缺几个字符。右端扩张直到覆盖全部，再不断移动左端收缩并更新最短答案。字符进出窗口各一次，时间 O(len(s)+len(t))，空间 O(字符集大小)。")

_add(53, "最大子数组和", "maximum-subarray", "Medium", "普通数组",
     "从数组中选择一个非空连续子数组，使其元素之和尽可能大，输出这个最大和。",
     "第一行整数 n。第二行 n 个整数。", "输出最大子数组和。",
     ["1 ≤ n ≤ 100000", "元素绝对值不超过 10000"],
     [("9\n-2 1 -3 4 -1 2 1 -5 4\n", "6\n"), ("1\n-1\n", "-1\n"),
      ("3\n-3 -2 -5\n", "-2\n"), ("1\n0\n", "0\n"), ("3\n5 -1 5\n", "9\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         a = data[1:1+data[0]]
         ending = answer = a[0]
         for i in range(1, len(a)):
             x = a[i]
             ending = max(x, ending+x)
             answer = max(answer, ending)
         print(answer)
     if __name__ == "__main__":
         solve()
     ''', "ending 表示必须以当前位置结尾的最大和。加入 x 时只有接上前一段或从 x 重新开始两种选择，因此 ending=max(x,ending+x)。全局最大值就是答案。时间 O(n)，核心状态空间 O(1)。")

_add(56, "合并区间", "merge-intervals", "Medium", "普通数组",
     "给定若干闭区间，合并所有有交集的区间。端点相接也算有交集，例如 [1,4] 与 [4,5] 应合并。输出合并后互不相交的区间。",
     "第一行整数 n。随后 n 行每行两个整数 left、right，且 left ≤ right。",
     "第一行输出合并后的区间数。随后逐行输出两个端点，区间按左端点升序排列。",
     ["0 ≤ n ≤ 100000", "端点绝对值不超过 10^9"],
     [("4\n1 3\n2 6\n8 10\n15 18\n", "3\n1 6\n8 10\n15 18\n"),
      ("0\n", "0\n"), ("1\n2 2\n", "1\n2 2\n"),
      ("2\n1 4\n4 5\n", "1\n1 5\n"),
      ("4\n-2 3\n-5 -3\n0 1\n-3 -2\n", "1\n-5 3\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n = data[0]
         intervals = sorted((data[1+2*i], data[2+2*i]) for i in range(n))
         answer = []
         for left, right in intervals:
             if answer and left <= answer[-1][1]:
                 answer[-1][1] = max(answer[-1][1], right)
             else:
                 answer.append([left, right])
         print(len(answer))
         for interval in answer:
             print(*interval)
     if __name__ == "__main__":
         solve()
     ''', "按左端点排序，维护最后一个合并区间。如果新区间左端点不超过最后区间右端点，就扩展右端点；否则开启新区间。时间 O(n log n)，空间 O(n)。")

_add(189, "轮转数组", "rotate-array", "Medium", "普通数组",
     "把数组向右循环移动 k 位：每次移动时末尾元素来到开头，其余元素依次右移。请使用 O(1) 额外空间完成核心操作。",
     "第一行整数 n、k。第二行 n 个整数。", "输出轮转后的 n 个整数。",
     ["1 ≤ n ≤ 100000", "0 ≤ k ≤ 10^9", "元素绝对值不超过 10^9"],
     [("7 3\n1 2 3 4 5 6 7\n", "5 6 7 1 2 3 4\n"),
      ("4 2\n-1 -100 3 99\n", "3 99 -1 -100\n"),
      ("3 0\n1 2 3\n", "1 2 3\n"), ("3 4\n1 2 3\n", "3 1 2\n"),
      ("1 100\n8\n", "8\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, k = data[:2]
         a = data[2:2+n]
         k %= n
         def reverse(left, right):
             while left < right:
                 a[left], a[right] = a[right], a[left]
                 left += 1
                 right -= 1
         reverse(0, n-1)
         reverse(0, k-1)
         reverse(k, n-1)
         print(*a)
     if __name__ == "__main__":
         solve()
     ''', "先用 k%=n 去掉整圈移动，再反转整个数组、前 k 个元素、剩下的元素。三次反转会把原后缀移到前面并恢复两段内部顺序。时间 O(n)，除输入存储外额外空间 O(1)。")

_add(238, "除自身以外数组的乘积", "product-of-array-except-self", "Medium", "普通数组",
     "构造数组 answer，其中 answer[i] 等于输入数组中除下标 i 外所有元素的乘积。不能使用除法，允许使用返回结果数组作为存储。",
     "第一行整数 n。第二行 n 个整数。", "输出 n 个乘积，以空格分隔。",
     ["2 ≤ n ≤ 100000", "-30 ≤ nums[i] ≤ 30", "所有前缀、后缀乘积和答案均在 64 位有符号整数范围内"],
     [("4\n1 2 3 4\n", "24 12 8 6\n"), ("4\n0 0 2 3\n", "0 0 0 0\n"),
      ("5\n-1 1 0 -3 3\n", "0 0 9 0 0\n"), ("2\n2 3\n", "3 2\n"),
      ("3\n-1 -2 -3\n", "6 3 2\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, a = data[0], data[1:1+data[0]]
         answer, prefix = [1]*n, 1
         for i in range(n):
             answer[i] = prefix
             prefix *= a[i]
         suffix = 1
         for i in range(n-1, -1, -1):
             answer[i] *= suffix
             suffix *= a[i]
         print(*answer)
     if __name__ == "__main__":
         solve()
     ''', "第一遍把每个位置左侧所有数的乘积写入答案，第二遍从右向左累积后缀乘积并乘入答案。自然支持 0，无需分类处理。时间 O(n)，除答案和输入外空间 O(1)。")

_add(41, "缺失的第一个正数", "first-missing-positive", "Hard", "普通数组",
     "给定一个未排序整数数组，求没有在数组中出现的最小正整数。请设计时间 O(n)、额外空间 O(1) 的算法。",
     "第一行整数 n。第二行 n 个整数；n 为 0 时该行可为空。", "输出缺失的最小正整数。",
     ["0 ≤ n ≤ 100000", "元素绝对值不超过 10^9"],
     [("4\n3 4 -1 1\n", "2\n"), ("3\n1 2 0\n", "3\n"),
      ("5\n7 8 9 11 12\n", "1\n"), ("0\n\n", "1\n"),
      ("5\n1 1 2 2 -3\n", "3\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, a = data[0], data[1:1+data[0]]
         for i in range(n):
             while 1 <= a[i] <= n and a[a[i]-1] != a[i]:
                 target = a[i]-1
                 a[i], a[target] = a[target], a[i]
         for i, x in enumerate(a):
             if x != i+1:
                 print(i+1)
                 return
         print(n+1)
     if __name__ == "__main__":
         solve()
     ''', "答案一定在 1 到 n+1 之间。让范围内的数字 x 尽可能放到下标 x-1，每次交换至少让一个数归位，检查目标位已等于 x 可避免重复值造成死循环。最终第一个不匹配的位置就是答案。时间 O(n)，核心额外空间 O(1)。")

_add(73, "矩阵置零", "set-matrix-zeroes", "Medium", "矩阵",
     "对矩阵中原本为 0 的每个元素，把它所在的整行和整列都置为 0。新产生的 0 不会继续触发其他行列。请尽量原地完成。",
     "第一行整数 m、n。随后 m 行，每行 n 个整数。", "输出修改后的矩阵，共 m 行，每行 n 个整数。",
     ["1 ≤ m,n ≤ 200", "元素绝对值不超过 10^9"],
     [("3 3\n1 1 1\n1 0 1\n1 1 1\n", "1 0 1\n0 0 0\n1 0 1\n"),
      ("2 3\n0 1 2\n3 4 5\n", "0 0 0\n0 4 5\n"),
      ("1 1\n5\n", "5\n"), ("1 4\n1 0 3 4\n", "0 0 0 0\n"),
      ("3 2\n1 2\n3 4\n5 0\n", "1 0\n3 0\n0 0\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         m, n = data[:2]
         a = [data[2+i*n:2+(i+1)*n] for i in range(m)]
         first_row = any(x == 0 for x in a[0])
         first_col = any(a[i][0] == 0 for i in range(m))
         for i in range(1, m):
             for j in range(1, n):
                 if a[i][j] == 0:
                     a[i][0] = a[0][j] = 0
         for i in range(1, m):
             for j in range(1, n):
                 if a[i][0] == 0 or a[0][j] == 0:
                     a[i][j] = 0
         if first_row:
             for j in range(n):
                 a[0][j] = 0
         if first_col:
             for i in range(m):
                 a[i][0] = 0
         for row in a:
             print(*row)
     if __name__ == "__main__":
         solve()
     ''', "用第一行和第一列记录其余行列是否应清零，另外用两个布尔值保存第一行和第一列原本是否含 0。先标记、再改内部、最后处理首行首列，避免新 0 污染判断。时间 O(mn)，核心额外空间 O(1)。")

_add(54, "螺旋矩阵", "spiral-matrix", "Medium", "矩阵",
     "从矩阵左上角开始，沿顺时针方向按圈访问所有元素，依次输出访问到的数。每个元素恰好访问一次。",
     "第一行整数 m、n。随后 m 行，每行 n 个整数。", "在一行中输出按螺旋顺序访问的 m×n 个数。",
     ["1 ≤ m,n ≤ 200", "元素绝对值不超过 10^9"],
     [("3 3\n1 2 3\n4 5 6\n7 8 9\n", "1 2 3 6 9 8 7 4 5\n"),
      ("1 4\n1 2 3 4\n", "1 2 3 4\n"), ("4 1\n1\n2\n3\n4\n", "1 2 3 4\n"),
      ("2 3\n1 2 3\n4 5 6\n", "1 2 3 6 5 4\n"), ("1 1\n-8\n", "-8\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         m, n = data[:2]
         a = [data[2+i*n:2+(i+1)*n] for i in range(m)]
         top, bottom, left, right = 0, m-1, 0, n-1
         answer = []
         while top <= bottom and left <= right:
             for j in range(left, right+1):
                 answer.append(a[top][j])
             top += 1
             for i in range(top, bottom+1):
                 answer.append(a[i][right])
             right -= 1
             if top <= bottom:
                 for j in range(right, left-1, -1):
                     answer.append(a[bottom][j])
                 bottom -= 1
             if left <= right:
                 for i in range(bottom, top-1, -1):
                     answer.append(a[i][left])
                 left += 1
         print(*answer)
     if __name__ == "__main__":
         solve()
     ''', "维护尚未访问区域的上下左右边界，依次访问上边、右边、下边、左边并收缩。访问下边和左边前检查边界，避免只有一行或一列时重复输出。时间 O(mn)，除答案和输入外空间 O(1)。")

_add(48, "旋转图像", "rotate-image", "Medium", "矩阵",
     "把 n×n 方阵顺时针旋转 90 度。要求直接修改矩阵，不能额外创建同样大小的矩阵。",
     "第一行整数 n。随后 n 行，每行 n 个整数。", "输出旋转后的 n 行矩阵。",
     ["1 ≤ n ≤ 200", "元素绝对值不超过 10^9"],
     [("3\n1 2 3\n4 5 6\n7 8 9\n", "7 4 1\n8 5 2\n9 6 3\n"),
      ("1\n5\n", "5\n"), ("2\n1 2\n3 4\n", "3 1\n4 2\n"),
      ("4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 15 16\n", "13 9 5 1\n14 10 6 2\n15 11 7 3\n16 12 8 4\n"),
      ("2\n-1 0\n3 -4\n", "3 -1\n-4 0\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n = data[0]
         a = [data[1+i*n:1+(i+1)*n] for i in range(n)]
         for i in range(n):
             for j in range(i+1, n):
                 a[i][j], a[j][i] = a[j][i], a[i][j]
         for row in a:
             row.reverse()
             print(*row)
     if __name__ == "__main__":
         solve()
     ''', "先沿主对角线转置，再把每一行原地反转。坐标变化为 (i,j)→(j,i)→(j,n-1-i)，正好是顺时针旋转 90 度。时间 O(n²)，核心额外空间 O(1)。")

_add(240, "搜索二维矩阵 II", "search-a-2d-matrix-ii", "Medium", "矩阵",
     "矩阵每一行从左到右非递减，每一列从上到下非递减。判断目标数是否存在于矩阵中。下一行首元素不保证大于上一行末元素。",
     "第一行整数 m、n、target。随后 m 行，每行 n 个整数。", "找到输出 true，否则输出 false。",
     ["1 ≤ m,n ≤ 300", "矩阵元素和 target 的绝对值不超过 10^9"],
     [("3 3 5\n1 4 7\n2 5 8\n3 6 9\n", "true\n"),
      ("3 3 10\n1 4 7\n2 5 8\n3 6 9\n", "false\n"),
      ("1 1 -3\n-3\n", "true\n"), ("2 2 2\n1 1\n1 1\n", "false\n"),
      ("3 2 -2\n-5 -3\n-2 0\n1 4\n", "true\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         m, n, target = data[:3]
         a = [data[3+i*n:3+(i+1)*n] for i in range(m)]
         i, j = 0, n-1
         while i < m and j >= 0:
             if a[i][j] == target:
                 print('true')
                 return
             if a[i][j] > target:
                 j -= 1
             else:
                 i += 1
         print('false')
     if __name__ == "__main__":
         solve()
     ''', "从右上角开始。当前位置偏大时，该列下面的数也偏大，可以删除整列；偏小时，该行左边的数也偏小，可以删除整行。每一步排除一行或一列，查询时间 O(m+n)，核心额外空间 O(1)。")

_add(35, "搜索插入位置", "search-insert-position", "Easy", "二分查找",
     "在严格递增数组中查找 target。若存在，输出它的下标；若不存在，输出保持有序时应插入的位置，下标从 0 开始。",
     "第一行整数 n、target。第二行 n 个严格递增的整数。", "输出一个下标，范围为 0 到 n。",
     ["0 ≤ n ≤ 100000", "元素及 target 的绝对值不超过 10^9", "查询部分要求 O(log n) 时间"],
     [("4 5\n1 3 5 6\n", "2\n"), ("4 2\n1 3 5 6\n", "1\n"),
      ("4 7\n1 3 5 6\n", "4\n"), ("4 0\n1 3 5 6\n", "0\n"),
      ("0 10\n\n", "0\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, target = data[:2]
         a = data[2:2+n]
         left, right = 0, n
         while left < right:
             mid = (left+right)//2
             if a[mid] < target:
                 left = mid+1
             else:
                 right = mid
         print(left)
     if __name__ == "__main__":
         solve()
     ''', "寻找第一个大于等于 target 的位置。用左闭右开区间 [left,right)，如果 a[mid]<target，则答案在 mid 右边；否则保留 mid 并收缩右边界。查询时间 O(log n)，额外空间 O(1)，读入仍需 O(n)。")

_add(74, "搜索二维矩阵", "search-a-2d-matrix", "Medium", "二分查找",
     "矩阵每行从左到右非递减，并且每一行的首元素都严格大于上一行的末元素。判断目标数是否存在。",
     "第一行整数 m、n、target。随后 m 行，每行 n 个整数。", "存在输出 true，不存在输出 false。",
     ["1 ≤ m,n ≤ 300", "矩阵元素及 target 的绝对值不超过 10^9", "查询部分要求 O(log(mn)) 时间"],
     [("3 4 3\n1 3 5 7\n10 11 16 20\n23 30 34 60\n", "true\n"),
      ("3 4 13\n1 3 5 7\n10 11 16 20\n23 30 34 60\n", "false\n"),
      ("1 1 -1\n-1\n", "true\n"), ("2 1 2\n1\n3\n", "false\n"),
      ("2 3 9\n1 1 2\n3 5 9\n", "true\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         m, n, target = data[:3]
         a = [data[3+i*n:3+(i+1)*n] for i in range(m)]
         left, right = 0, m*n
         while left < right:
             mid = (left+right)//2
             value = a[mid//n][mid%n]
             if value == target:
                 print('true')
                 return
             if value < target:
                 left = mid+1
             else:
                 right = mid
         print('false')
     if __name__ == "__main__":
         solve()
     ''', "把矩阵看成按行展开的有序数组，不需要实际复制展开。第 mid 项对应第 mid//n 行、第 mid%n 列。对下标区间执行普通二分。查询时间 O(log(mn))，额外空间 O(1)，读入时间 O(mn)。")

_add(34, "在排序数组中查找元素的第一个和最后一个位置", "find-first-and-last-position-of-element-in-sorted-array", "Medium", "二分查找",
     "数组按非递减顺序排列。输出 target 第一次出现和最后一次出现的下标；如果不存在，输出两个 -1。",
     "第一行整数 n、target。第二行 n 个非递减整数。", "输出两个从 0 开始的下标；不存在时输出 -1 -1。",
     ["0 ≤ n ≤ 100000", "元素及 target 的绝对值不超过 10^9", "查询部分要求 O(log n) 时间"],
     [("6 8\n5 7 7 8 8 10\n", "3 4\n"), ("6 6\n5 7 7 8 8 10\n", "-1 -1\n"),
      ("0 0\n\n", "-1 -1\n"), ("4 2\n2 2 2 2\n", "0 3\n"),
      ("1 -5\n-5\n", "0 0\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, target = data[:2]
         a = data[2:2+n]
         def lower_bound(value):
             left, right = 0, n
             while left < right:
                 mid = (left+right)//2
                 if a[mid] < value:
                     left = mid+1
                 else:
                     right = mid
             return left
         first = lower_bound(target)
         if first == n or a[first] != target:
             print(-1, -1)
         else:
             print(first, lower_bound(target+1)-1)
     if __name__ == "__main__":
         solve()
     ''', "分别二分第一个大于等于 target 和第一个大于 target 的位置，后者减 1 即右端点。因为元素是整数，第二次可查 lower_bound(target+1)。先确认左端点确实命中。查询时间 O(log n)，额外空间 O(1)。")

_add(33, "搜索旋转排序数组", "search-in-rotated-sorted-array", "Medium", "二分查找",
     "一个元素互不相同的严格递增数组经过某次循环位移，形成当前数组。查找 target 的下标，找不到则输出 -1。数组也可能没有发生位移。",
     "第一行整数 n、target。第二行 n 个整数，满足上述旋转性质。", "输出 target 的下标（从 0 开始），不存在时输出 -1。",
     ["1 ≤ n ≤ 100000", "数组元素互不相同，元素及 target 的绝对值不超过 10^9", "查询部分要求 O(log n) 时间"],
     [("7 0\n4 5 6 7 0 1 2\n", "4\n"), ("7 3\n4 5 6 7 0 1 2\n", "-1\n"),
      ("1 1\n1\n", "0\n"), ("2 1\n3 1\n", "1\n"),
      ("5 5\n1 2 3 4 5\n", "4\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n, target = data[:2]
         a = data[2:2+n]
         left, right = 0, n-1
         while left <= right:
             mid = (left+right)//2
             if a[mid] == target:
                 print(mid)
                 return
             if a[left] <= a[mid]:
                 if a[left] <= target < a[mid]:
                     right = mid-1
                 else:
                     left = mid+1
             else:
                 if a[mid] < target <= a[right]:
                     left = mid+1
                 else:
                     right = mid-1
         print(-1)
     if __name__ == "__main__":
         solve()
     ''', "每次二分后，左右两半至少有一半严格有序。先判断哪半边有序，再检查 target 是否在该半边的值域内，据此保留一半搜索区间。查询时间 O(log n)，额外空间 O(1)。")

_add(153, "寻找旋转排序数组中的最小值", "find-minimum-in-rotated-sorted-array", "Medium", "二分查找",
     "一个严格递增、没有重复元素的数组经过循环位移后，求当前数组中的最小值。允许数组保持原样。",
     "第一行整数 n。第二行 n 个整数，满足旋转排序性质。", "输出数组中的最小元素。",
     ["1 ≤ n ≤ 100000", "元素互不相同，绝对值不超过 10^9", "查询部分要求 O(log n) 时间"],
     [("5\n3 4 5 1 2\n", "1\n"), ("7\n4 5 6 7 0 1 2\n", "0\n"),
      ("4\n11 13 15 17\n", "11\n"), ("1\n-3\n", "-3\n"),
      ("2\n2 1\n", "1\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         a = data[1:1+data[0]]
         left, right = 0, len(a)-1
         while left < right:
             mid = (left+right)//2
             if a[mid] > a[right]:
                 left = mid+1
             else:
                 right = mid
         print(a[left])
     if __name__ == "__main__":
         solve()
     ''', "比较中点与右端：若 a[mid]>a[right]，最小值必在中点右边；否则中点到右端有序，最小值可能是 mid 或在左边。循环保持最小值在闭区间内。查询时间 O(log n)，额外空间 O(1)。")

_add(4, "寻找两个正序数组的中位数", "median-of-two-sorted-arrays", "Hard", "二分查找",
     "给定两个分别按非递减顺序排列的数组，求它们合并后的中位数。总长度为奇数时取中间元素，为偶数时取中间两个元素的平均值。",
     "第一行整数 m、n。第二行 m 个整数表示第一个数组。第三行 n 个整数表示第二个数组。长度为 0 的数组对应空行。",
     "输出中位数，整数或小数写法均可。允许绝对或相对误差不超过 10^-6。",
     ["0 ≤ m,n ≤ 100000，且 m+n ≥ 1", "元素绝对值不超过 10^9", "查询部分要求 O(log(min(m,n)+1)) 时间"],
     [("2 1\n1 3\n2\n", "2\n"), ("2 2\n1 2\n3 4\n", "2.5\n"),
      ("0 1\n\n1\n", "1\n"), ("2 2\n0 0\n0 0\n", "0\n"),
      ("2 2\n-5 -3\n-2 -1\n", "-2.5\n"), ("2 0\n5 9\n\n", "7\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         m, n = data[:2]
         a, b = data[2:2+m], data[2+m:2+m+n]
         if m > n:
             a, b, m, n = b, a, n, m
         left, right = 0, m
         half = (m+n+1)//2
         while left <= right:
             i = (left+right)//2
             j = half-i
             al = a[i-1] if i else float('-inf')
             ar = a[i] if i < m else float('inf')
             bl = b[j-1] if j else float('-inf')
             br = b[j] if j < n else float('inf')
             if al > br:
                 right = i-1
             elif bl > ar:
                 left = i+1
             else:
                 if (m+n) % 2:
                     print(max(al, bl))
                 else:
                     print((max(al, bl)+min(ar, br))/2)
                 return
     if __name__ == "__main__":
         solve()
     ''', "在较短数组中二分分割位置 i，另一个数组分割位置 j 由左半总数固定决定。只需保证两数组左半最大值均不大于另一数组右半最小值。若左半偏大则减少 i，若另一侧左半偏大则增大 i。边界用正负无穷处理。查询时间 O(log(min(m,n)+1))，额外空间 O(1)，读入仍为 O(m+n)。", compare="float")

_add(136, "只出现一次的数字", "single-number", "Easy", "技巧",
     "数组中恰好有一个整数出现一次，其余每个整数都出现两次。找出只出现一次的整数。",
     "第一行整数 n。第二行 n 个整数。", "输出只出现一次的整数。",
     ["1 ≤ n ≤ 100001，n 为奇数", "元素在 32 位有符号整数范围内", "要求 O(n) 时间、O(1) 额外空间"],
     [("5\n4 1 2 1 2\n", "4\n"), ("1\n7\n", "7\n"),
      ("3\n-1 2 2\n", "-1\n"), ("5\n0 -3 5 -3 5\n", "0\n"),
      ("3\n-2147483648 2147483647 2147483647\n", "-2147483648\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         answer = 0
         for x in data[1:1+data[0]]:
             answer ^= x
         print(answer)
     if __name__ == "__main__":
         solve()
     ''', "异或满足 x^x=0、x^0=x，且可交换和结合。把所有元素异或，成对元素互相抵消，剩下的就是只出现一次的数。Python 的整数异或也适用于负数。时间 O(n)，核心额外空间 O(1)。")

_add(169, "多数元素", "majority-element", "Easy", "技巧",
     "数组中有一个数的出现次数严格超过数组长度的一半。数据保证这个数存在，请输出它。",
     "第一行整数 n。第二行 n 个整数。", "输出多数元素。",
     ["1 ≤ n ≤ 100000", "元素绝对值不超过 10^9", "要求 O(n) 时间、O(1) 额外空间"],
     [("7\n2 2 1 1 1 2 2\n", "2\n"), ("1\n9\n", "9\n"),
      ("5\n-1 -1 2 -1 3\n", "-1\n"), ("4\n0 0 0 1\n", "0\n"),
      ("5\n1 2 3 3 3\n", "3\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         candidate, votes = 0, 0
         for x in data[1:1+data[0]]:
             if votes == 0:
                 candidate = x
             votes += 1 if x == candidate else -1
         print(candidate)
     if __name__ == "__main__":
         solve()
     ''', "摩尔投票法：维护候选数和票数，同值加一，不同值减一，票数归零时更换候选。每次抵消一对不同数字，而多数元素数量超过其余总和，最终一定留下多数元素。题目保证存在，因此无需额外验证。时间 O(n)，核心空间 O(1)。")

_add(75, "颜色分类", "sort-colors", "Medium", "技巧",
     "数组只包含 0、1、2 三种数。将它们原地排列成所有 0 在前、1 居中、2 在后。不要直接调用排序函数。",
     "第一行整数 n。第二行 n 个整数，每个整数为 0、1 或 2。", "输出重新排列的 n 个整数。",
     ["1 ≤ n ≤ 100000", "目标为 O(n) 时间、O(1) 额外空间"],
     [("6\n2 0 2 1 1 0\n", "0 0 1 1 2 2\n"), ("1\n2\n", "2\n"),
      ("4\n1 1 1 1\n", "1 1 1 1\n"), ("6\n0 0 1 1 2 2\n", "0 0 1 1 2 2\n"),
      ("5\n2 2 0 2 0\n", "0 0 2 2 2\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         a = data[1:1+data[0]]
         left, scan, right = 0, 0, len(a)-1
         while scan <= right:
             if a[scan] == 0:
                 a[left], a[scan] = a[scan], a[left]
                 left += 1
                 scan += 1
             elif a[scan] == 2:
                 a[scan], a[right] = a[right], a[scan]
                 right -= 1
             else:
                 scan += 1
         print(*a)
     if __name__ == "__main__":
         solve()
     ''', "荷兰国旗划分：left 左边全为 0，right 右边全为 2，scan 之前未归零的部分全为 1。遇到 0 换到左侧，遇到 2 换到右侧；与右端交换后，新换来的值尚未检查，所以 scan 不前进。时间 O(n)，核心空间 O(1)。")

_add(31, "下一个排列", "next-permutation", "Medium", "技巧",
     "把数组看成一个允许重复元素的排列。修改成字典序上紧邻它的下一个更大排列；若已是最大排列，则改成最小排列。字典序在首个不同的位置比较数值大小。",
     "第一行整数 n。第二行 n 个整数。", "输出下一个排列的 n 个整数。",
     ["1 ≤ n ≤ 100000", "元素绝对值不超过 10^9", "要求原地修改、O(1) 额外空间"],
     [("3\n1 2 3\n", "1 3 2\n"), ("3\n3 2 1\n", "1 2 3\n"),
      ("3\n1 1 5\n", "1 5 1\n"), ("1\n8\n", "8\n"),
      ("3\n1 3 2\n", "2 1 3\n"), ("3\n2 2 2\n", "2 2 2\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         a = data[1:1+data[0]]
         i = len(a)-2
         while i >= 0 and a[i] >= a[i+1]:
             i -= 1
         if i >= 0:
             j = len(a)-1
             while a[j] <= a[i]:
                 j -= 1
             a[i], a[j] = a[j], a[i]
         left, right = i+1, len(a)-1
         while left < right:
             a[left], a[right] = a[right], a[left]
             left += 1
             right -= 1
         print(*a)
     if __name__ == "__main__":
         solve()
     ''', "从右向左找第一个 a[i]<a[i+1] 的位置，把它与右侧最小的、严格大于它的数交换。右侧原本是非递增序列，因此从最右端找第一个更大值即可。最后反转右侧，使增大的幅度最小。若找不到 i，反转整个数组。时间 O(n)，核心空间 O(1)。")

_add(287, "寻找重复数", "find-the-duplicate-number", "Medium", "技巧",
     "给定 n+1 个整数，每个都在 1 到 n 之间。恰好只有一个数出现超过一次，其他数最多出现一次。找出这个重复数；它可能出现两次以上。不能修改数组，要求 O(1) 额外空间。",
     "第一行整数 n。第二行 n+1 个整数。注意：第一行 n 比数组长度少 1。", "输出重复的那个数。",
     ["1 ≤ n ≤ 100000", "1 ≤ nums[i] ≤ n", "恰好一个数出现多次，数组长度为 n+1"],
     [("4\n1 3 4 2 2\n", "2\n"), ("4\n3 1 3 4 2\n", "3\n"),
      ("1\n1 1\n", "1\n"), ("4\n2 2 2 2 2\n", "2\n"),
      ("5\n1 2 3 4 5 5\n", "5\n")],
     '''
     import sys
     def solve():
         data = list(map(int, sys.stdin.buffer.read().split()))
         n = data[0]
         a = data[1:n+2]
         slow = fast = 0
         while True:
             slow = a[slow]
             fast = a[a[fast]]
             if slow == fast:
                 break
         finder = 0
         while finder != slow:
             finder = a[finder]
             slow = a[slow]
         print(finder)
     if __name__ == "__main__":
         solve()
     ''', "把下标 i 指向 nums[i]，从 0 出发得到一个必定进入环的路径。0 没有入边，路径的环入口有来自环内和环外的两条入边，因此入口值就是重复数。先用快慢指针找相遇点，再让一个指针回到 0，两者同速前进到相遇即可得到入口。时间 O(n)，核心空间 O(1)。")
