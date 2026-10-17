// Optional developer checks: node tests/test_frontend.cjs (no npm dependencies).
// Node is only needed for these checks; the application runs with Python alone.
// Executes the shipped app in a minimal DOM with controlled request ordering.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const sourcePath = process.argv[2] || require('node:path').join(__dirname, '../static/app.js');
const source = fs.readFileSync(sourcePath, 'utf8').replace('  bootstrap();', '  globalThis.testApi={state,openProblem,renderDescription,renderCases,loadSolution,loadSubmissions,codeChanged,flushSave,execute,bootstrap};');

function deferred() { let resolve,reject; const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject}; }
function setup({storedValues={},hash=''}={}) {
  class Element {
    constructor(tag='div') {this.tagName=tag.toUpperCase();this.children=[];this.className='';this.value='';this.hidden=false;this.disabled=false;this.selectionStart=0;this.dataset={};this.textContent='';this.style={setProperty(k,v){this[k]=v;}};this.classList={contains:c=>this.className.split(' ').includes(c),add:c=>this.className+=' '+c,remove:c=>this.className=this.className.split(' ').filter(v=>v!==c).join(' '),toggle:(c,v)=>{if(v===undefined)v=!this.classList.contains(c);if(v)this.classList.add(c);else this.classList.remove(c);}};}
    append(...nodes){this.children.push(...nodes);}
    replaceChildren(...nodes){this.children=nodes;}
    get lastElementChild(){return this.children.at(-1)||(this.children[0]=new Element());}
    setAttribute(name,value){(this.attributes ||= {})[name]=value;} removeAttribute(name){if(this.attributes)delete this.attributes[name];} addEventListener(){} focus(){} scrollIntoView(){} remove(){} click(){} close(){} showModal(){}
    querySelectorAll(selector){return this.children.flatMap(c=>[...(selector==='*'||selector.startsWith('.')&&c.className.split(' ').includes(selector.slice(1))?[c]:[]),...c.querySelectorAll(selector)]);}
  }
  const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
  const stored=new Map(Object.entries(storedValues).map(([key,value])=>['acm-hot100:'+key,JSON.stringify(value)])),calls=[];
  const context={console,Map,Set,Promise,Blob,Date,JSON,Number,String,Array,Object,Math,Error,URL:{createObjectURL:()=>'',revokeObjectURL(){}},localStorage:{getItem:k=>stored.get(k)||null,setItem:(k,v)=>stored.set(k,v)},confirm:()=>true,setTimeout:()=>1,clearTimeout(){},setInterval(){},requestAnimationFrame(){},navigator:{},location:{hash,reload(){}},history:{replaceState(){}},getComputedStyle:()=>({getPropertyValue:()=>50}),document:{createElement:t=>new Element(t),createTextNode:t=>Object.assign(new Element(),{textContent:t}),getElementById:get,querySelectorAll:()=>[],querySelector:get,addEventListener(){},documentElement:new Element(),body:new Element(),activeElement:null}};
  context.window=context;context.addEventListener=()=>{};
  let handler=async()=>({});context.fetch=async(path,options={})=>{const body=options.body?JSON.parse(options.body):undefined;calls.push({path,body});return {ok:true,json:async()=>handler(path,body)};};
  vm.createContext(context);vm.runInContext(source,context);
  const problem=id=>({id,title:'Problem '+id,starter:'starter '+id,examples:[{input:'sample '+id,output:'answer'}],constraints:[],category:'array',difficulty:'Easy',slug:'p'+id});
  const {state}=context.testApi;state.problems=[problem(1),problem(2),problem(3)];state.current=state.problems[0];state.progress={1:{code:'old code'}};state.loading=false;get('code').value='old code';
  return {api:context.testApi,nodes,get,calls,stored,problem,setHandler:h=>handler=h};
}
const tests=[];const test=(name,fn)=>tests.push([name,fn]);
test('retired exercise links and saved history fall back to Hot100 without changing notes',async()=>{
  for(const options of [{hash:'#10008'},{storedValues:{'last-problem':10001}}]){
    const {api,get,setHandler,calls}=setup(options),catalog=api.state.problems,old={code:'my solution',notes:'my notes',favorite:true,status:'solved'};
    api.state.current=null;
    setHandler(path=>path==='/api/bootstrap'?{problems:catalog,progress:{1:{...old}},token:'test',python_version:'3.13'}:catalog.find(p=>path==='/api/problems/'+p.id)||{});
    await api.bootstrap();
    assert.equal(api.state.current.id,1);assert.equal(get('code').value,old.code);assert.equal(get('notes').value,old.notes);
    assert.deepEqual(api.state.progress[1],old);assert.equal(calls.some(c=>c.path.includes('/1000')||c.path==='/api/progress'),false);
  }
});
test('Hot100 unsaved drafts restore while retired drafts remain archived',async()=>{
  const drafts={1:{problem_id:1,code:'restored draft',notes:'restored note'},10008:{problem_id:10008,code:'archived draft'}};
  const {api,get,setHandler,calls,stored}=setup({storedValues:{'unsaved-drafts':drafts}}),catalog=api.state.problems;
  api.state.current=null;
  setHandler(path=>path==='/api/bootstrap'?{problems:catalog,progress:{1:{status:'solved'}},token:'test',python_version:'3.13'}:catalog.find(p=>path==='/api/problems/'+p.id)||{});
  await api.bootstrap();await api.state.saves;
  assert.equal(get('code').value,drafts[1].code);assert.equal(get('notes').value,drafts[1].notes);assert.equal(api.state.progress[1].status,'solved');
  assert.deepEqual(calls.filter(c=>c.path==='/api/progress').map(c=>c.body.problem_id),[1]);
  assert.deepEqual(JSON.parse(stored.get('acm-hot100:unsaved-drafts')), {10008:drafts[10008]});
});
function guidedPayload(){
  return {solution:'print(1)',explanation:'legacy explanation',tutorial:{approach:'Hash table',sections:[{title:'Proof',text:'Detailed proof'}],guide:{
    version:2,hook:'If we know one number, what is missing?',goal:'Recognize the complement',
    recognition:{signals:['Return two positions','Target sum'],pattern:'Lookup earlier numbers',why:'Reuse a stored position'},
    dialogue:[{question:'Can we try every pair?',hint:'Count the repeated comparisons',answer:'Quadratic pair search'},{question:'What do we need to remember?',hint:'The earlier position',answer:'Store a hash table'}],
    walkthrough:{input:'nums=[2,7], target=9',columns:['Current','Need','Seen'],rows:[['2','7','{}'],['7','2','{2:0}']],conclusion:'Return [0,1]'},
    invariant:{statement:'Only earlier positions are stored',reason:'Different positions are required'},
    recall:{mnemonic:'Find first, store second',steps:['Create a table','Look up the complement','Save this position'],skeleton:'seen = {}\nfor i, x in enumerate(nums):\n    ...'},
    self_check:[{question:'Why check before inserting?',answer:'Do not reuse this position'},{question:'What if two values are equal?',answer:'Different positions can still work'}],
    complexity:{time:'Expected O(n)',space:'O(n)',reason:'One lookup and insertion per number',optimality:'Must read the input'}
  }}};
}

test('guided tutorials render the actual title, state table and memory skeleton without changing code',async()=>{
  const {api,get,setHandler}=setup(),payload=guidedPayload();setHandler(()=>payload);await api.loadSolution(1);const view=get('solution-view');
  assert.equal(view.querySelectorAll('.guide-title')[0].textContent,'1. Problem 1');
  assert.equal(view.querySelectorAll('.guide-question').length,2);assert.equal(view.querySelectorAll('.guide-section').length,7);
  const table=view.querySelectorAll('.guide-state-table')[0];assert.equal(table.children[0].tagName,'CAPTION');assert.equal(table.children[0].textContent,payload.tutorial.guide.walkthrough.input);
  assert.deepEqual(table.children[1].children[0].children.map(c=>c.textContent),payload.tutorial.guide.walkthrough.columns);
  assert.ok(table.children[1].children[0].children.every(c=>c.attributes.scope==='col'));
  assert.deepEqual(table.children[2].children.map(row=>row.children.map(c=>c.textContent)),payload.tutorial.guide.walkthrough.rows);
  assert.equal(view.querySelectorAll('.guide-table-scroll')[0].tabIndex,0);assert.equal(view.querySelectorAll('.guide-skeleton')[0].textContent,payload.tutorial.guide.recall.skeleton);
  assert.equal(get('code').value,'old code');assert.equal(api.state.revisions[1],undefined);
});

test('reading mode reveals and closes answers locally while hints and proof stay independently collapsed',async()=>{
  const {api,get,setHandler,stored,calls}=setup();setHandler(()=>guidedPayload());await api.loadSolution(1);const view=get('solution-view'),answers=view.querySelectorAll('.guide-answer'),hints=view.querySelectorAll('.guide-hint'),modes=view.querySelectorAll('.guide-mode');
  assert.ok(answers.every(answer=>!answer.open));assert.equal(modes[0].attributes['aria-pressed'],'true');const before=[...stored];
  modes[1].onclick();assert.ok(answers.every(answer=>answer.open));assert.ok(hints.every(hint=>!hint.open));assert.ok(!view.querySelectorAll('.guide-deeper')[0].open);assert.equal(modes[1].attributes['aria-pressed'],'true');
  modes[0].onclick();assert.ok(answers.every(answer=>!answer.open));assert.equal(modes[1].attributes['aria-pressed'],'false');assert.deepEqual([...stored],before);assert.equal(calls.length,1);assert.equal(get('code').value,'old code');
});

test('guided content remains literal text even in questions, table cells and code skeletons',async()=>{
  const {api,get,setHandler}=setup(),payload=guidedPayload(),literal='<img src=x onerror=alert(1)>';
  payload.tutorial.guide.dialogue[0].question=literal;payload.tutorial.guide.dialogue[0].answer=literal;payload.tutorial.guide.walkthrough.rows[0][0]=literal;payload.tutorial.guide.recall.skeleton=literal;
  setHandler(()=>payload);await api.loadSolution(1);const view=get('solution-view');
  assert.equal(view.querySelectorAll('.guide-question-heading')[0].children[1].textContent,literal);assert.equal(view.querySelectorAll('.guide-answer')[0].children[1].textContent,literal);assert.equal(view.querySelectorAll('.guide-state-table')[0].children[2].children[0].children[0].textContent,literal);assert.equal(view.querySelectorAll('.guide-skeleton')[0].textContent,literal);
  assert.equal(view.querySelectorAll('*').some(node=>node.tagName==='IMG'),false);
});

test('a delayed guided payload cannot replace the next problem or its editor',async()=>{
  const {api,get,setHandler}=setup(),pending=deferred();setHandler(()=>pending.promise);const request=api.loadSolution(1);
  api.state.current=api.state.problems[1];get('solution-view').replaceChildren();get('code').value='draft two';pending.resolve(guidedPayload());await request;
  assert.equal(get('solution-view').querySelectorAll('.guide-hero').length,0);assert.equal(get('code').value,'draft two');assert.equal(api.state.revisions[2],undefined);
});

test('structured tutorials render headings and plain text without replacing the draft',async()=>{
  const {api,get,setHandler}=setup();const sections=Array.from({length:8},(_,i)=>({title:'Step '+i,text:'<b>literal</b>\nExplanation '+i}));
  setHandler(()=>({solution:'print(1)',explanation:'legacy explanation',tutorial:{approach:'Hash table',sections}}));
  await api.loadSolution(1);const blocks=get('solution-view').querySelectorAll('.tutorial-section');
  assert.equal(blocks.length,8);assert.deepEqual(blocks.map(b=>b.children[0].textContent),sections.map(s=>s.title));
  assert.equal(blocks[0].children[1].textContent,sections[0].text);assert.equal(get('code').value,'old code');
  assert.equal(get('solution-view').querySelectorAll('.solution-code')[0].textContent,'print(1)');
});

test('older solution payloads still display the flat explanation',async()=>{
  const {api,get,setHandler}=setup();setHandler(()=>({solution:'legacy code',explanation:'legacy explanation'}));
  await api.loadSolution(1);assert.equal(get('solution-view').querySelectorAll('.solution-explanation')[0].textContent,'legacy explanation');
});

test('enhanced descriptions render the full rules list and explained examples',()=>{
  const {api,get,problem}=setup();const p=Object.assign(problem(1),{description:'Detailed statement',clarifications:['Distinct indexes','Repeated values are allowed','Any valid answer'],examples:[{input:'2 0\n0 0\n',output:'0 1\n',explanation:'Two different positions'}]});
  api.renderDescription(p);const view=get('description-view');const rules=view.querySelectorAll('.constraints')[0];
  assert.deepEqual(rules.children.map(node=>node.textContent),p.clarifications);
  assert.ok(view.querySelectorAll('.example-explanation').some(node=>node.textContent.includes('Two different positions')));
});

test('custom input survives switching to a sample and another problem',async()=>{
  const {api,get}=setup();api.renderCases();get('stdin').value='custom\n123';get('stdin').oninput();get('case-buttons').children[0].onclick();assert.equal(get('stdin').value,'sample 1');get('case-buttons').children.at(-1).onclick();assert.equal(get('stdin').value,'custom\n123');
  api.state.current=api.state.problems[1];api.renderCases();api.state.current=api.state.problems[0];api.renderCases();assert.equal(get('stdin').value,'custom\n123');
});
test('rapid problem navigation preserves draft and ignores stale fetch',async()=>{
  const {api,get,setHandler,problem,calls}=setup(),p2=deferred(),p3=deferred();
  setHandler(path=>path==='/api/problems/2'?p2.promise:path==='/api/problems/3'?p3.promise:{});
  get('code').value='draft one';api.codeChanged();const nav2=api.openProblem(2),nav3=api.openProblem(3);p3.resolve(problem(3));await nav3;p2.resolve(problem(2));await nav2;await api.state.saves;
  assert.equal(api.state.current.id,3);assert.equal(get('code').value,'starter 3');assert.equal(calls.find(c=>c.path==='/api/progress').body.code,'draft one');assert.equal(calls.find(c=>c.path==='/api/progress').body.problem_id,1);
});
test('queued saves preserve later edit when earlier request completes',async()=>{
  const {api,get,setHandler,calls,stored}=setup(),first=deferred();let count=0;setHandler(path=>path==='/api/progress'&&++count===1?first.promise:{});
  get('code').value='first';api.codeChanged();api.flushSave(1);await Promise.resolve();await Promise.resolve();get('code').value='second';api.codeChanged();api.flushSave(1);first.resolve({ok:true});await api.state.saves;
  assert.deepEqual(calls.filter(c=>c.path==='/api/progress').map(c=>c.body.code),['first','second']);assert.equal(api.state.saved[1],api.state.revisions[1]);assert.deepEqual(JSON.parse(stored.get('acm-hot100:unsaved-drafts')),{});
});
test('import blocks stale solution/history buttons and overlapping export/run',async()=>{
  const {api,get,setHandler,calls}=setup(),fileText=deferred();
  setHandler(path=>path.endsWith('/solution')?{solution:'reference code',explanation:''}:path.endsWith('/submissions')?{submissions:[{code:'historical code',status:'Accepted',passed:1,total:1}]}:path==='/api/bootstrap'?{progress:{1:{code:'imported code'}},token:'new'}:path==='/api/problems/1'?api.state.problems[0]:{});
  await api.loadSolution(1);const apply=get('solution-view').querySelectorAll('*').find(e=>e.textContent==='放入编辑器');
  await api.loadSubmissions(1);get('submissions-view').children.find(e=>e.className==='submission-row').onclick();const restore=get('submissions-view').querySelectorAll('*').find(e=>e.textContent==='恢复这份代码');
  get('import-file').files=[{size:5,text:()=>fileText.promise}];const importing=get('import-file').onchange();assert.equal(api.state.importing,true);
  apply.onclick();restore.onclick();get('notes').value='stray note';get('notes').oninput();get('favorite').onclick();await get('export-data').onclick();await api.execute(true);
  assert.equal(get('code').value,'old code');assert.equal(api.state.revisions[1],undefined);assert.equal(get('export-data').disabled,true);assert.equal(calls.some(c=>['/api/export','/api/submit'].includes(c.path)),false);
  fileText.resolve('{}');await importing;assert.equal(get('code').value,'imported code');assert.equal(api.state.importing,false);assert.equal(get('code').disabled,false);
});
test('import waits until current navigation completes',async()=>{
  const {api,get,calls}=setup();api.state.loading=true;get('import-file').files=[{size:2,text:async()=>'{}'}];await get('import-file').onchange();assert.equal(calls.some(c=>c.path==='/api/import'),false);assert.match(get('toast').textContent,/加载/);
});
test('export refuses running submissions and serializes backup operations',async()=>{
  const {api,get,setHandler,calls}=setup(),response=deferred();api.state.busy=true;await get('export-data').onclick();assert.equal(calls.length,0);api.state.busy=false;setHandler(path=>path==='/api/export'?response.promise:{});
  const exporting=get('export-data').onclick();await Promise.resolve();await Promise.resolve();assert.equal(get('import-data').disabled,true);await api.execute(false);assert.equal(calls.some(c=>c.path==='/api/run'),false);response.resolve({});await exporting;assert.equal(get('import-data').disabled,false);
});
test('successful import with failed refresh disables stale editor',async()=>{
  const {api,get,setHandler,calls}=setup();setHandler(path=>{if(path==='/api/bootstrap')throw Error('connection lost');return {};});get('import-file').files=[{size:2,text:async()=>'{}'}];await get('import-file').onchange();assert.equal(api.state.current,null);assert.equal(get('code').disabled,true);assert.match(get('toast').textContent,/已导入/);await api.openProblem(2);assert.equal(api.state.current,null);assert.equal(calls.some(c=>c.path==='/api/problems/2'),false);
});
test('large result display is bounded without changing the judge response',async()=>{
  const {api,get,setHandler}=setup();const output='x'.repeat(4*1024*1024);setHandler(()=>({status:'Finished',stdout:output,elapsed_ms:1}));await api.execute(false);
  assert.equal(get('result-view').querySelectorAll('.result-pre')[0].textContent.length,65536);assert.equal(api.state.results.get(1).data.stdout.length,output.length);assert.ok(get('result-view').querySelectorAll('.result-info').some(n=>n.textContent.includes('截断')));
});

(async()=>{let failed=0;for(const [name,fn]of tests){try{await fn();console.log('PASS',name);}catch(e){failed++;console.error('FAIL',name,e.stack);}}console.log(`${tests.length-failed}/${tests.length} frontend behavior checks passed`);process.exitCode=failed?1:0;})();
