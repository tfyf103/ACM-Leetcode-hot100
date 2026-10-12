// Optional frontend regressions: node --test tests/test_frontend.js
// Uses built-in Node modules only; Node is not needed to run the application.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');

function deferred() {
  let resolve, reject;
  const promise = new Promise((done, fail) => { resolve = done; reject = fail; });
  return {promise, resolve, reject};
}

class Element {
  constructor(text = '') {
    this.children = [];
    this.value = '';
    this.textContent = text;
    this.style = {setProperty() {}};
    this.dataset = {};
    this.selectionStart = 0;
    const classes = new Set();
    this.classList = {
      add: (...names) => names.forEach(name => classes.add(name)),
      remove: (...names) => names.forEach(name => classes.delete(name)),
      contains: name => classes.has(name),
      toggle(name, active = !classes.has(name)) {
        if (active) classes.add(name); else classes.delete(name);
      },
    };
  }
  get lastElementChild() { return this.children.at(-1) || this; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  addEventListener() {}
  setAttribute() {}
  removeAttribute() {}
  querySelectorAll() { return []; }
  focus() {}
  scrollIntoView() {}
}

const problems = [1, 2].map(id => ({
  id, title: `Problem ${id}`, slug: `problem-${id}`, difficulty: 'Easy',
  category: 'Arrays', description: '', input_format: '', output_format: '',
  examples: [], starter: `starter ${id}`,
}));

function harness() {
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, new Element());
    return elements.get(id);
  };
  const document = {
    getElementById: element,
    createElement: () => new Element(),
    createTextNode: text => new Element(text),
    querySelectorAll: () => [],
    querySelector: element,
    addEventListener() {},
    documentElement: new Element(),
    body: new Element(),
  };
  const backupRequest = deferred();
  const navigationRequest = deferred();
  let holdNavigation = false, secondProblemRequests = 0, failBootstrap = false;
  const requests = [];
  const context = vm.createContext({
    document, console,
    window: {addEventListener() {}},
    localStorage: {getItem: () => null, setItem() {}},
    location: {hash: ''}, history: {replaceState() {}},
    confirm: () => true,
    setTimeout: () => 1, clearTimeout() {}, setInterval() {},
    requestAnimationFrame: fn => fn(),
    fetch: async (url, options) => {
      requests.push({url, options});
      let data;
      if (url === '/api/problems/2' && holdNavigation && ++secondProblemRequests === 1) {
        data = await navigationRequest.promise;
      } else if (url === '/api/import') {
        data = await backupRequest.promise;
      } else if (url === '/api/bootstrap') {
        if (failBootstrap) throw new Error('Connection interrupted');
        data = {token: 'new-token', progress: {
          1: {code: 'imported 1'}, 2: {code: 'imported 2'},
        }};
      } else if (/\/solution$/.test(url)) {
        data = {solution: 'reference solution', explanation: ''};
      } else if (/\/submissions$/.test(url)) {
        data = {submissions: [{code: 'old submission', status: 'Accepted',
          passed: 1, total: 1, elapsed_ms: 1, created_at: 0}]};
      } else if (/\/api\/problems\/\d+$/.test(url)) {
        data = problems.find(problem => url.endsWith('/' + problem.id));
      } else {
        data = {ok: true};
      }
      return {ok: true, json: async () => data};
    },
  });
  const source = fs.readFileSync(path.join(__dirname, '../static/app.js'), 'utf8');
  assert.match(source, /  bootstrap\(\);\s*\}\)\(\);\s*$/);
  vm.runInContext(source.replace(/  bootstrap\(\);(?=\s*\}\)\(\);\s*$)/,
    '  globalThis.app = {state, openProblem, loadSolution, loadSubmissions};'), context);
  context.app.state.problems = problems;
  context.app.state.token = 'token';
  function importBackup(text = '{}') {
    element('import-file').files = [{size: text.length, text: async () => text}];
    return element('import-file').onchange();
  }
  return {app: context.app, element, requests, backupRequest, navigationRequest,
    importBackup, holdNavigation: () => { holdNavigation = true; },
    failBootstrap: () => { failBootstrap = true; }};
}

const settle = () => new Promise(resolve => setImmediate(resolve));
function findText(root, text) {
  if (root.textContent === text) return root;
  for (const child of root.children || []) {
    const match = findText(child, text);
    if (match) return match;
  }
}

test('backup import waits for navigation and then preserves the selected problem', async () => {
  const h = harness();
  await h.app.openProblem(1);
  h.holdNavigation();
  const navigation = h.app.openProblem(2);
  await h.importBackup();
  assert.equal(h.requests.some(request => request.url === '/api/import'), false);
  assert.match(h.element('toast').textContent, /加载/);
  assert.equal(h.element('code').disabled, true);
  h.navigationRequest.resolve(problems[1]);
  await navigation;
  const importing = h.importBackup();
  await settle();
  assert.equal(h.element('code').disabled, true);
  assert.equal(h.element('notes').disabled, true);
  h.backupRequest.resolve({ok: true});
  await importing;
  assert.equal(h.app.state.current.id, 2);
  assert.equal(h.element('code').value, 'imported 2');
  assert.equal(h.element('code').disabled, false);
});

test('a failed import preserves the selected problem and enables editing', async () => {
  const h = harness();
  await h.app.openProblem(1);
  h.holdNavigation();
  const navigation = h.app.openProblem(2);
  h.navigationRequest.resolve(problems[1]);
  await navigation;
  await h.importBackup('{');
  assert.equal(h.app.state.current.id, 2);
  assert.equal(h.element('code').disabled, false);
  assert.equal(h.requests.some(request => request.url === '/api/import'), false);
});

test('reference solution cannot replace a draft during backup import', async () => {
  const h = harness();
  await h.app.openProblem(1);
  await h.app.loadSolution(1);
  const apply = findText(h.element('solution-view'), '放入编辑器');
  assert.ok(apply);
  const importing = h.importBackup();
  await settle();
  apply.onclick();
  assert.equal(h.element('code').value, 'starter 1');
  h.backupRequest.resolve({ok: true});
  await importing;
  assert.equal(h.element('code').value, 'imported 1');
});

test('submission restore cannot replace a draft during backup import', async () => {
  const h = harness();
  await h.app.openProblem(1);
  await h.app.loadSubmissions(1);
  const view = h.element('submissions-view');
  view.children.find(child => child.className === 'submission-row').onclick();
  const restore = findText(view, '恢复这份代码');
  assert.ok(restore);
  const importing = h.importBackup();
  await settle();
  restore.onclick();
  assert.equal(h.element('code').value, 'starter 1');
  h.backupRequest.resolve({ok: true});
  await importing;
  assert.equal(h.element('code').value, 'imported 1');
});

test('failed progress reload cannot leave stale drafts editable after import', async () => {
  const h = harness();
  await h.app.openProblem(1);
  h.failBootstrap();
  const importing = h.importBackup();
  h.backupRequest.resolve({ok: true});
  await importing;
  assert.equal(h.element('code').disabled, true);
  assert.equal(h.element('notes').disabled, true);
  assert.equal(h.element('run').disabled, true);
  assert.equal(h.app.state.current, null);
  await h.app.openProblem(2);
  assert.equal(h.app.state.current, null);
  assert.ok(findText(h.element('description-view'), '重试'));
});

test('lost import response reloads persisted progress before editing resumes', async () => {
  const h = harness();
  await h.app.openProblem(1);
  const importing = h.importBackup();
  await settle();
  h.backupRequest.reject(new Error('Response connection lost'));
  await importing;
  assert.equal(h.element('code').value, 'imported 1');
  assert.equal(h.element('code').disabled, false);
  assert.equal(h.app.state.importing, false);
});
