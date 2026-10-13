# Implementation contract

Python standard library only, Python >=3.9. Assets offline. Local-only loopback server.

## Catalog
Each catalog/part_*.py exports PROBLEMS (list of dictionaries) and optional CHECKERS {int_id: callable(stdin, actual, expected)->bool}.
All authored descriptions are original concise Chinese ACM adaptations, not copied statements.
Fields: id (int), title, slug, difficulty (Easy/Medium/Hard), category (Chinese), description (plain text), input_format, output_format, constraints (list[str]), examples (list[{input,output,explanation}]), tests (list[{input,output}]), starter (standalone Python solve skeleton), solution (complete executable Python stdin/stdout program), explanation (Chinese algorithm and complexity), compare (default tokens; allowed tokens,float,unordered_lines,unordered_tokens,exact).
Minimum 5 meaningful cases per problem including examples + edges; reference solution must pass all. Avoid import-time subprocess execution. Fixed expected test outputs preferred; do not derive expectations from reference implementation at runtime. No JSON stdin: use ordinary ACM whitespace/line input. For nonunique answers implement CHECKERS instead of imposing arbitrary algorithm. Plain text output not HTML. Tree serialization: line with level-order values and null, first line token count when used; define precisely. Input consistency within each problem is essential.

The shipped catalog combines `part_*.py` with trusted fixed `enrichment.json`
through `apply_enrichment`. Both the application and verifier must apply this
same enrichment. At least 20 distinct inputs and 3 explained public examples
per problem; #22 and #51 instead cover every legal n (8 and 9 values). Public
field `clarifications: list[str]` explains exact rules and boundary behavior.
No reference solution is used to generate added expectations. The developer
generator uses independent small-input oracles and is never invoked at startup.

The same enrichment loads `tutorials.json` (exactly all 100 IDs) and
`optimal_solutions.json` (a subset of IDs). Each tutorial is
`{approach: str, sections: [{title: str, text: str}]}` with eight authored
sections covering derivation, correctness, trace, time, space and tradeoffs.
The flat `explanation` is derived from these sections for compatibility.
Optimized programs replace `solution` before either runtime or verifier uses it.
Tutorial text is rendered as plain text with semantic headings, never as HTML.

The complete catalog additionally loads `guides.json` into `tutorial.guide`.
Version 2 fields: `hook`, `goal`, `recognition {signals,pattern,why}`,
`dialogue [{question,hint,answer}]`, `walkthrough {input,columns,rows,conclusion}`,
`invariant {statement,reason}`, `recall {mnemonic,steps,skeleton}`,
`self_check [{question,answer}]`, `complexity {time,space,reason,optimality}`.
The builder and verifier check exact coverage and field/table integrity.
Each authored lesson has at least three discovery questions and two retrieval
questions. Memory skeletons are illustrative plain text, not executable programs.
Native details/summary keep hints and answers independently revealable; the
full-reading toggle opens instructional answers only and changes no saved drafts
or global preferences. Legacy sections and flat solution payloads remain supported.

The IO basics extension is exactly IDs 10001–10012, with `track: acm_io`,
`display_id: IO-01` through `IO-12`, category `ACM 输入输出基础` and Easy difficulty.
It loads fixed `io_basics.json` and `io_guides.json`, has at least 20 distinct
tests and three explained examples per exercise, and sorts before the unchanged
100 official Hot 100 IDs. Full catalog: 112 exercises, 18 categories.
The original enrichment/guides still require exact coverage of the Hot 100 subset.
Public problem and summary objects include optional display_id and track;
numeric IDs remain the API, hash URL and progress keys. Fresh/default navigation
uses the first catalog entry; saved history and explicit URLs take priority.

IO exercises use `compare: exact`: normalize CRLF to LF and ignore one optional
terminal newline only for nonempty expected output. All other characters,
including spaces, inner line breaks, labels and precision, are significant.
An empty expected result requires truly empty output. Other comparison modes
retain their existing contracts.

Optional per-problem fields: output_limit (positive int bytes, at most 32 MiB; default 4 MiB) and case_timeout (finite positive seconds, at most 35; default 5). Both custom runs and submissions must honor these fields. Overall submission timeout remains 35 seconds. Problem #15 uses 32 MiB / 10 seconds for its quadratic number of valid triples. HTTP stdin limit is 4 MiB and normal request body limit is 8 MiB.

## HTTP API
GET /api/bootstrap -> {problems:[summary objects {id,title,slug,difficulty,category,test_count,display_id?,track?}], progress:{string_id:{status,code,notes,favorite,updated_at}}, token:string, python_version:string}
GET /api/problems/{id} -> all public problem fields (excludes tests and solution; includes test_count)
GET /api/problems/{id}/solution -> {solution,explanation,tutorial?}; tutorial is optional for custom catalogs
GET /api/problems/{id}/submissions -> {submissions:[{id,problem_id,status,passed,total,elapsed_ms,created_at,code}]}
POST /api/progress {problem_id,code?,notes?,favorite?} -> {ok:true}. Preserve fields not present. Header X-Local-Token from bootstrap for all POST requests.
POST /api/run {problem_id,code,stdin} -> {status:Finished/Runtime Error/Time Limit Exceeded/Output Limit Exceeded,stdout,stderr,elapsed_ms}; no marking solved.
POST /api/submit {problem_id,code} -> {status:Accepted/Wrong Answer/Runtime Error/Time Limit Exceeded/Output Limit Exceeded,passed,total,elapsed_ms,case?:{input,expected,actual,stderr,index},submission_id}. Mark attempted or solved. Keep solved after later wrong submissions.
GET /api/export -> {version:1,progress:...,submissions:...}
POST /api/import (same shape) -> {ok:true}; merge progress; validate size.
Errors: {error:string} with non-2xx HTTP status.

## Frontend
static/index.html, static/styles.css, static/app.js; frontend agent owns static except vendor. LeetCode inspired desktop workspace: full-height top navbar, problem-list toggle/drawer, two-column problem/editor and tests underneath editor; light/dark, Python editor, tabs description/solution/submissions/notes, run + submit, custom stdin, resizable divider, search/filter the complete catalog, progress/favorites, timer, shortcut Ctrl+Enter run / Ctrl+Shift+Enter submit, persist drafts without switching races. Default problem is the first catalog entry. Do not display fake acceptance rates or fake account. Brand ACM Hot 100 with small local label. Prefer vendored lightweight CodeMirror if available; fallback should still be fully usable.
