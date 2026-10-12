#!/usr/bin/env python3
"""Author reproducible fixed fixtures using small, independent specification oracles.

No reference solution is executed or used to derive expectations. Generated JSON
is committed and loaded as data only. Exhaustive input domains (#22, #51) are
fully covered; other problems receive at least 20 distinct inputs in total.
"""
import importlib.util
import itertools as it
import json
import math
from collections import Counter, OrderedDict, deque
from functools import lru_cache
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]


def base_problems():
    result = {}
    for path in sorted((ROOT / 'catalog').glob('part_*.py')):
        spec = importlib.util.spec_from_file_location('author_' + path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result.update({p['id']: p for p in module.PROBLEMS})
    return result


def line(values):
    return ' '.join(map(str, values)) + '\n'


def array(values, *params):
    return line([len(values), *params]) + line(values)


def boolean(value):
    return 'true\n' if value else 'false\n'


def collection(records):
    records = list(records)
    return str(len(records)) + '\n' + ''.join(line(record) if record else '-\n' for record in records)


def intervals(values):
    return [values[a:b] for a in range(len(values)) for b in range(a + 1, len(values) + 1)]


def subsets(values):
    return [tuple(v for i, v in enumerate(values) if mask >> i & 1) for mask in range(1 << len(values))]


def node(value, left=None, right=None):
    return [value, left, right]


def serialize(tree):
    queue, tokens = deque([tree]), []
    while queue:
        current = queue.popleft()
        if current is None:
            tokens.append('null')
        else:
            tokens.append(str(current[0])); queue.extend(current[1:])
    while len(tokens) > 1 and tokens[-1] == 'null':
        tokens.pop()
    return line(tokens)


def tree_input(tree):
    text = serialize(tree)
    return str(len(text.split())) + '\n' + text


def nodes(tree):
    if tree is None:
        return []
    return [tree] + nodes(tree[1]) + nodes(tree[2])


def traversal(tree, order):
    if tree is None:
        return []
    left, right = traversal(tree[1], order), traversal(tree[2], order)
    return {'pre': [tree[0]] + left + right, 'in': left + [tree[0]] + right}[order]


def levels(tree):
    current, result = [tree] if tree else [], []
    while current:
        result.append([x[0] for x in current])
        current = [child for parent in current for child in parent[1:] if child is not None]
    return result


def random_tree(rng, size, unique=False):
    if size == 0:
        return None
    values = rng.sample(range(-50, 51), size) if unique else [rng.randint(-8, 8) for _ in range(size)]
    root = node(values[0]); slots = [(root, 1), (root, 2)]
    for value in values[1:]:
        parent, side = slots.pop(rng.randrange(len(slots)))
        child = node(value); parent[side] = child; slots.extend([(child, 1), (child, 2)])
    return root


def balanced(values):
    if not values:
        return None
    middle = (len(values) - 1) // 2
    return node(values[middle], balanced(values[:middle]), balanced(values[middle + 1:]))


def mirror(tree):
    return None if tree is None else node(tree[0], mirror(tree[2]), mirror(tree[1]))


def tree_graph(tree):
    all_nodes = nodes(tree); ids = {id(n): i for i, n in enumerate(all_nodes)}
    graph = [[] for _ in all_nodes]
    for i, parent in enumerate(all_nodes):
        for child in parent[1:]:
            if child is not None:
                j = ids[id(child)]; graph[i].append(j); graph[j].append(i)
    return all_nodes, graph


def jumps(values):
    distance = {0: 0}; queue = deque([0])
    while queue:
        i = queue.popleft()
        for j in range(i + 1, min(len(values), i + values[i] + 1)):
            if j not in distance:
                distance[j] = distance[i] + 1; queue.append(j)
    return distance.get(len(values) - 1)


def valid_brackets(text):
    stack = []; pairs = {')': '(', ']': '[', '}': '{'}
    for char in text:
        if char in '([{': stack.append(char)
        elif not stack or stack.pop() != pairs[char]: return False
    return not stack


def case(pid, rng, attempt):
    """Return stdin, fixed answer, and a specific public example explanation."""
    a = [rng.randint(-5, 5) for _ in range(rng.randint(1, 10))]
    if attempt % 7 == 0: a = [0] * rng.randint(1, 10)
    if attempt % 7 == 1: a.sort()
    if attempt % 7 == 2: a.sort(reverse=True)
    n = len(a)
    source = array(a)
    reason = ''
    if pid == 1:
        if n < 2: a.append(rng.randint(-5, 5)); n = len(a)
        i, j = rng.sample(range(n), 2); target = a[i] + a[j]
        source, answer = array(a, target), line([i, j])
        reason = '下标 %d 和 %d 对应的值为 %d、%d，相加等于目标 %d；两个下标不同。' % (i, j, a[i], a[j], target)
    elif pid == 49:
        words = [rng.choice(['', 'a', 'ab', 'ba', 'abc', 'bca', 'cab', 'b', 'aa']) for _ in range(rng.randint(0, 10))]
        groups = {}
        for word in words: groups.setdefault(''.join(sorted(word)), []).append(word)
        source = str(len(words)) + '\n' + ''.join(w + '\n' for w in words)
        answer = str(len(groups)) + '\n' + ''.join(str(len(group)) + '\n' + ''.join(w + '\n' for w in group) for group in groups.values())
        reason = '按每种字母的出现次数分组，共 %d 组；相同字符串的多次出现和空字符串都保留。' % len(groups)
    elif pid == 128:
        if attempt % 4 == 0: a = []
        unique = sorted(set(a)); best = run = 0; previous = None
        for value in unique: run = run + 1 if previous is not None and value == previous + 1 else 1; best = max(best, run); previous = value
        source, answer = array(a), str(best) + '\n'; reason = '把不同数值按大小看作连续整数段，最长一段有 %d 个不同整数，重复值不计入长度。' % best
    elif pid == 283:
        result = [v for v in a if v != 0] + [0] * a.count(0)
        answer = line(result); reason = '保留非零元素的原有顺序，再把 %d 个零放到末尾。' % a.count(0)
    elif pid in (11, 42, 84, 121):
        a = [abs(x) for x in a]
        if pid == 11 and len(a) < 2: a.append(0)
        if pid == 11: value = max((j-i)*min(a[i],a[j]) for i in range(len(a)) for j in range(i+1,len(a)))
        elif pid == 42: value = sum(max(0, min(max(a[:i+1]),max(a[i:]))-a[i]) for i in range(len(a)))
        elif pid == 84: value = max(len(part)*min(part) for part in intervals(a))
        else: value = max([0]+[a[j]-a[i] for i in range(len(a)) for j in range(i+1,len(a))])
        source, answer = array(a), str(value)+'\n'
        reason = {11:'逐一比较两根竖线形成的容器，最大宽度与有效高度乘积为 %d。',42:'每个位置仅累加左右挡板都能拦住的水，合计 %d 个单位。',84:'枚举连续柱子区间，矩形高度受区间最矮柱子限制，最大面积为 %d。',121:'只允许在较早的日子买入、较晚的日子卖出；最优收益为 %d，负收益可以通过不交易避免。'}[pid] % value
    elif pid in (15, 53, 560, 152):
        if pid == 15:
            if attempt % 5 == 0: a = []
            result = sorted({tuple(sorted(t)) for t in it.combinations(a,3) if sum(t)==0})
            source, answer = array(a), collection(result); reason = '从不同位置取三个数，去掉数值相同的重复组合后共有 %d 组，顺序不影响答案。' % len(result)
        elif pid == 53:
            value = max(map(sum, intervals(a))); answer = str(value)+'\n'; reason = '只比较非空连续子数组，最大元素和为 %d；全负数时也不能选择空数组。' % value
        elif pid == 560:
            target = rng.randint(-6,6); value = sum(sum(part)==target for part in intervals(a)); source, answer = array(a,target),str(value)+'\n'; reason = '按起点和终点区分子数组，和为 %d 的非空连续区间共有 %d 个。' % (target,value)
        else:
            value=max(math.prod(part) for part in intervals(a));answer=str(value)+'\n';reason='负数相乘可能变为正数，零会中断乘积；全部非空连续区间中的最大乘积为 %d。'%value
    elif pid in (3, 438, 76, 5, 32, 20, 1143, 72):
        alphabet = 'ab AB' if pid == 3 else '()[]{}' if pid == 20 else '()' if pid == 32 else 'ab'
        s = ''.join(rng.choice(alphabet) for _ in range(rng.randint(0 if pid in (3,20,32,1143,72,76,438) else 1, 9 if pid != 72 else 4)))
        source = s+'\n'
        if pid == 3: value=max([0]+[len(t) for t in intervals(s) if len(set(t))==len(t)]);answer=str(value)+'\n';reason='子串必须连续，且其中每个字符最多出现一次；最长长度为 %d，空格也算字符。'%value
        elif pid == 20: value=valid_brackets(s);answer=boolean(value);reason='逐个匹配最近尚未闭合的同类型左括号；'+('全部正确匹配，输出 true。' if value else '存在类型、嵌套顺序或数量不匹配，输出 false。')
        elif pid == 32: value=max([0]+[len(t) for t in intervals(s) if valid_brackets(t)]);answer=str(value)+'\n';reason='只取连续、完整匹配的圆括号片段，最长合法片段长度为 %d。'%value
        elif pid == 5:
            answer=max((t for t in intervals(s) if t==t[::-1]),key=len)+'\n';reason='最长连续回文子串长度为 %d；若另一个回文串同样长，也可作为正确输出。'%len(answer.strip())
        else:
            t=''.join(rng.choice('ab') for _ in range(rng.randint(1 if pid==438 else 0,4 if pid==72 else 7)));source=s+'\n'+t+'\n'
            if pid == 438:
                positions=[i for i in range(len(s)-len(t)+1) if Counter(s[i:i+len(t)])==Counter(t)];answer=str(len(positions))+'\n'+line(positions);reason='只比较长度等于第二行的窗口；字母计数一致的起点有 %d 个，使用从 0 开始的下标。'%len(positions)
            elif pid == 76:
                candidates=[x for x in intervals(s) if all(Counter(x)[ch]>=count for ch,count in Counter(t).items())];value=min(candidates,key=len) if t and candidates else '';answer=value+'\n';reason='必须覆盖第二行每个字符的全部出现次数；'+('最短覆盖长度为 %d。'%len(value) if value else '目标为空或没有覆盖方案，所以输出空行。')
            elif pid == 1143:
                common=set(''.join(x) for x in subsets(s)) & set(''.join(x) for x in subsets(t));value=max(map(len,common));answer=str(value)+'\n';reason='可以删除字符但不能改变相对顺序，两串共同保留的最长序列有 %d 个字符。'%value
            else:
                queue=deque([(s,0)]);seen={s};limit=max(len(s),len(t))
                while queue:
                    text,distance=queue.popleft()
                    if text==t: value=distance;break
                    edits={text[:i]+text[i+1:] for i in range(len(text))}
                    edits.update(text[:i]+ch+text[i+1:] for i in range(len(text)) for ch in 'ab')
                    if len(text)<limit: edits.update(text[:i]+ch+text[i:] for i in range(len(text)+1) for ch in 'ab')
                    for new in edits-seen: seen.add(new);queue.append((new,distance+1))
                answer=str(value)+'\n';reason='每次插入、删除或替换一个字符都算一步；最短编辑过程需要 %d 步。'%value
    elif pid == 239:
        k=rng.randint(1,n);values=[max(a[i:i+k]) for i in range(n-k+1)];source,answer=array(a,k),line(values);reason='窗口宽度为 %d，共产生 %d 个窗口，逐个取最大值；相等元素仍可留在不同窗口内。'%(k,len(values))
    elif pid == 56:
        pairs=[sorted([rng.randint(-5,5),rng.randint(-5,5)]) for _ in range(rng.randint(0,8))];groups=[]
        for pair in pairs:
            overlaps=[g for g in groups if pair[0]<=g[1] and g[0]<=pair[1]]
            while overlaps:
                groups=[g for g in groups if g not in overlaps];pair=[min([pair[0]]+[g[0] for g in overlaps]),max([pair[1]]+[g[1] for g in overlaps])];overlaps=[g for g in groups if pair[0]<=g[1] and g[0]<=pair[1]]
            groups.append(pair)
        source=str(len(pairs))+'\n'+''.join(line(x) for x in pairs);answer=collection(sorted(groups));reason='闭区间重叠或端点相接都合并，最后剩 %d 个互不相交的区间。'%len(groups)
    elif pid == 189:
        k=rng.choice([0,n,n+1,1000000000,rng.randint(1,30)]);shift=k%n;result=a[-shift:]+a[:-shift] if shift else a;source,answer=array(a,k),line(result);reason='右移 %d 位等价于右移 %d 位；末尾这部分按原有顺序移到数组开头。'%(k,shift)
    elif pid == 238:
        if n<2:a.append(0)
        source,answer=array(a),line([math.prod(a[:i]+a[i+1:]) for i in range(len(a))]);reason='每个位置乘上除自己之外的所有数；一个零或多个零会使对应答案不同，不能用总乘积直接相除。'
    elif pid == 41:
        if attempt%5==0:a=[]
        value=next(x for x in range(1,len(a)+2) if x not in a);source,answer=array(a),str(value)+'\n';reason='只检查正整数，%d 之前的正整数都已出现，而 %d 没有出现。'%(value,value)
    elif pid in (73,54,48,240,74,64):
        m,n=rng.randint(1,5),rng.randint(1,5)
        if pid==48:n=m
        grid=[[rng.randint(0,8) if pid==64 else rng.randint(-3,3) for _ in range(n)] for _ in range(m)]
        if pid in (240,74):
            if pid==240:grid=[[r*2+c*3-8 for c in range(n)] for r in range(m)]
            else:
                values=sorted(rng.sample(range(-30,31),m*n));grid=[values[r*n:(r+1)*n] for r in range(m)]
            target=rng.choice([rng.choice(rng.choice(grid)),rng.randint(-35,35)]);source=line([m,n,target])+''.join(map(line,grid));answer=boolean(any(target in row for row in grid));reason='目标值 %d %s于矩阵中；按题面所给的行列排序条件查找，不改变输入矩阵。'%(target,'存在' if answer.startswith('true') else '不存在')
        elif pid==48:
            source=str(m)+'\n'+''.join(map(line,grid));result=[[grid[m-1-c][r] for c in range(m)] for r in range(m)];answer=''.join(map(line,result));reason='原矩阵第 r 行第 c 列移到第 c 行第 n-1-r 列，方向是顺时针。'
        else:
            source=line([m,n])+''.join(map(line,grid))
            if pid==73:
                rows={r for r in range(m) for c in range(n) if grid[r][c]==0};cols={c for r in range(m) for c in range(n) if grid[r][c]==0};answer=''.join(line([0 if r in rows or c in cols else grid[r][c] for c in range(n)]) for r in range(m));reason='只由原矩阵中的零确定需要清空的行和列，新产生的零不继续传播。'
            elif pid==54:
                position=(0,0);directions=[(0,1),(1,0),(0,-1),(-1,0)];direction=0;seen=set();result=[]
                for _ in range(m*n):
                    r,c=position;seen.add(position);result.append(grid[r][c]);dr,dc=directions[direction];new=(r+dr,c+dc)
                    if not(0<=new[0]<m and 0<=new[1]<n) or new in seen:direction=(direction+1)%4;dr,dc=directions[direction];new=(r+dr,c+dc)
                    position=new
                answer=line(result);reason='从左上角向右出发，遇到边界或已访问位置就顺时针转弯，每个元素仅输出一次。'
            else:
                def costs(r,c):
                    if r==m-1 and c==n-1:return [grid[r][c]]
                    following=(costs(r+1,c) if r+1<m else [])+(costs(r,c+1) if c+1<n else [])
                    return [grid[r][c]+value for value in following]
                value=min(costs(0,0));answer=str(value)+'\n';reason='所有路径只向右或向下，包含起点与终点数字的最小总和为 %d。'%value
    elif pid in (35,34,33,153,4):
        if pid==4:
            b=sorted([rng.randint(-10,10) for _ in range(rng.randint(0,10))]);a=sorted(a if attempt%4 else []);
            if not a and not b:b=[0]
            values=sorted(a+b);size=len(values);value=(values[size//2]+values[(size-1)//2])/2;source=line([len(a),len(b)])+line(a)+line(b);answer=str(value)+'\n';reason='合并后共有 %d 个元素，取中间一个或两个的平均值，中位数为 %s。'%(size,value)
        else:
            a=sorted(a if pid==34 else set(a))
            if pid in (35,34) and attempt%5==0:a=[]
            if pid in (33,153):shift=rng.randrange(len(a));a=a[shift:]+a[:shift]
            target=rng.choice(a+[rng.randint(-8,8)]) if a else 0
            if pid==153:source,answer=array(a),str(min(a))+'\n';reason='循环位移只改变位置，不改变数值集合，最小值为 %d。'%min(a)
            elif pid==34:
                found=[i for i,v in enumerate(a) if v==target];source,answer=array(a,target),line([found[0],found[-1]] if found else [-1,-1]);reason='输出目标 %d 的首末下标；没有出现时两个位置都填 -1。'%target
            elif pid==35:source,answer=array(a,target),str(sum(v<target for v in a))+'\n';reason='目标前面有 %d 个更小元素，因此查找或插入的位置就是该数量。'%sum(v<target for v in a)
            else:source,answer=array(a,target),str(a.index(target) if target in a else -1)+'\n';reason='下标对应旋转后的当前数组，不是旋转前的有序数组；找不到时输出 -1。'
    elif pid in (136,169,75,31,287,215,347):
        if pid==136:
            unique=rng.randint(-100,100);others=rng.sample([v for v in range(-20,21) if v!=unique],rng.randint(0,8));a=[unique]+others*2;rng.shuffle(a);source,answer=array(a),str(unique)+'\n';reason='除 %d 只出现一次外，其他每个整数恰好出现两次。'%unique
        elif pid==169:
            majority=rng.randint(-5,5);a=[majority]*(n//2+1)+[rng.randint(-5,5) for _ in range(n-n//2-1)];rng.shuffle(a);source,answer=array(a),str(majority)+'\n';reason='%d 的出现次数严格超过数组长度的一半，不能把恰好一半当作多数。'%majority
        elif pid==75:
            a=[rng.randint(0,2) for _ in a];source,answer=array(a),line(sorted(a));reason='按 0、1、2 的顺序重排，三种值的出现次数保持不变。'
        elif pid==31:
            a=a[:6];ordered=sorted(set(it.permutations(a)));index=ordered.index(tuple(a));answer=line(ordered[(index+1)%len(ordered)]);source=array(a);reason='在不同排列的字典序中取紧邻的后一项；当前项最大时回到最小排列。'
        elif pid==287:
            n=rng.randint(1,15);duplicate=rng.randint(1,n);copies=rng.randint(2,n+1);others=rng.sample([v for v in range(1,n+1) if v!=duplicate],n+1-copies);a=[duplicate]*copies+others;rng.shuffle(a);source,answer=line([n])+line(a),str(duplicate)+'\n';reason='第一行 n=%d，数组实际有 %d 个数；只有 %d 出现多次（%d 次）。'%(n,n+1,duplicate,copies)
        elif pid==215:
            k=rng.randint(1,len(a));source,answer=array(a,k),str(sorted(a,reverse=True)[k-1])+'\n';reason='从大到小排名，重复值占用多个位置，第 %d 项是 %s。'%(k,answer.strip())
        else:
            freq=Counter(a);k=rng.randint(1,len(freq));chosen=sorted(freq,key=lambda v:(-freq[v],v))[:k];source,answer=array(a,k),line(chosen);reason='按出现次数选择 %d 个不同整数；临界频率并列时可任选，但更高频元素必须保留。'%k
    elif pid in (160,206,234,141,142,21,2,19,24,25,138,148,23):
        a=[rng.randint(0,9) if pid==234 else rng.randint(-8,8) for _ in range(rng.randint(0 if pid not in (19,) else 1,15))];source=array(a)
        if pid==160:
            b=[rng.randint(-2,2) for _ in range(rng.randint(0,8))];c=[rng.randint(-2,2) for _ in range(rng.randint(0,8))];source=line([len(a),len(b),len(c)])+line(a)+line(b)+line(c);answer=(str(c[0]) if c else 'null')+'\n';reason='第三段是两条链表共享的同一条后缀；'+('它的首结点值为 %d。'%c[0] if c else '共享段长度为 0，即使前缀值相同也不相交。')
        elif pid==206:answer=line(a[::-1]);reason='把 next 连接顺序反过来，新的头结点是原来的尾结点；空表仍输出空行。'
        elif pid==234:
            if attempt%2==0:a=a[:7]+a[:7][::-1];source=array(a)
            answer=boolean(a==a[::-1]);reason='比较全部结点值的正序和逆序，'+('完全相同，所以是回文。' if a==a[::-1] else '不完全相同，所以不是回文。')
        elif pid in (141,142):
            pos=rng.choice([-1]+list(range(len(a))));source+=str(pos)+'\n';answer=boolean(pos!=-1) if pid==141 else str(pos)+'\n';reason='尾结点'+('指向空，因此没有环。' if pos==-1 else '连接到原序列下标 %d 的结点，该结点就是环入口。'%pos)
        elif pid==21:
            b=sorted(rng.randint(-8,8) for _ in range(rng.randint(0,10)));a.sort();source=array(a)+array(b);answer=line(sorted(a+b));reason='两个有序序列的全部结点都要保留，包括重复值；空表不会贡献元素。'
        elif pid==2:
            x,y=rng.randint(0,10**12),rng.randint(0,10**12);source=array(list(str(x)[::-1]))+array(list(str(y)[::-1]));answer=line(str(x+y)[::-1]);reason='两条链表分别表示 %d 和 %d，先相加再按低位在前输出 %d，末尾进位不能丢失。'%(x,y,x+y)
        elif pid==19:
            k=rng.randint(1,len(a));source+=str(k)+'\n';answer=line(a[:len(a)-k]+a[len(a)-k+1:]);reason='长度为 %d 的链表中，倒数第 %d 个对应正序下标 %d，删除且只删除这个结点。'%(len(a),k,len(a)-k)
        elif pid==24:
            values=a[:]
            for i in range(0,len(values)-1,2):values[i],values[i+1]=values[i+1],values[i]
            answer=line(values);reason='每个完整的相邻二元组交换顺序；奇数长度时最后一个结点保持原位。'
        elif pid==25:
            k=rng.randint(1,18);source+=str(k)+'\n';values=[]
            for i in range(0,len(a),k):part=a[i:i+k];values.extend(part[::-1] if len(part)==k else part)
            answer=line(values);reason='每 %d 个结点组成完整组才反转；最后不足一组的结点仍保持原顺序。'%k
        elif pid==138:
            randoms=[rng.choice([-1]+list(range(len(a)))) for _ in a];source+=line(randoms);answer=source;reason='拷贝后的值和 random 下标关系与原表相同；-1 是空指针，指向自己或形成 random 环也合法。'
        elif pid==148:answer=line(sorted(a));reason='按结点值升序排列，值相同的结点不能被去重或丢失。'
        else:
            lists=[sorted(rng.randint(-8,8) for _ in range(rng.randint(0,8))) for _ in range(rng.randint(0,7))];source=str(len(lists))+'\n'+''.join(array(x) for x in lists);answer=line(sorted([v for x in lists for v in x]));reason='合并所有链表中的结点，空链表可以跳过；链表数为零时输出空行。'
    elif pid in (94,104,226,101,543,102,108,98,230,199,114,105,437,236,124):
        size=rng.randint(1 if pid in (230,236,124) else 0,15);tree=random_tree(rng,size,pid in (105,236));source=tree_input(tree)
        if pid in (108,230):
            values=sorted(rng.sample(range(-100,101),size));tree=balanced(values)
            if pid==108:source,answer=array(values),serialize(tree);reason='输出保持严格二叉搜索树的大小关系，且每个结点的左右高度差不超过 1；偶数长度可选择不同中间结点。'
            else:k=rng.randint(1,size);source=tree_input(tree)+str(k)+'\n';answer=str(values[k-1])+'\n';reason='按数值升序排列结点值，第 %d 小是 %d；k 从 1 开始。'%(k,values[k-1])
        elif pid==94:answer=line(traversal(tree,'in'));reason='对每个结点先访问完整左子树，再访问该结点，最后访问右子树；空位置不输出值。'
        elif pid==104:answer=str(len(levels(tree)))+'\n';reason='从根到最深叶子的结点数为 %d，不是边数。'%len(levels(tree))
        elif pid==226:answer=serialize(mirror(tree));reason='在每个非空结点处都交换左右子树；输出层序序列中的 null 保留中间的空位置。'
        elif pid==101:
            if attempt%2==0:child=random_tree(rng,rng.randint(0,5));tree=node(rng.randint(-3,3),child,mirror(child));source=tree_input(tree)
            answer=boolean(tree==mirror(tree));reason='比较镜像位置的值和结构，只有两者都对应才对称，空树也对称。'
        elif pid in (543,124):
            all_nodes,graph=tree_graph(tree);best=0 if pid==543 else -10**9
            for start in range(len(all_nodes)):
                queue=deque([(start,-1,0 if pid==543 else all_nodes[start][0])])
                while queue:
                    current,parent,value=queue.popleft();best=max(best,value)
                    for following in graph[current]:
                        if following!=parent:queue.append((following,current,value+1 if pid==543 else value+all_nodes[following][0]))
            answer=str(best)+'\n';reason=('最长路径经过 %d 条边，可能不经过根。' if pid==543 else '比较任意起点、终点之间的非空简单路径，最大结点值总和为 %d；全负数也不能选空路径。')%best
        elif pid==102:result=levels(tree);answer=str(len(result))+'\n'+''.join(line([len(row),*row]) for row in result);reason='每层从左到右输出，先写层数，再在每层前写该层结点数，不能把空孩子当成一层。'
        elif pid==98:
            if attempt%3==0:tree=balanced(sorted(rng.sample(range(-100,101),size)));source=tree_input(tree)
            values=traversal(tree,'in');answer=boolean(all(x<y for x,y in zip(values,values[1:])));reason='要求整棵左子树都小于根、整棵右子树都大于根，重复值也会使严格搜索树条件失败。'
        elif pid==199:answer=line([row[-1] for row in levels(tree)]);reason='取每层最右边的实际结点，右子树缺失时可能看到左子树中的结点。'
        elif pid==114:answer=line(traversal(tree,'pre'));reason='展开后的 right 链顺序是根、左子树、右子树的前序顺序，不能使用中序或层序结果。'
        elif pid==105:source=str(size)+'\n'+line(traversal(tree,'pre'))+line(traversal(tree,'in'));answer=serialize(tree);reason='前序确定各子树根的先后顺序，中序确定左右范围；两序列来自同一棵树且没有重复值。'
        elif pid==437:
            target=rng.randint(-10,10);source+=str(target)+'\n';count=0
            for start in nodes(tree):
                queue=[(start,start[0])]
                while queue:
                    current,value=queue.pop();count+=value==target
                    queue.extend((child,value+child[0]) for child in current[1:] if child is not None)
            answer=str(count)+'\n';reason='可以从任意结点开始，但只能向后代延伸；和为 %d 的非空路径按起点、终点计数，共 %d 条。'%(target,count)
        else:
            all_nodes=nodes(tree);p,q=rng.choice(all_nodes)[0],rng.choice(all_nodes)[0];source+=line([p,q]);paths={}
            def visit(current,path):
                if current is None:return
                paths[current[0]]=path+[current[0]];visit(current[1],paths[current[0]]);visit(current[2],paths[current[0]])
            visit(tree,[]);common=[x for x,y in zip(paths[p],paths[q]) if x==y];answer=str(common[-1])+'\n';reason='从根出发的两条路径最后共同经过的结点就是答案；一个目标结点也可能是另一个的祖先。'
    elif pid in (146,155,208,295):
        operations=[];answers=[];q=rng.randint(12,30)
        if pid==146:
            capacity=rng.randint(1,5);cache=OrderedDict()
            for _ in range(q):
                key=rng.randint(0,7)
                if rng.random()<.55:
                    value=rng.randint(0,100);operations.append('PUT %d %d'%(key,value));cache.pop(key,None);cache[key]=value
                    if len(cache)>capacity:cache.popitem(last=False)
                else:
                    operations.append('GET %d'%key);answers.append(cache.get(key,-1))
                    if key in cache:cache.move_to_end(key)
            operations.append('GET 0');answers.append(cache.get(0,-1));source=line([capacity,len(operations)])+'\n'.join(operations)+'\n';reason='成功 GET 和新增/更新 PUT 都刷新最近使用顺序；容量满时淘汰最久未使用的键，查询不存在键返回 -1。'
        elif pid==155:
            stack=[]
            for _ in range(q):
                operation=rng.choice(['push','push','pop','top','getMin']) if stack else 'push'
                if operation=='push':value=rng.randint(-10,10);stack.append(value);operations.append('push %d'%value)
                elif operation=='pop':stack.pop();operations.append('pop')
                else:operations.append(operation);answers.append(stack[-1] if operation=='top' else min(stack))
            if not stack:stack.append(0);operations.append('push 0')
            operations.append('getMin');answers.append(min(stack));source=str(len(operations))+'\n'+'\n'.join(operations)+'\n';reason='只在非空栈上查询或弹出；top 返回栈顶，getMin 返回当前全部栈元素中的最小值。'
        elif pid==208:
            words=set()
            for _ in range(q):
                word=''.join(rng.choice('abc') for _ in range(rng.randint(1,5)));operation=rng.choice(['insert','search','startsWith']);operations.append(operation+' '+word)
                if operation=='insert':words.add(word)
                else:answers.append('true' if (word in words if operation=='search' else any(w.startswith(word) for w in words)) else 'false')
            operations.append('startsWith a');answers.append('true' if any(w.startswith('a') for w in words) else 'false');source=str(len(operations))+'\n'+'\n'.join(operations)+'\n';reason='search 必须匹配完整已插入单词，startsWith 只需匹配某个已插入单词的开头，两者结果可以不同。'
        else:
            values=[]
            for _ in range(q):
                if not values or rng.random()<.6:value=rng.randint(-20,20);values.append(value);operations.append('addNum %d'%value)
                else:ordered=sorted(values);answers.append((ordered[len(ordered)//2]+ordered[(len(ordered)-1)//2])/2);operations.append('findMedian')
            ordered=sorted(values);answers.append((ordered[len(ordered)//2]+ordered[(len(ordered)-1)//2])/2);operations.append('findMedian');source=str(len(operations))+'\n'+'\n'.join(operations)+'\n';reason='每次查询都只使用此时已经加入的数字；偶数数量取中间两数平均值，负数和重复值照常参与。'
        answer=''.join(str(x)+'\n' for x in answers)
    elif pid in (200,994,79):
        m,n=rng.randint(1,4 if pid!=79 else 3),rng.randint(1,4 if pid!=79 else 3)
        grid=[[rng.choice('abAB') if pid==79 else rng.randint(0,1 if pid==200 else 2) for _ in range(n)] for _ in range(m)]
        source=line([m,n])+''.join(''.join(map(str,row))+'\n' if pid in (200,79) else line(row) for row in grid)
        if pid==200:
            land={(r,c) for r in range(m) for c in range(n) if grid[r][c]==1};parents={x:x for x in land}
            def find(x):
                while parents[x]!=x:x=parents[x]
                return x
            for r,c in land:
                for neighbor in [(r+1,c),(r,c+1)]:
                    if neighbor in land:parents[find(neighbor)]=find((r,c))
            value=len({find(x) for x in land});answer=str(value)+'\n';reason='只把上下左右相邻的陆地连在一起，斜对角不相连，共有 %d 座岛。'%value
        elif pid==994:
            fresh={(r,c) for r in range(m) for c in range(n) if grid[r][c]==1};rotten={(r,c) for r in range(m) for c in range(n) if grid[r][c]==2};minute=0
            while fresh:
                following={(r+dr,c+dc) for r,c in rotten for dr,dc in [(0,1),(0,-1),(1,0),(-1,0)]}&fresh
                if not following:minute=-1;break
                minute+=1;fresh-=following;rotten|=following
            answer=str(minute)+'\n';reason='同一分钟的腐烂传播同时发生，空格子不能传染；'+('有新鲜橘子始终无法感染，输出 -1。' if minute==-1 else '经过 %d 分钟不再有新鲜橘子。'%minute)
        else:
            word=''.join(rng.choice('abAB') for _ in range(rng.randint(1,6)));source+=word+'\n';found=False;queue=deque([(r,c,0,frozenset({(r,c)})) for r in range(m) for c in range(n) if grid[r][c]==word[0]])
            while queue:
                r,c,i,seen=queue.popleft()
                if i==len(word)-1:found=True;break
                for dr,dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                    pos=(r+dr,c+dc)
                    if 0<=pos[0]<m and 0<=pos[1]<n and pos not in seen and grid[pos[0]][pos[1]]==word[i+1]:queue.append((*pos,i+1,seen|{pos}))
            answer=boolean(found);reason='单词字符按顺序连接，只走上下左右且不能重复使用格子，大小写必须相同；'+('存在这样的路径。' if found else '不存在符合全部规则的路径。')
    elif pid==207:
        n=rng.randint(1,6);edges=rng.sample([(a,b) for a in range(n) for b in range(n)],rng.randint(0,min(n*n,10)));requirements=[set() for _ in range(n)]
        for a,b in edges:requirements[a].add(b)
        reachable={frozenset()}
        for _ in range(n):reachable|={state|{course} for state in list(reachable) for course in range(n) if course not in state and requirements[course]<=state}
        source=line([n,len(edges)])+''.join(line(pair) for pair in edges);answer=boolean(any(len(state)==n for state in reachable));reason='依赖 a b 的方向是先 b 后 a；有自环或依赖环就不可能学完，否则可按某个先修顺序完成。'
    elif pid in (46,78,17,39,22,131,51):
        if pid in (46,78):
            a=rng.sample(range(-10,11),rng.randint(1 if pid==46 else 0,5 if pid==46 else 7));source=array(a);records=list(it.permutations(a)) if pid==46 else subsets(a);answer=collection(records);reason='共有 %d 个不同%s；每个输入元素最多在同一答案中使用一次，全部答案都必须输出。'%(len(records),'排列' if pid==46 else '子集（包括空集）')
        elif pid==17:
            digits=''.join(rng.choice('23456789') for _ in range(rng.randint(1,3)));mapping=dict(zip('23456789',['abc','def','ghi','jkl','mno','pqrs','tuv','wxyz']));records=[''.join(x) for x in it.product(*(mapping[d] for d in digits))];source=digits+'\n';answer=str(len(records))+'\n'+'\n'.join(records)+'\n';reason='每位数字独立选择一个对应字母，组合数是各位选择数的乘积，共 %d 个。'%len(records)
        elif pid==39:
            candidates=sorted(rng.sample(range(2,12),rng.randint(1,5)));target=rng.randint(1,15);records=[]
            for counts in it.product(*(range(target//v+1) for v in candidates)):
                if sum(v*c for v,c in zip(candidates,counts))==target:records.append([v for v,c in zip(candidates,counts) for _ in range(c)])
            source=line([len(candidates),target])+line(candidates);answer=collection(records);reason='每个候选数可以重复选取，按各数的选择次数区分组合；和恰好为 %d 的组合有 %d 个。'%(target,len(records))
        elif pid==22:
            n=attempt+1;records=[''.join(x) for x in it.product('()',repeat=2*n) if valid_brackets(''.join(x))];source=str(n)+'\n';answer=str(len(records))+'\n'+'\n'.join(records)+'\n';reason='%d 对括号构成 %d 个合法串，每个前缀中右括号都不能更多。'%(n,len(records))
        elif pid==131:
            word=''.join(rng.choice('abc') for _ in range(rng.randint(1,8)));records=[]
            for mask in range(1<<(len(word)-1)):
                cuts=[0]+[i+1 for i in range(len(word)-1) if mask>>i&1]+[len(word)];parts=[word[a:b] for a,b in zip(cuts,cuts[1:])]
                if all(part==part[::-1] for part in parts):records.append(parts)
            source=word+'\n';answer=collection(records);reason='切分后的每段都必须回文且拼接回原串；不同切分位置形成 %d 个完整方案。'%len(records)
        else:
            n=attempt+1;records=[p for p in it.permutations(range(1,n+1)) if len({i-v for i,v in enumerate(p)})==n and len({i+v for i,v in enumerate(p)})==n];source=str(n)+'\n';answer=collection(records);reason='每行和每列各放一个皇后，两条对角线方向也不能冲突；n=%d 时共有 %d 个方案，列号从 1 开始。'%(n,len(records))
    elif pid==394:
        def encoded(depth):
            if depth==0 or rng.random()<.3:text=''.join(rng.choice('abc') for _ in range(rng.randint(1,3)));return text,text
            first,expanded=encoded(depth-1);second,other=encoded(depth-1);count=rng.randint(1,5);return str(count)+'['+first+']'+second,expanded*count+other
        text,value=encoded(3);source,answer=text+'\n',value+'\n';reason='方括号中的片段先完成内部解码，再整体重复指定次数；括号之外的字母按出现顺序拼接。'
    elif pid==739:
        values=[next((j-i for j in range(i+1,n) if a[j]>a[i]),0) for i in range(n)];answer=line(values);reason='寻找后面第一个严格更高的温度，相同温度不满足要求；始终没有更高值则填 0。'
    elif pid in (55,45):
        a=[rng.randint(0,5) for _ in a]
        if pid==45 and jumps(a) is None:a=[max(1,x) for x in a]
        distance=jumps(a);source=array(a);answer=boolean(distance is not None) if pid==55 else str(distance)+'\n';reason='每次向右跳的步数可以小于当前最大值；'+('到不了最后一个位置。' if distance is None else '到达末尾至少需要 %d 次跳跃，长度为 1 时无需跳跃。'%distance)
    elif pid==763:
        word=''.join(rng.choice('abc') for _ in range(rng.randint(1,10)));best=[]
        for mask in range(1<<(len(word)-1)):
            cuts=[0]+[i+1 for i in range(len(word)-1) if mask>>i&1]+[len(word)];parts=[word[a:b] for a,b in zip(cuts,cuts[1:])]
            if sum(len(set(part)) for part in parts)==len(set(word)) and len(parts)>len(best):best=parts
        source=word+'\n';answer=str(len(best))+'\n'+line(map(len,best));reason='同一种字母的所有出现都保留在同一片段内，满足这一条件时最多能分成 %d 段。'%len(best)
    elif pid in (70,118,279,62):
        if pid==70:
            n=rng.randint(1,45);value=sum(math.comb(n-k,k) for k in range(n//2+1));source,answer=str(n)+'\n',str(value)+'\n';reason='按使用两级步子的次数分类，再选择这些步子的位置，共 %d 种顺序不同的走法。'%value
        elif pid==118:
            n=rng.randint(1,30);source=str(n)+'\n';answer=''.join(line(math.comb(r,c) for c in range(r+1)) for r in range(n));reason='第 r 行（从 0 开始）的第 c 项是组合数 C(r,c)，每行两端都是 1，共输出 %d 行。'%n
        elif pid==279:
            n=rng.randint(1,300);squares=[x*x for x in range(1,math.isqrt(n)+1)];queue=deque([(0,0)]);seen={0}
            while queue:
                current,steps=queue.popleft()
                if current==n:value=steps;break
                for square in squares:
                    following=current+square
                    if following<=n and following not in seen:seen.add(following);queue.append((following,steps+1))
            source,answer=str(n)+'\n',str(value)+'\n';reason='只使用正完全平方数，允许同一个平方数重复出现，组成 %d 最少需要 %d 项。'%(n,value)
        else:
            m,n=rng.randint(1,100),rng.randint(1,100);value=math.comb(m+n-2,m-1);source,answer=line([m,n]),str(value)+'\n';reason='每条路径由 %d 次向下和 %d 次向右组成，选择这些移动的次序即可得到 %d 条路径，需用整数精确输出。'%(m-1,n-1,value)
    elif pid in (198,300,416):
        if pid==198:a=[abs(v) for v in a]
        if pid==416:a=[abs(v)+1 for v in a]
        selected=subsets(a)
        if pid==198:value=max(sum(a[i] for i in range(len(a)) if mask>>i&1) for mask in range(1<<len(a)) if not(mask & (mask<<1)));answer=str(value)+'\n';reason='不能同时选相邻下标；在全部合法选择（包括不选）中，最大金额为 %d。'%value
        elif pid==300:value=max(len(x) for x in selected if all(u<v for u,v in zip(x,x[1:])));answer=str(value)+'\n';reason='只能删元素、不能换顺序，相等值不能延长严格递增序列；最大长度为 %d。'%value
        else:value=any(sum(x)*2==sum(a) for x in selected);answer=boolean(value);reason='每个位置仅用一次，'+('存在一个子集恰好占总和的一半，剩余元素组成另一半。' if value else '总和为奇数或不存在恰好一半的子集，所以无法均分。')
        source=array(a)
    elif pid==322:
        coins=sorted(rng.sample(range(1,13),rng.randint(1,6)));amount=rng.randint(0,45);distance={0:0};queue=deque([0])
        while queue:
            current=queue.popleft()
            for coin in coins:
                following=current+coin
                if following<=amount and following not in distance:distance[following]=distance[current]+1;queue.append(following)
        value=distance.get(amount,-1);source=line([len(coins),amount])+line(coins);answer=str(value)+'\n';reason='每种面值都可无限使用；'+('无法组成金额 %d，输出 -1。'%amount if value==-1 else '组成金额 %d 至少要 %d 枚硬币，金额为零时不用硬币。'%(amount,value))
    elif pid==139:
        word=''.join(rng.choice('ab') for _ in range(rng.randint(1,12)));dictionary=sorted(set(''.join(rng.choice('ab') for _ in range(rng.randint(1,5))) for _ in range(rng.randint(1,8))))
        @lru_cache(None)
        def split(index):return index==len(word) or any(word.startswith(token,index) and split(index+len(token)) for token in dictionary)
        value=split(0);source=word+'\n'+str(len(dictionary))+'\n'+'\n'.join(dictionary)+'\n';answer=boolean(value);reason='词典单词可重复用，但切分必须覆盖整个字符串且顺序不能改变；'+('存在完整切分方案。' if value else '局部能匹配也无法完成整串切分。')
    else:
        raise ValueError('missing oracle for #%d'%pid)
    assert reason, pid
    return {'input':source,'output':answer,'explanation':reason}


def build(details):
    problems=base_problems();result={}
    assert set(details)=={str(pid) for pid in problems}
    for pid,p in problems.items():
        rng=random.Random(20261012+pid);original={c['input'] for c in p['tests']};extra=[];seen=set(original);target={22:8,51:9}.get(pid,20);attempt=0
        while len(seen)<target or (pid not in (22,51) and len(extra)<15):
            example=case(pid,rng,attempt);attempt+=1
            if example['input'] not in seen:
                seen.add(example['input']);extra.append(example)
            if pid in (22,51) and attempt==target:break
            if attempt>3000:raise ValueError('not enough diverse cases #%d'%pid)
        # Select concise examples; keep the first familiar example and explain it.
        first=dict(p['examples'][0],explanation=details[str(pid)]['sample'])
        concise=sorted(extra,key=lambda x:len(x['input'])+len(x['output']))
        examples=[first]+concise[:2]
        if len(examples)<3:
            for old in p['tests'][1:]:
                if len(examples)==3:break
                if all(old['input']!=x['input'] for x in examples):examples.append(dict(old,explanation=details[str(pid)]['rules'][0]))
        result[str(pid)]={'description':p['description']+'\n\n'+details[str(pid)]['detail'],
            'clarifications':details[str(pid)]['rules'],'examples':examples,
            'tests':[{'input':x['input'],'output':x['output']} for x in extra]}
    destination=ROOT/'catalog/enrichment.json'
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Authored %d additional fixed cases for %d problems.'%(sum(len(x['tests']) for x in result.values()),len(result)))


if __name__=='__main__':
    build(json.loads((ROOT/'tools/practice_details.json').read_text(encoding='utf-8')))
