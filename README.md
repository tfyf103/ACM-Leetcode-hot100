# ACM · LeetCode Hot 100

一个只需 **Python 3** 的本地刷题工作台。采用熟悉的 LeetCode 分栏布局，将新版热题 100 改为 **ACM 标准输入 / 标准输出模式**：自己读输入、写 `solve()`、打印答案。

**无需 pip、Node.js、Docker、账号或 API key。题库、代码编辑器和判题均可离线使用。**

## 开始使用

安装 Python **3.9 或更高版本**，下载并解压本仓库，在项目目录运行：

```bash
python app.py
```

浏览器会自动打开 <http://127.0.0.1:8765>。终端保持运行，结束时按 `Ctrl+C`。

- **Windows**：直接双击 `start.bat`。支持 Python、Miniconda、Anaconda；无需提前激活环境或安装依赖。
- **macOS / Linux**：执行 `python3 app.py` 或 `sh start.sh`。
- 端口被占用：`python app.py --port 8766`。
- 不自动打开浏览器：`python app.py --no-browser`。

### Windows / Miniconda 启动

已安装 Miniconda 就不需要再安装一份 Python。`start.bat` 会调用 Windows 自带的 PowerShell，逐一验证 Python 版本和 SQLite 模块，自动跳过不可用的 `py` 启动器与 Microsoft Store 别名；也会查找 Conda 环境记录和各盘根目录的常见安装位置（例如 `E:\Miniconda3`）。不会下载文件、运行 `pip` 或修改系统 PATH。

```bat
start.bat --check
start.bat --port 8766
start.bat --no-browser
```

`--check` 只显示检测到的 Python 路径和版本；其他参数原样传递给应用。正常启动后请保持终端窗口打开。

如果安装位置特殊或需要指定环境，在项目根目录新建 `python-path.txt`，只写一行完整路径，例如：

```text
E:\Miniconda3\python.exe
```

也可以设置环境变量 `ACM_PYTHON`（优先于该文件），或在已激活环境的 Miniconda Prompt 中启动。`python-path.txt` 不会上传 GitHub。显式指定的路径无效时会报错，避免悄悄使用其他环境。

如果仍使用旧版项目，可临时运行：

```bat
"E:\Miniconda3\python.exe" app.py
```

更新项目时保留 `.local/` 和自己的 `python-path.txt`，以免丢失刷题进度或本机设置。`start.bat` 与 `start.ps1` 需要一起更新。

也可以使用 Git：

```bash
git clone https://github.com/tfyf103/ACM-Leetcode-hot100.git
cd ACM-Leetcode-hot100
python app.py
```

## 如何刷题

1. 打开「题单」，按分类、难度、完成状态或关键词选题。
2. 阅读该题的**输入格式和输出格式**。这里不使用 `class Solution` 接口，也不直接把 LeetCode 的 JSON 示例粘进 stdin。
3. 在右侧 Python 3 编辑器中写完整程序，点击「运行」检查当前输入。
4. 点击「提交」运行该题全部本地测试。通过后记录完成状态；错误时显示失败用例、预期输出、实际输出或异常。
5. 需要时查看题解、历史提交或记笔记。代码草稿自动保存，刷新和重启后可继续。

常用 Python ACM 模板：

```python
import sys

input = sys.stdin.readline

def solve():
    n = int(input())
    nums = list(map(int, input().split()))
    # 根据当前题目的格式读取其他数据并求解
    print(sum(nums))

if __name__ == '__main__':
    solve()
```

## 功能

- 新版 Hot 100：17 个分类、100 道题，逐题 ACM 说明、样例、测试和 Python 参考解法。
- 本地 CodeMirror 编辑器：Python 高亮、行号、自动缩进、括号匹配、字号设置。
- 左侧题面，右侧编辑器及测试结果；可拖拽分栏，支持浅色 / 深色。
- 自定义标准输入、错误诊断、超时与输出大小限制。
- 多解题专门判定：例如两数之和、异位词分组、最长回文、平衡二叉搜索树等。
- 搜索、分类和难度筛选、收藏、计时器、笔记、提交历史、进度备份导入导出。
- `Ctrl+Enter` 运行，`Ctrl+Shift+Enter` 提交（macOS 使用 `Cmd`）。

## 题库与判题说明

本项目按[当前官方学习计划](https://leetcode.cn/studyplan/top-100-liked/)整理题目，题面以简明中文重新描述并定义 ACM 协议。链表、二叉树、Trie、LRU 等题目使用题面列出的序列或操作输入，不需要额外插件。

每题包含样例和边界测试；集合类答案在题意允许时忽略顺序，浮点答案使用误差容忍。**Accepted 表示通过本项目的测试，不等同于通过力扣官方隐藏测试。** 本地测试并不能证明算法复杂度、原地修改或深拷贝语义；相关要求在题解中说明。

「运行」只执行你当前的 stdin，不增加已完成数量；「提交」才检查整套测试。运行时使用启动应用的同一 Python 解释器。

自定义输入最多 4 MiB；一般题目输出最多 4 MiB、单个用例限时 2 秒。三数之和可能输出大量合法组合，单独允许 32 MiB 输出和 10 秒；每次提交总限时仍为 35 秒。网页结果区每段最多展示 65,536 个字符并提示截断，判题使用完整输出。

## 保存与迁移

进度、草稿、笔记和提交记录保存在项目的 `.local/` 目录中，已排除 Git 跟踪。请勿删除该目录，除非确实想清空练习记录。可以在网页中导出 JSON 备份，并在另一台电脑导入。

也可以指定数据目录：

```bash
python app.py --data-dir path/to/my-progress
```

## 本机运行范围

服务仅监听 `127.0.0.1`，适合个人电脑使用。提交的 Python 代码以当前用户身份执行，可以访问本机文件；超时和输出限制不是操作系统沙箱。仅运行你信任的代码，不应把端口代理到公网或用作多人在线评测服务。

## 开发与测试

```bash
python -m unittest discover -s tests -v
python tools/verify_catalog.py
```

可选前端行为回归：`node tests/test_frontend.cjs`。Node.js 只用于开发测试，日常刷题仍只需 Python。

结构：`app.py`（HTTP / 持久化）、`judge.py`（运行及判题）、`catalog/`（题库）、`static/`（离线网页）。不需要前端构建步骤。

本次验证（2026-10-12，Windows / Miniconda Python 3.13.13）：100 题的 **542** 个固定测试全部通过；**15** 个手工多解及错误答案检查通过；**39** 项 Python 回归（34 项后端、5 项 Windows 启动器）通过；**8** 项前端行为回归通过。启动器实测覆盖中文/空格路径、参数传递、Python 不在 PATH、失效的 `py` 启动器和指定解释器。前端本次通过内存 DOM 验证，未重新进行真实浏览器视觉验收。macOS/Linux 尚未实机验收。

参考项目及依赖许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。原创实现采用 MIT；CodeMirror 保留其 MIT 声明。界面借鉴 LeetCode 工作台，仅用于个人本地练习，与力扣官方无关联。
