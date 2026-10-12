# Sources and acknowledgments

## Bundled dependency

The files in `static/vendor/` are unmodified CodeMirror 5.22.0 distribution
files from [components/codemirror](https://github.com/components/codemirror),
an offline distribution of [CodeMirror](https://github.com/codemirror/codemirror5).
Copyright Marijn Haverbeke and other contributors; MIT license included in
`static/vendor/LICENSE`. Only the editor core, stylesheet, Python mode,
close-brackets, match-brackets and show-hint addons are bundled. No dependency download
is required when starting this application.

`show-hint.js` and `show-hint.css` come from the same CodeMirror 5.22.0 release
(https://github.com/codemirror/codemirror5/tree/5.22.0/addon/hint). Their MIT
license is preserved. The indentation guides and Python lexical candidate
provider in `static/editor-support.js` are authored for this project, using the
[CodeMirror 5 addon API](https://codemirror.net/5/doc/manual.html#addon_show-hint).

## Research references

- [LeetCode official Top 100 Liked study plan](https://leetcode.cn/studyplan/top-100-liked/): problem identifiers, names, categories and difficulty, checked on 2026-10-12. This uses the current 17-category study plan rather than the older Hot 100 list.
- [Python_LeetCode_Hot100](https://github.com/hymreire/Python_LeetCode_Hot100): cross-check of problem identifiers.
- [cojudge](https://github.com/cojudge/cojudge) (MIT): offline practice workflow, problem-specific checking and saved local progress.
- [vscode-leetcode](https://github.com/LeetCode-OpenSource/vscode-leetcode) (MIT): problem navigation and editing/submission workflow.
- [Leetcode-Clone](https://github.com/Avijit200318/Leetcode-Clone) (repository identifies MIT): split problem/editor/results layout.

These projects are architecture and interaction references. Their application
source, problem statements and solutions are not copied into this repository.
The ACM descriptions, input/output protocols, examples, tests and Python
reference programs are authored for this project. LeetCode's private judge
data is not included. LeetCode names and links identify corresponding problems;
this independent local practice project is not an official LeetCode client.
