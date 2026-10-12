# ACM · LeetCode Hot 100

一个只需 **Python 3** 的本地刷题工作台。采用熟悉的 LeetCode 分栏布局，将新版热题 100 改为 **ACM 标准输入 / 标准输出模式**：自己读输入、写 `solve()`、打印答案。

**无需 pip、Node.js、Docker、账号或 API key。题库、代码编辑器和判题均可离线使用。**

## 开始使用

安装 Python **3.9 或更高版本**（已有 Miniconda / Anaconda 也可以直接使用），下载并解压本仓库，在项目目录运行：

```bash
python app.py
```

浏览器会自动打开 <http://127.0.0.1:8765>。终端保持运行，结束时按 `Ctrl+C`。

- **Windows**：直接双击 `start.bat`。脚本会验证 Python 是否可用，支持项目 `.venv`、已激活的 Conda 环境、PATH、Python 启动器、Conda 登记的安装位置和常见安装目录；不会因为存在一个失效的 `py` 启动器就停止查找。
- **macOS / Linux**：执行 `python3 app.py` 或 `sh start.sh`。
- 端口被占用：`python app.py --port 8766`。
- 不自动打开浏览器：`python app.py --no-browser`。

Windows 启动脚本也支持这些参数，例如 `start.bat --port 8766 --no-browser`。执行 `start.bat --check` 只检查解释器，不启动服务。脚本使用 Windows 自带的 Windows PowerShell，不需要安装额外依赖。

如果 Miniconda 安装在自定义目录且未被自动找到，可以在 Anaconda Prompt 中进入项目目录再运行 `start.bat`，或在命令提示符中指定 Python 的完整路径：

```bat
set "ACM_PYTHON=E:\Miniconda3\python.exe"
start.bat
```

`ACM_PYTHON` 优先于自动检测；设置后若该解释器不可用，脚本会提示错误。启动时会显示实际使用的解释器路径，判题也使用同一个 Python。无需重新安装 Python、修改全局 PATH 或执行 `pip install`。

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

当前单用例时限为 5 秒，整次提交时限为 35 秒；自定义输入最多 4 MiB，标准输出和错误输出合计最多 32 MiB。这些上限覆盖题库中大量枚举结果的合法用例；运行时间仍会受到本机性能影响。

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

如已安装 Node.js，可额外运行 `node --test tests/test_frontend.js` 检查备份导入与草稿保存的异步回归；Node.js 仅用于这组开发测试，日常刷题不需要安装。

结构：`app.py`（HTTP / 持久化）、`judge.py`（运行及判题）、`catalog/`（题库）、`static/`（离线网页）。不需要前端构建步骤。

本次验证（2026-10-12，Windows / Miniconda Python 3.13）：100 题的 **540** 个固定测试全部通过；**15** 个多解及错误答案检查通过；**40** 项后台、题库边界及 Windows 启动回归通过；**6** 项前端异步回归通过。边界回归包括约 2.4 MB 输入、112 万个三数之和答案、全排列和回文分割的最大输出，以及无 PATH 配置的 Conda 检测和中文路径启动。macOS/Linux 启动路径已实现，尚未在对应系统实机验收。

参考项目及依赖许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。原创实现采用 MIT；CodeMirror 保留其 MIT 声明。界面借鉴 LeetCode 工作台，仅用于个人本地练习，与力扣官方无关联。
