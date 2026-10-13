"""Build original, fixed ACM I/O exercises and independently computed fixtures.

This developer-only script never runs a reference solution to obtain expected
answers. Runtime reads the committed JSON; running this builder is optional.
"""
from fractions import Fraction
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = []
CATEGORY = "ACM 输入输出基础"
STARTER = '''import sys


def solve():
    # 先确认：一组数据是什么？何时停止？每组要输出几行？
    pass


if __name__ == "__main__":
    solve()
'''


def lines(values):
    """Format nonempty output records with one terminal newline."""
    return "\n".join(map(str, values)) + ("\n" if values else "")


def add(number, title, slug, description, input_format, output_format,
        constraints, clarifications, examples, cases, code, explanation):
    code = dedent(code).strip() + "\n"
    compile(code, f"io-{number:02}.py", "exec")
    tests = [{"input": stdin, "output": expected} for stdin, expected in cases]
    assert len(tests) >= 20
    assert len({case["input"] for case in tests}) == len(tests)
    assert len(examples) == 3
    assert all(example["explanation"] for example in examples)
    assert all(not case["output"] or case["output"].endswith("\n") for case in tests)
    PROBLEMS.append({
        "id": 10000 + number, "display_id": f"IO-{number:02}", "track": "acm_io",
        "title": title, "slug": slug, "difficulty": "Easy", "category": CATEGORY,
        "description": description, "input_format": input_format,
        "output_format": output_format, "constraints": constraints,
        "clarifications": clarifications, "examples": examples, "tests": tests,
        "starter": STARTER, "solution": code, "explanation": explanation,
        "compare": "exact",
    })


def example(stdin, expected, explanation):
    return {"input": stdin, "output": expected, "explanation": explanation}


def build():
    PROBLEMS.clear()

    # 01: a single pair. Expected answers use only the mathematical sum.
    pairs = [(7, 12), (-8, 13), (0, 0), (1, 1), (-1, -1), (0, 9), (9, 0),
             (1000000000, 1000000000), (-1000000000, -1000000000),
             (1000000000, -1000000000), (42, -42), (13, 29), (101, 909),
             (-73, 22), (55, -89), (-16, -23), (8, 2048), (999, 1),
             (123456, 654321), (27, -6), (19, 81), (-50, 200)]
    formats = ["{a} {b}\n", " {a}\t{b} \n", "{a}\n{b}\n", "\n{a}  {b}", "{a} {b}"]
    cases = [(formats[i % len(formats)].format(a=a, b=b), lines([a + b]))
             for i, (a, b) in enumerate(pairs)]
    add(1, "一组两个整数：先读再算", "acm-io-one-pair",
        "输入只包含一组数据：两个整数 a 和 b。请读取这两个数，输出它们的和。此题不要求复杂算法，重点是把标准输入转换成整数，并按要求输出一行结果。",
        "输入恰好包含两个整数 a、b，以一个或多个空白字符分隔。空白可以是空格、制表符或换行；最后一行不一定以换行结束。",
        "输出 a+b，占一行。不要添加提示语、标签或其他内容。",
        ["-10^9 ≤ a,b ≤ 10^9", "输入恰好有两个整数"],
        ["换行也是分隔符，两个数不一定出现在同一物理行。", "先把输入转换成 int，再相加；字符串相加会拼接文本。", "这不是多组数据题，只输出一个结果。"],
        [example("7 12\n", "19\n", "读取整数 7 和 12，相加得到 19。"),
         example("-8\n13\n", "5\n", "两个数分处两行，仍是一组；-8+13=5。"),
         example("0 0\n", "0\n", "这里没有结束标记，0 和 0 是正常数据。")],
        cases, '''
        import sys

        def solve():
            a, b = map(int, sys.stdin.buffer.read().split())
            print(a + b)

        if __name__ == "__main__":
            solve()
        ''', "先用 read().split() 按空白切成两个 token，再用 int 转换并相加。记住：读入、转换、计算、输出。设输入字符数为 L，读取和转换耗时 O(L)，保存原始输入需要 O(L) 空间；两个整数相加的计算量在给定范围内可视为常数。")

    # 02: n specifies token count; array wrapping does not change grouping.
    arrays = [[3, -2, 7, 0, 4], [], [9], [-4], [0], [1, 2], [-1, -2],
              [5, -5], [0, 0, 0], [1000000000] * 4, [-1000000000] * 3,
              list(range(1, 11)), list(range(-5, 6)), [17, -9, 3],
              [1] * 25, [-1] * 30, [88, 7, 5], [2, 4, 6, 8],
              [99, -100, 1], [31, 41, 59, 26], list(range(100)), [8, -3, 12, -7, 6, 0]]
    cases = []
    for i, values in enumerate(arrays):
        separator = [" ", "\n", "\t", "  "][i % 4]
        stdin = str(len(values)) + "\n" + separator.join(map(str, values))
        if i % 3:
            stdin += "\n"
        cases.append((stdin, lines([sum(values)])))
    add(2, "先读 n：固定长度数组求和", "acm-io-fixed-array",
        "先读取数组长度 n，再读取恰好 n 个整数，输出这些整数的总和。数组可以被排版成一行或多行，你应按照 n 确定数据数量，而不是按照行数猜测。",
        "第一个整数是 n；随后恰好 n 个整数表示数组。所有整数以空白分隔，可以跨行。n=0 时不再有数组元素。",
        "输出数组元素之和，占一行。空数组输出 0。",
        ["0 ≤ n ≤ 100000", "每个数组元素的绝对值不超过 10^9"],
        ["n 是长度，不参加求和。", "一行未读够 n 个数时，仍需继续读取后面的 token。", "n=0 合法，答案为 0，不是停止处理的特殊标记。"],
        [example("5\n3 -2 7 0 4\n", "12\n", "长度为 5，求和 3-2+7+0+4=12。"),
         example("4\n8 -3\n12 -7\n", "10\n", "四个元素分处两行；跨行不改变数组长度。"),
         example("0\n", "0\n", "没有数组元素，空集合的和为 0。")],
        cases, '''
        import sys

        def solve():
            tokens = iter(sys.stdin.buffer.read().split())
            n = int(next(tokens))
            total = sum(int(next(tokens)) for _ in range(n))
            print(total)

        if __name__ == "__main__":
            solve()
        ''', "把全部空白分隔的 token 交给迭代器，先 next() 取得长度，再恰好取 n 个整数求和。顺口记：先读长度，再读内容。必须读取每个元素才能确定和；设输入字符数 L，整体时间 O(L+n)，批量 read().split() 占 O(L) 输入存储；不另外保存整数数组或数组切片。")

    # 03: T fixed-size cases; include T=0 and awkward token wrapping.
    pair_groups = [[(2, 8), (-4, 9), (0, 0)], [], [(11, 22)], [(-7, -8)],
                   [(0, 5), (5, 0)], [(1, 2), (3, 4)], [(8, -8)] * 3,
                   [(1000000000, 1000000000), (-1000000000, 1)],
                   [(i, i + 1) for i in range(10)], [(i, -i) for i in range(7)],
                   [(31, 12), (-3, 18), (7, -2), (9, 9)], [(0, 0)],
                   [(-1, 0)], [(0, -1)], [(100, 200), (300, 400)],
                   [(99, 1), (101, -1)], [(-40, -60), (50, -50)],
                   [(2, 2)] * 20, [(19, 23), (29, 31), (37, 41)],
                   [(1234, 5678)], [(5, 17), (9, -3), (-11, 4)], [(42, 42)] * 4]
    cases = []
    for i, group in enumerate(pair_groups):
        values = [str(len(group))] + [str(x) for pair in group for x in pair]
        stdin = [" ", "\n", "\t"][i % 3].join(values) + ("\n" if i % 2 else "")
        cases.append((stdin, lines([a + b for a, b in group])))
    add(3, "先读 T：多组两数之和", "acm-io-test-count",
        "输入开头给出测试组数 T。接下来每组包含两个整数，分别输出每组的和。先确定要处理多少组，再重复相同的读取和计算流程。",
        "第一个整数为 T。随后是 T 组数据，每组恰好两个整数 a、b。整数以空白分隔，组的边界由每组两个数确定。",
        "按照输入顺序输出 T 行，每行是对应组的 a+b。T=0 时不输出任何内容。",
        ["0 ≤ T ≤ 10000", "每个整数的绝对值不超过 10^9"],
        ["T 不是第一组的数字。", "每次循环读取两个数，一共循环 T 次。", "0 0 也是正常的一组，应该输出 0。"],
        [example("3\n2 8\n-4 9\n0 0\n", "10\n5\n0\n", "组数为 3，三个答案按原顺序各占一行。"),
         example("2 11\n22 -7 -8\n", "33\n-15\n", "按 token 分组：11、22 是第一组，-7、-8 是第二组。"),
         example("0\n", "", "T=0，没有测试组，也就没有输出行。")],
        cases, '''
        import sys

        def solve():
            tokens = iter(sys.stdin.buffer.read().split())
            t = int(next(tokens))
            for _ in range(t):
                a = int(next(tokens))
                b = int(next(tokens))
                print(a + b)

        if __name__ == "__main__":
            solve()
        ''', "先 next() 取得测试组数，然后循环 T 次，每次恰好再 next() 两次。记住：T 管次数，每组管数量。设输入字符数为 L，读取和转换 O(L)，处理 T 组 O(T)；批量 read().split() 保存输入 token，占 O(L) 空间，单组计算只保留两个整数；输出必须有 T 行。")

    # 04: EOF is the stop condition, including genuinely empty stdin.
    eof_groups = [[], [(6, 14)], [(0, 0)], [(1, 2), (3, 4)],
                  [(-5, 8), (10, -10), (0, 7)], [(1000000000, -1000000000)],
                  [(-1, -9)], [(0, 3), (0, 0), (4, 0)], [(2, 8)] * 3,
                  [(i, i * 2) for i in range(12)], [(9, 9), (8, 8)],
                  [(31, -2)], [(-7, 13), (-100, 1)], [(50, 60), (70, 80)],
                  [(9, 1), (8, 2), (7, 3)], [(-30, -40), (0, 0)],
                  [(11, 22), (33, 44), (55, 66)], [(999, 1)],
                  [(123456, 654321)], [(5, -5)] * 7, [(1, 0)], [(0, -1)]]
    cases = []
    for i, group in enumerate(eof_groups):
        if i == 0:
            stdin = ""
        elif i % 3 == 0:
            stdin = "\n\n" + "\n\n".join(f"{a} {b}" for a, b in group) + "\n\n"
        elif i % 3 == 1:
            stdin = "\t".join(str(x) for pair in group for x in pair)
        else:
            stdin = lines([f"{a} {b}" for a, b in group])
        cases.append((stdin, lines([a + b for a, b in group])))
    cases.append((" \n\t\n", ""))
    add(4, "读到 EOF：未知组数的两数之和", "acm-io-until-eof",
        "这次没有 T，也没有结束数字。输入中出现多少组整数，就处理多少组；直到标准输入结束（EOF）才停止。每组仍然恰好包含两个整数。",
        "零组或多组数据，每组为两个整数 a、b，以空白分隔。允许组间空行和末尾空白；非空输入的整数总数保证为偶数。",
        "按输入顺序，每组输出一行 a+b。空输入或只有空白的输入不输出任何内容。",
        ["0 至 10000 组数据", "每个整数的绝对值不超过 10^9"],
        ["EOF 表示输入结束，与读到数值 0 不同。", "空行仅是空白分隔，不表示一组，也不表示结束。", "最后一组可以没有末尾换行；0 0 仍须输出 0。"],
        [example("6 14\n-5 8\n", "20\n3\n", "没有组数，依次读到两组，再到 EOF。"),
         example("0 0\n\n4 0", "0\n4\n", "空行跳过，0 0 是正常数据，最后没有换行也应处理。"),
         example("", "", "从开始就是 EOF，没有结果需要输出。")],
        cases, '''
        import sys

        def solve():
            tokens = iter(sys.stdin.buffer.read().split())
            for first in tokens:
                a = int(first)
                b = int(next(tokens))
                print(a + b)

        if __name__ == "__main__":
            solve()
        ''', "read() 一次读到 EOF，split() 自动忽略空白；for 取每组第一个 token，next() 取第二个。空迭代器自然执行零次。记住：没有 T，就看到哪读到哪。设有 K 组、输入字符数 L，整体时间 O(L+K)，批量输入 token 占 O(L) 空间，当前一组只保留两个整数。")

    # 05: a sentinel is checked before calculating; suffix data is ignored.
    before_groups = [[(4, 9), (-3, 8)], [], [(0, 7)], [(7, 0)],
                     [(2, -2)], [(-5, -6)], [(1, 1), (2, 2)],
                     [(0, 1), (1, 0), (0, -2)], [(1000000000, 1000000000)],
                     [(-1000000000, 1)], [(i + 1, 10) for i in range(8)],
                     [(33, 44), (55, -66)], [(9, -9), (-9, 9)], [(10, 20)],
                     [(1, -3)] * 12, [(50, 51), (52, 53)], [(3, 7), (8, 12), (13, 17)],
                     [(999, 1)], [(5, 5), (0, 2)], [(-7, 0), (0, -8)],
                     [(123, 456)], [(81, 19), (90, 10), (100, 1)]]
    cases = []
    for i, group in enumerate(before_groups):
        suffix = [(700 + i, 900 - i)] if i % 2 else []
        values = [str(x) for pair in group + [(0, 0)] + suffix for x in pair]
        stdin = [" ", "\n", "\t"][i % 3].join(values) + ("\n" if i % 2 else "")
        cases.append((stdin, lines([a + b for a, b in group])))
    add(5, "哨兵结束：遇到 0 0 立即停止", "acm-io-sentinel",
        "逐组读取两个整数并输出它们的和。与上一题不同，当一整组恰好是 0 0 时，立即结束。这组是结束标记，不能产生输出；结束标记后即使还有整数，也不再处理。",
        "输入包含若干组整数 a、b，以空白分隔，保证至少出现一组 0 0。结束标记后的内容若存在，也是合法的整数对，但应忽略。",
        "只输出第一个 0 0 之前各组的和，每组一行。如果第一组就是 0 0，不输出任何内容。",
        ["结束标记前 0 至 10000 组数据", "整份输入最多 20001 个整数对，包含结束标记及标记后的数据", "每个整数的绝对值不超过 10^9"],
        ["必须两个数同时为 0 才结束；0 7、7 0 都是正常数据。", "先检查结束条件，再计算和，不能先输出 0。", "结束标记后的数据不参与任何输出。"],
        [example("4 9\n-3 8\n0 0\n", "13\n5\n", "两组结果之后读到结束标记，标记本身不输出。"),
         example("0 7\n7 0\n0 0\n", "7\n7\n", "只有一个零不满足结束条件。"),
         example("0 0\n99 1\n", "", "第一组就结束，后面的 99、1 完全忽略。")],
        cases, '''
        import sys

        def solve():
            tokens = iter(sys.stdin.buffer.read().split())
            for first in tokens:
                a = int(first)
                b = int(next(tokens))
                if a == 0 and b == 0:
                    break
                print(a + b)

        if __name__ == "__main__":
            solve()
        ''', "for 取每组第一个 token，next() 取第二个；先检查 a==0 and b==0，满足便 break，否则输出和。口诀：哨兵先判断，答案后输出。当前实现仍会批量 read().split() 读取整份输入，若字符数为 L，读取时间与输入空间均为 O(L)；标记前 K 组的计算为 O(K)，标记后的 token 不再转换或计算。")

    # 06: each n starts a new group; n=0 is an empty group, not a sentinel.
    variable_groups = [[[2, 5, -1], [], [8, 9]], [], [[]], [[4]], [[-7]],
                       [[1, 2], [3]], [[], [], []], [[0], [], [0, 0]],
                       [[1000000000, 1000000000], [-1000000000]],
                       [list(range(10)), [-1, 1]], [[6, -6], [8, -8], []],
                       [[17, 19, 23]], [[1] * 20], [[-1] * 21, []],
                       [[2, 4, 6, 8], [10, 12]], [[99, 1], [], [-50, 50]],
                       [[], [1], [], [2], []], [[5, 9], [12, -4], [3, 8]],
                       [[31, 41, 59, 26]], [[123, -23, 100], [7]],
                       [list(range(-10, 11))], [[0] * 30, [9, 0]]]
    cases = []
    for i, groups in enumerate(variable_groups):
        values = [str(x) for group in groups for x in [len(group)] + group]
        stdin = [" ", "\n", "\t"][i % 3].join(values)
        if i % 2 and values:
            stdin += "\n"
        cases.append((stdin, lines([sum(group) for group in groups])))
    cases.append((" \n\n", ""))
    add(6, "变长分组：每组先给 n，直到 EOF", "acm-io-variable-groups",
        "输入由多组长度不同的数组组成。每组先给长度 n，再给这组的 n 个整数。输出每组的总和，读完一组后再读下一组的长度，直到 EOF。",
        "零组或多组数据。每组依次包含一个非负整数 n 和恰好 n 个整数。所有数以空白分隔，可以跨行。n=0 是一个合法的空数组组；之后仍可能有下一组。",
        "每组输出一行元素之和，空数组组输出 0。没有任何组时不输出。",
        ["0 至 10000 组", "每组 0 ≤ n ≤ 100000，总元素数不超过 100000", "元素绝对值不超过 10^9"],
        ["此题的 0 不是哨兵，长度为 0 也算一组。", "读过一组的 n 个元素之后，下一个 token 才是新长度。", "组边界取决于 n，与换行位置无关。"],
        [example("3 2 5 -1\n0\n2 8 9\n", "6\n0\n17\n", "三组的长度分别为 3、0、2；空组也输出一行 0。"),
         example("2\n6\n-6 1\n9", "0\n9\n", "先取长度 2 和两个元素，再取长度 1 和一个元素。"),
         example("", "", "没有组长度，因此不输出。")],
        cases, '''
        import sys

        def solve():
            tokens = iter(sys.stdin.buffer.read().split())
            for length in tokens:
                n = int(length)
                total = sum(int(next(tokens)) for _ in range(n))
                print(total)

        if __name__ == "__main__":
            solve()
        ''', "for 每次取得新组的长度，再 next() 恰好取 n 个元素求和；同一个迭代器已前进到下一组。n=0 时零次取元素，sum 得到 0，然后继续。记住：先长度，再 n 项，直到 EOF。设 K 组、总元素 M、字符数 L，时间 O(L+M+K)，批量 token 输入占 O(L) 空间；不另外保存每组整数数组。")

    # 07: matrix grouping uses dimensions, not incidental line wrapping.
    matrices = [[[1, 2, 3], [-4, 5, 6]], [[9]], [[0]], [[-8]],
                [[1, 2, 3, 4]], [[1], [2], [3]], [[0, 0], [0, 0]],
                [[5, -5], [7, -7]], [[1000000000] * 3], [[-1000000000] * 2],
                [[1, 3], [5, 7], [9, 11]], [[1, -2, 3], [-4, 5, -6], [7, -8, 9]],
                [list(range(10))], [[i] for i in range(8)], [[10, 20], [30, 40]],
                [[31, 41, 59, 26], [53, 58, 97, 93]], [[99, 1, -100]],
                [[2, 4, 6], [8, 10, 12], [14, 16, 18], [20, 22, 24]],
                [[0, 8, 0, 9]], [[-1, -2], [-3, -4]], [[1] * 12 for _ in range(3)],
                [[123, -23], [200, -100], [0, 100]]]
    cases = []
    for i, matrix in enumerate(matrices):
        rows, cols = len(matrix), len(matrix[0])
        values = [str(rows), str(cols)] + [str(x) for row in matrix for x in row]
        stdin = [" ", "\n", "\t"][i % 3].join(values) + ("\n" if i % 2 else "")
        cases.append((stdin, lines([sum(row) for row in matrix])))
    add(7, "二维矩阵：按 r×c 读取并输出各行和", "acm-io-matrix",
        "读取一个 r 行 c 列的整数矩阵，按从上到下的顺序输出每行的元素总和。重点是识别两个维度，读取 r×c 个元素，并按每行 c 个元素分组。",
        "前两个整数是 r、c，之后恰好 r×c 个整数按行优先顺序给出：先第一行，再第二行，依此类推。整数以空白分隔，物理换行不保证与矩阵行边界一致。",
        "输出 r 行。第 i 行为矩阵第 i 行全部 c 个元素的和。",
        ["1 ≤ r,c ≤ 1000，r×c ≤ 100000", "矩阵元素绝对值不超过 10^9"],
        ["r 和 c 是维度，不是矩阵元素。", "每 c 个元素构成一行，即使输入在任意位置换行也应如此分组。", "输出的是每行的和，共 r 行；不输出矩阵总和或列和。"],
        [example("2 3\n1 2 3\n-4 5 6\n", "6\n7\n", "第一行 1+2+3=6，第二行 -4+5+6=7。"),
         example("3 1\n1 2 3\n", "1\n2\n3\n", "矩阵有三行，每行一列；输入写成一行也仍输出三个结果。"),
         example("1 4\n5\n-5 8\n2", "10\n", "这是一个只有一行的矩阵，四个元素的和为 10。")],
        cases, '''
        import sys

        def solve():
            tokens = iter(sys.stdin.buffer.read().split())
            rows = int(next(tokens))
            columns = int(next(tokens))
            for _ in range(rows):
                total = sum(int(next(tokens)) for _ in range(columns))
                print(total)

        if __name__ == "__main__":
            solve()
        ''', "先 next() 两次取得 rows、columns，外层重复 rows 次，每次恰好 next() 读取 columns 个元素并求和。口诀：先维度，后元素；每 c 项，算一行。每个矩阵元素必须读取，设字符数 L，时间 O(L+rc)，批量输入 token 占 O(L) 空间；不另外建立矩阵或行切片。")

    # 08: string fixtures preserve literal whitespace and Unicode code points.
    texts = [["  hello  ", "", "你好 世界"], [], [""], ["a"], [" "],
             ["   "], [" hello"], ["hello "], ["a  b   c"], ["中文"],
             ["🙂"], ["🙂 汉字 A"], ["[inside]", "123"], ["", "", ""],
             ["front ", " middle ", " tail"], ["\tA\t"], ["a", "b", "c"],
             ["0", "0 0"], ["CASE #1: 7"], ["line one", "line two"],
             ["x" * 100], ["  世界🙂  ", "", "끝"], ["last line without LF"]]
    cases = []
    for i, records in enumerate(texts):
        stdin = str(len(records)) + "\n" + "\n".join(records)
        if records and (i != len(texts) - 1):
            stdin += "\n"
        expected = lines([value for text in records for value in (len(text), "[" + text + "]")])
        cases.append((stdin, expected))
    cases.append(("2\r\n  A  \r\n\r\n", "5\n[  A  ]\n0\n[]\n"))
    add(8, "读完整一行：保留空格、空行与文字", "acm-io-full-text-lines",
        "先读文字行数 N，再读 N 行原文。对每行输出它的长度和带方括号的原文。这里空格、制表符和空行都是数据的一部分，不能使用 split() 或 strip() 破坏原文。",
        "第一行是整数 N。接下来恰好 N 行文字，可含前导、尾随或连续空格，也可为空行。文字不含换行字符；换行符为 LF 或 CRLF，非空的最后一行可以没有末尾换行。",
        "每条原文输出两行：第一行是长度，按 Python len(text) 的 Unicode 码点个数计算；第二行是 [原文]，方括号内部必须完整保留原文。N=0 时不输出。",
        ["0 ≤ N ≤ 1000", "每行 0 至 10000 个 Unicode 码点，总码点数不超过 100000", "输入采用 UTF-8；换行符不计入长度"],
        ["只去除行尾换行符，不去除首尾空格或制表符。", "空行是长度为 0 的记录，输出 0 和 [] 两行。", "汉字和示例中的单码点 emoji 各计 1；组合字符按各码点分别计数，而非显示宽度。", "需要 N 条记录；表示最后一条空记录时，输入仍应提供对应的空行换行符。"],
        [example("3\n  hello  \n\n你好 世界\n", "9\n[  hello  ]\n0\n[]\n5\n[你好 世界]\n", "hello 两侧各两个空格，长度为 9；空行长度为 0；中文记录含 5 个码点。"),
         example("2\n🙂\na  b", "1\n[🙂]\n4\n[a  b]\n", "emoji 计 1，a 与 b 之间两个空格必须保留；末行没有换行也合法。"),
         example("0\n", "", "没有文字记录，不输出长度或方括号。")],
        cases, r'''
        import sys

        def solve():
            n = int(sys.stdin.readline())
            for _ in range(n):
                text = sys.stdin.readline().removesuffix('\n').removesuffix('\r')
                print(len(text))
                print('[' + text + ']')

        if __name__ == "__main__":
            solve()
        ''', "逐行读取，只移除末尾 LF，再移除 CR；保留一切属于原文的空白。每行输出 len(text) 和 '['+text+']'。记忆：数字题按词，原文题按行；去换行，不去空格。总输入字符数 L，读取和输出时间 O(L+N)，一次保存最长行长度 M 的文本，辅助空间 O(M)。")

    # 09: commas are structural, not whitespace; expected sorting is mathematical.
    csv_arrays = [[7, -2, 7, 0], [9], [-4], [0], [3, 1, 2], [1, 1, 1],
                  [-3, -1, -2], [5, -5], [0, 2, 0, -2],
                  [1000000000, -1000000000, 0], list(range(10, -1, -1)),
                  [31, 41, 59, 26], [8, 8, -8, -8], [100, 20, 3],
                  [-100, -20, -3], [1, 10, 2, 20], [99, 1], [0] * 20,
                  [9, 7, 5, 3, 1], [2, 4, 6, 8], [123, -23, 100, 7],
                  [17, 19, 23, 11, 13]]
    cases = []
    for i, values in enumerate(csv_arrays):
        separator = [",", " , ", "\t,\t"][i % 3]
        stdin = separator.join(map(str, values))
        if i % 2:
            stdin = "  " + stdin + " \n"
        cases.append((stdin, lines([",".join(map(str, sorted(values)))])))
    add(9, "逗号分隔：排序并按指定格式输出", "acm-io-comma-separated",
        "输入一行逗号分隔的整数，将所有整数按从小到大排序，再用逗号连接输出。此题练习指定分隔符的读取，以及输出格式中标点和空格的精确控制。",
        "一行包含至少一个整数，相邻整数用英文逗号 , 分隔。数字及逗号两侧可有空格或制表符；不出现连续逗号、首尾逗号或空字段。",
        "输出排序后的整数，占一行，用英文逗号连接，逗号两侧不能有空格。重复整数保留。",
        ["1 至 100000 个整数", "每个整数的绝对值不超过 10^9"],
        ["应按逗号 split(',')，不能只按空格 split()。", "先转 int 再排序，避免把 100 放在 20 前面的字符串顺序错误。", "输出用 ','.join(...)，不添加方括号、尾随逗号或空格。"],
        [example("7,-2,7,0\n", "-2,0,7,7\n", "按数值排序，两个 7 都保留。"),
         example(" 100 , 20 , 3 \n", "3,20,100\n", "输入允许空格，输出统一为没有空格的逗号格式。"),
         example("-4", "-4\n", "只有一个整数时直接输出该整数，没有逗号。")],
        cases, '''
        import sys

        def solve():
            values = [int(part) for part in sys.stdin.read().split(',')]
            values.sort()
            print(','.join(map(str, values)))

        if __name__ == "__main__":
            solve()
        ''', "先按逗号拆分，int 自动接受字段两侧空白，排序后用 join 精确连接。口诀：逗号拆，整数排，逗号连。设 n 个数、L 个输入字符，读取转换 O(L)，比较排序 O(n log n)，输入与排序存储 O(L+n)；通用比较排序方案适合题目范围。")

    # 10: expected rounding uses exact rational arithmetic, independent of Decimal.
    decimal_groups = [["1.25", "2.50", "3.75"], ["1.005"], ["-1.005"],
                      ["0"], ["-0.0001"], ["2.675"], ["-2.675"],
                      ["1", "2"], ["1", "2", "2"], ["0.0049"], ["0.005"],
                      ["-0.005"], ["999999999.995"], ["1000000000", "-1000000000"],
                      ["0.1", "0.2", "0.3"], ["-1.25", "2.75"],
                      ["3.141592", "2.718281"], ["12.345", "12.345"],
                      ["-12.345", "-12.345"], ["7"] * 20,
                      ["0.000001", "-0.000002"], ["10", "11", "12", "13"],
                      ["1.004999"], ["1.005001"], ["-0.004999"],
                      ["999999999.999999", "999999999.999998", "999999999.999997"]]
    cases = []
    for i, values in enumerate(decimal_groups):
        mean = sum((Fraction(value) for value in values), Fraction()) / len(values)
        scaled = abs(mean) * 100
        whole, remainder = divmod(scaled.numerator, scaled.denominator)
        if 2 * remainder >= scaled.denominator:
            whole += 1
        sign = "-" if mean < 0 and whole else ""
        expected = f"{sign}{whole // 100}.{whole % 100:02}\n"
        stdin = str(len(values)) + ["\n", " ", "\t"][i % 3] + " ".join(values)
        if i % 2:
            stdin += "\n"
        cases.append((stdin, expected))
    add(10, "小数输出：平均值保留两位，明确舍入规则", "acm-io-decimal-format",
        "读取 N 个十进制数，输出它们的平均值，固定保留两位小数。舍入使用 ROUND_HALF_UP：恰好处在两个百分位数中间时，向远离零的方向取整。不要依赖二进制 float 的默认舍入行为。",
        "第一个整数为 N，之后恰好 N 个十进制数，以空白分隔。每个数采用普通十进制写法，可为整数或带小数点的数，不使用指数记法。",
        "输出平均值，占一行，恰好两位小数，按 ROUND_HALF_UP 舍入。例如 1.005 输出 1.01，-1.005 输出 -1.01。若舍入结果是零，统一输出 0.00，不输出 -0.00。",
        ["1 ≤ N ≤ 10000", "每个数的绝对值不超过 10^9，最多 6 位小数"],
        ["N 必须至少为 1，不能对空数组计算平均值。", "固定两位表示 7 也要输出 7.00。", "ROUND_HALF_UP 与 Python round 的默认规则不同，负数的中间值也向远离零方向舍入。", "Decimal 应从输入字符串构造，避免先转 float 引入误差。"],
        [example("3\n1.25 2.50 3.75\n", "2.50\n", "平均值为 2.5，固定两位后写成 2.50。"),
         example("1\n-1.005\n", "-1.01\n", "负数中间值按 HALF_UP 规则向远离零方向舍入。"),
         example("1\n-0.0001\n", "0.00\n", "舍入到百分位得到零，需要去除负零符号。")],
        cases, '''
        import sys
        from decimal import Decimal, ROUND_HALF_UP, getcontext

        def solve():
            getcontext().prec = 40
            tokens = sys.stdin.read().split()
            n = int(tokens[0])
            total = sum((Decimal(token) for token in tokens[1:1 + n]), Decimal(0))
            mean = (total / Decimal(n)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if mean == 0:
                mean = abs(mean)
            print(format(mean, '.2f'))

        if __name__ == "__main__":
            solve()
        ''', "用 Decimal(字符串) 保留输入的十进制含义，40 位精度覆盖题目范围，求和除以 N 后 quantize 到 0.01，明确指定 ROUND_HALF_UP，最后规范负零并固定两位。口诀：字符串入 Decimal，规则定舍入，格式补两位。设字符数 L，在本题有界数位下时间 O(L+N)，批量输入空间 O(L+N)。")

    # 11: T tells case count; every case supplies its own array length.
    labeled_groups = [[[4, 6, -1], []], [], [[8]], [[-8]], [[0]],
                      [[1, 2], [3, 4]], [[], [], []], [[9], [], [10, -10]],
                      [[1000000000] * 3], [[-1000000000] * 2, [1]],
                      [list(range(10)), list(range(-5, 6))], [[17, 19, 23]],
                      [[1] * 20, [-1] * 15], [[2, 4, 6, 8], [10]],
                      [[31, 41, 59, 26], [53, 58]], [[99, 1], [], [0]],
                      [[5], [6], [7], [8], [9]], [[0] * 40],
                      [[123, -23, 100], [7, -7]], [[], [0], []],
                      [[-10, 20], [30, -40], [50, -60]], [[1, 3, 5, 7, 9]]]
    cases = []
    for i, groups in enumerate(labeled_groups):
        values = [str(len(groups))] + [str(x) for group in groups for x in [len(group)] + group]
        stdin = [" ", "\n", "\t"][i % 3].join(values) + ("\n" if i % 2 else "")
        expected = lines([f"Case #{index}: {sum(group)}" for index, group in enumerate(groups, 1)])
        cases.append((stdin, expected))
    add(11, "Case 标签：多组变长数组与编号输出", "acm-io-case-labels",
        "先读取测试组数 T，每组再读取数组长度 n 和 n 个元素，求每组总和。输出必须带从 1 开始的 Case 编号，练习嵌套输入协议和精确的标签格式。",
        "第一个整数为 T。接下来 T 组：每组先给 n，再给 n 个整数。所有数字以空白分隔；n=0 代表空数组组。",
        "每组输出一行 Case #i: S，其中 i 是从 1 开始的组号，S 为该组元素和。冒号后恰好一个空格，Case 与 # 之间也恰好一个空格。T=0 时不输出。",
        ["0 ≤ T ≤ 10000", "每组 0 ≤ n ≤ 100000，总元素数不超过 100000", "元素绝对值不超过 10^9"],
        ["T 是总组数，n 是当前组长度，两者职责不同。", "数组长度与组号不参加求和。", "严格输出 Case #1: ...；不能从 Case #0 开始，也不能写成 case 或多加空格。", "空数组仍占一个 Case 编号，并输出总和 0。"],
        [example("2\n3 4 6 -1\n0\n", "Case #1: 9\nCase #2: 0\n", "两组长度为 3 和 0，编号从 1 开始。"),
         example("3 1 8 2 -3 5 1 0", "Case #1: 8\nCase #2: 2\nCase #3: 0\n", "没有按组换行也能按长度读取，输出仍是一组一行。"),
         example("0\n", "", "没有测试组，不输出任何 Case 标签。")],
        cases, '''
        import sys

        def solve():
            tokens = iter(sys.stdin.buffer.read().split())
            t = int(next(tokens))
            for case in range(1, t + 1):
                n = int(next(tokens))
                total = sum(int(next(tokens)) for _ in range(n))
                print(f'Case #{case}: {total}')

        if __name__ == "__main__":
            solve()
        ''', "外层用 T 管组数，每组先 next() 取 n，再取恰好 n 项；迭代器自动前进到下一组，格式字符串保证标签和编号准确。口诀：T 管组，n 管项，Case 从一编号。设总元素 M、字符数 L，时间 O(L+M+T)，批量输入 token 占 O(L) 空间；单组不保存额外数组。")

    # 12: each physical nonblank line is one independent group.
    row_groups = [[[3, 5, -2], [9], [0]], [], [[0]], [[-4]], [[1, 2]],
                  [[1], [2], [3]], [[5, -5], [7, -7]], [[0, 0, 0]],
                  [[1000000000] * 3], [[-1000000000] * 2],
                  [list(range(10)), [10, 20]], [[31, 41, 59, 26]],
                  [[1] * 20, [-1] * 20], [[2, 4, 6], [8, 10, 12]],
                  [[99, 1], [0], [-50, 50]], [[123, -23, 100]],
                  [[1, 3, 5, 7, 9], [2, 4, 6, 8]], [[8], [], [9]],
                  [[0], [0]], [[-7, 0], [0, -8]], [[17, 19, 23], [29]],
                  [[100, -100], [100, -99]]]
    cases = []
    for i, rows in enumerate(row_groups):
        formatted = [[" ", "\t", "  "][i % 3].join(map(str, row)) for row in rows]
        if i == 1:
            stdin = ""
        elif i % 3 == 0:
            stdin = "\n \t\n" + "\n\n".join(formatted) + "\n\n"
        else:
            stdin = "\n".join(formatted) + ("\n" if i % 2 else "")
        cases.append((stdin, lines([sum(row) for row in rows if row])))
    cases.append(("\n \t \n\n", ""))
    add(12, "按行分组到 EOF：每行整数个数未知", "acm-io-line-groups",
        "输入中每个有内容的物理行是一组，该行可能有一个或多个整数。逐行求和，直到 EOF。这里换行承担分组作用，不能把整个文件直接 split 后当成一组。空行或只有空白的行应跳过。",
        "零行或多行数据。每个非空白行有至少一个整数，以空格或制表符分隔。允许空白行，最后一个非空白行不一定以换行结束。",
        "每个非空白输入行输出一行整数总和，顺序不变。空白行不输出；只有空输入或空白行时不输出任何内容。",
        ["0 至 10000 个非空白行，总整数个数不超过 100000", "每个整数绝对值不超过 10^9"],
        ["行内按空白拆分，行间不能合并。", "空白行应跳过，不应输出 0；包含数字 0 的行则要输出 0。", "没有 T、n 或哨兵，只根据物理行和 EOF 处理。"],
        [example("3 5 -2\n9\n0\n", "6\n9\n0\n", "三个物理行各为一组，元素个数分别为 3、1、1。"),
         example("\n1 2\n \t \n5 -5", "3\n0\n", "空白行跳过，两个有数字的行分别输出；末行无换行也处理。"),
         example(" \n\t\n", "", "虽然有换行，但没有任何整数记录，因此不输出。")],
        cases, '''
        import sys

        def solve():
            for line in sys.stdin:
                tokens = line.split()
                if not tokens:
                    continue
                print(sum(map(int, tokens)))

        if __name__ == "__main__":
            solve()
        ''', "用 for line in sys.stdin 逐行直到 EOF，line.split() 得到当前行的整数，空列表就 continue，其余求和。记住：一行一组，空行跳过；0 是数据，EOF 才结束。总字符数 L、整数数 M，时间 O(L+M)，只保留当前行，空间 O(最长行字符数及其 token 数)。")

    assert [problem["id"] for problem in PROBLEMS] == list(range(10001, 10013))
    assert all(problem["compare"] == "exact" for problem in PROBLEMS)
    target = ROOT / "catalog" / "io_basics.json"
    target.write_text(json.dumps(PROBLEMS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(PROBLEMS)} I/O exercises and {sum(len(p['tests']) for p in PROBLEMS)} fixed tests.")


if __name__ == "__main__":
    build()
