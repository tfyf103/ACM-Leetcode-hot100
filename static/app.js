/* ACM Hot 100 — no build step, no network dependencies. */
"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const icons = {
    list:'<path d="M8 6h12M8 12h12M8 18h12"/><path d="M4 6h.01M4 12h.01M4 18h.01"/>',
    left:'<path d="m14 6-6 6 6 6"/>', right:'<path d="m10 6 6 6-6 6"/>',
    play:'<path d="m8 5 11 7-11 7z" fill="currentColor" stroke="none"/>',
    upload:'<path d="M12 16V3m-5 5 5-5 5 5M4 15v5h16v-5"/>',
    download:'<path d="M12 3v13m-5-5 5 5 5-5M4 16v5h16v-5"/>',
    timer:'<circle cx="12" cy="14" r="8"/><path d="M12 10v4l3 2M9 2h6m-3 0v4m6 0 2-2"/>',
    moon:'<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z"/>',
    sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
    settings:'<path d="m10 3-.7 2.1-2 .9-2.1-.4-2 3.5L4.6 11v2L3.2 15l2 3.4 2.2-.4 1.9 1 .7 2h4l.7-2 1.9-1 2.2.4 2-3.4-1.4-2v-2l1.4-1.9-2-3.5-2.1.4-2-.9L14 3z"/><circle cx="12" cy="12" r="3"/>',
    document:'<path d="M14 3H5v18h14V8zM14 3v5h5M8 12h8m-8 4h6"/>',
    bulb:'<path d="M9 18h6m-5 3h4M8 14a6 6 0 1 1 8 0c-1.5 1-1 2-1 2H9s.5-1-1-2Z"/>',
    history:'<path d="M3 11a9 9 0 1 1 2 7M3 5v6h6m3-4v5l3 2"/>',
    note:'<path d="M13 4H4v16h16v-9M10 14l1-4 8-8 3 3-8 8z"/>',
    star:'<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9z"/>',
    code:'<path d="m7 6-5 6 5 6m10-12 5 6-5 6M14 3l-4 18"/>',
    reset:'<path d="M3 10a9 9 0 1 1 2 8M3 4v6h6"/>',
    terminal:'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3m6 0h4"/>',
    checklist:'<path d="m3 6 2 2 3-4m3 2h10M3 12l2 2 3-4m3 2h10M3 18l2 2 3-4m3 2h10"/>',
    check:'<path d="m5 12 4 4L19 6"/>',
    circle:'<circle cx="12" cy="12" r="5"/>',
    attempt:'<circle cx="12" cy="12" r="7"/><path d="M12 8v4l3 2"/>',
    close:'<path d="m6 6 12 12M6 18 18 6"/>',
    search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    lock:'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10h.01"/>',
    copy:'<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>',
  };
  const svg = (name) => '<svg viewBox="0 0 24 24" aria-hidden="true">' + (icons[name] || icons.document) + '</svg>';
  document.querySelectorAll('[data-icon]').forEach((node) => { node.innerHTML = svg(node.dataset.icon); });
  const difficulty = {Easy:'简单', Medium:'中等', Hard:'困难'};
  const statusText = {'Accepted':'通过', 'Wrong Answer':'答案错误', 'Runtime Error':'运行出错', 'Time Limit Exceeded':'超出时间限制', 'Output Limit Exceeded':'超出输出限制', 'Finished':'运行完成'};
  const state = {problems:[], progress:{}, cache:new Map(), results:new Map(), inputs:new Map(), token:'', current:null, targetId:null, tab:'description', testTab:'testcase', navigation:0, loading:true, busy:false, importing:false, backupBusy:false, reloadRequired:false, revisions:{}, saved:{}, errors:new Set(), timers:new Map(), saves:Promise.resolve(), fontSize:14};
  let cm = null, suppressEditor = false, toastTimeout, drawerFocus = null, submissionRequest = 0;
  const store = {get(key, fallback=null) {try {const val=localStorage.getItem('acm-hot100:'+key); return val===null?fallback:JSON.parse(val);}catch (_) {return fallback;}}, set(key,val) {try{localStorage.setItem('acm-hot100:'+key,JSON.stringify(val));}catch (_) {}}};
  let unsavedDrafts = store.get('unsaved-drafts', {});
  if (!unsavedDrafts || typeof unsavedDrafts !== 'object' || Array.isArray(unsavedDrafts)) unsavedDrafts = {};

  function el(tag, className, text) {const node=document.createElement(tag); if(className) node.className=className; if(text!==undefined) node.textContent=text; return node;}
  function icon(name) {const n=el('span');n.innerHTML=svg(name);return n;}
  function toast(message) {clearTimeout(toastTimeout);$('toast').textContent=message;$('toast').hidden=false;toastTimeout=setTimeout(()=>{$('toast').hidden=true;},4000);}
  function empty(message, detail='') {const node=el('div','empty-state');node.append(el('p','',message));if(detail)node.append(el('small','',detail));return node;}
  function loading(message='正在加载…') {const node=el('div','loading-state');node.append(el('span','spinner'),document.createTextNode(message));return node;}
  function errorView(error, retry) {const node=el('div','error-state');node.append(el('p','',error.message || String(error)));if(retry){const b=el('button','secondary-button','重试');b.onclick=retry;node.append(b);}return node;}
  function isSolved(p) {return ['solved','Accepted','accepted'].includes(p && p.status);}
  function isAttempted(p) {return !isSolved(p) && p && ['attempted','Wrong Answer','Runtime Error','Time Limit Exceeded','Output Limit Exceeded'].includes(p.status);}
  function progress(id) {return state.progress[String(id)] || (state.progress[String(id)] = {});}
  function canEdit(id=state.current?.id) {return !!state.current&&state.current.id===id&&!state.loading&&!state.importing&&!state.reloadRequired;}
  function getCode() {return cm ? cm.getValue() : $('code').value;}
  function setCode(code) {suppressEditor=true;if(cm)cm.setValue(code);else $('code').value=code;suppressEditor=false;updateCursor();}
  function refreshEditor() {if(cm) requestAnimationFrame(()=>cm.refresh());}
  async function api(path, body) {
    const options = body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json','X-Local-Token':state.token},body:JSON.stringify(body)};
    const response=await fetch(path, options);let data;
    try {data=await response.json();}catch(_){throw new Error('本地服务返回了无效响应，请检查启动窗口。');}
    if(!response.ok) throw new Error(data.error || '请求失败（'+response.status+'）');return data;
  }

  function updateSaveStatus() {
    if(!state.current)return;
    const id=state.current.id, node=$('save-status');node.classList.toggle('error',state.errors.has(id));
    node.textContent=state.errors.has(id)?'保存失败 · 草稿暂存此浏览器':(state.saved[id]||0)<(state.revisions[id]||0)?'保存中…':'已保存';
  }
  function snapshot(id) {const p=progress(id), data={problem_id:id};['code','notes','favorite'].forEach(k=>{if(p[k]!==undefined)data[k]=p[k];});return data;}
  function persistDraft(id) {unsavedDrafts[id]=snapshot(id);store.set('unsaved-drafts',unsavedDrafts);}
  function scheduleSave(id) {
    state.revisions[id]=(state.revisions[id]||0)+1;persistDraft(id);clearTimeout(state.timers.get(id));
    state.timers.set(id,setTimeout(()=>flushSave(id),650));updateSaveStatus();
  }
  function flushSave(id) {
    clearTimeout(state.timers.get(id));state.timers.delete(id);
    const revision=state.revisions[id]||0;
    if(revision<=(state.saved[id]||0))return state.saves;
    const data=snapshot(id);
    state.saves=state.saves.then(async()=>{
      if(revision<=(state.saved[id]||0))return;
      try{
        await api('/api/progress',data);state.saved[id]=revision;state.errors.delete(id);
        if(revision===(state.revisions[id]||0)){delete unsavedDrafts[id];store.set('unsaved-drafts',unsavedDrafts);}
      }catch(err){state.errors.add(id);toast('自动保存失败：'+err.message);}finally{updateSaveStatus();}
    });return state.saves;
  }
  async function flushAll() {for(const p of state.problems)if((state.revisions[p.id]||0)>(state.saved[p.id]||0))flushSave(p.id);await state.saves;}
  function codeChanged() {if(suppressEditor||!canEdit())return;progress(state.current.id).code=getCode();scheduleSave(state.current.id);}
  function updateCursor() {let line=1,col=1;if(cm){const p=cm.getCursor();line=p.line+1;col=p.ch+1;}else{const before=$('code').value.slice(0,$('code').selectionStart);line=before.split('\n').length;col=before.length-before.lastIndexOf('\n');}$('cursor-position').textContent='Ln '+line+', Col '+col;}

  if(window.CodeMirror){
    cm=CodeMirror.fromTextArea($('code'),{mode:'python',lineNumbers:true,indentUnit:4,tabSize:4,indentWithTabs:false,lineWrapping:false,matchBrackets:true,autoCloseBrackets:true,viewportMargin:20,extraKeys:{Tab(cm){if(cm.somethingSelected())cm.indentSelection('add');else cm.replaceSelection(' '.repeat(4-(cm.getCursor().ch%4)),'end');},'Shift-Tab':cm=>cm.indentSelection('subtract'),'Ctrl-Enter':()=>execute(false),'Shift-Ctrl-Enter':()=>execute(true),'Cmd-Enter':()=>execute(false),'Shift-Cmd-Enter':()=>execute(true)}});
    cm.on('change',codeChanged);cm.on('cursorActivity',updateCursor);
  } else {
    $('code').addEventListener('input',codeChanged);['click','keyup','select'].forEach(e=>$('code').addEventListener(e,updateCursor));
    $('code').addEventListener('keydown',e=>{if(e.key==='Tab'){e.preventDefault();const t=$('code'),start=t.selectionStart,end=t.selectionEnd;t.setRangeText('    ',start,end,'end');codeChanged();updateCursor();}});
  }
  function setEditorEnabled(enabled){enabled=enabled&&!state.importing&&!state.reloadRequired;if(cm)cm.setOption('readOnly',!enabled);$('code').disabled=!enabled;$('notes').disabled=!enabled;$('stdin').disabled=!enabled;['reset-code','download-code','favorite'].forEach(id=>$(id).disabled=!enabled);updateExecutionButtons();}
  function updateExecutionButtons(){['run','submit'].forEach(id=>$(id).disabled=state.busy||state.backupBusy||state.loading||state.reloadRequired||!state.current);}
  setEditorEnabled(false);

  function renderDescription(problem) {
    const view=$('description-view');view.replaceChildren();
    const titleRow=el('div','problem-title-row');titleRow.append(el('h1','problem-title',problem.id+'. '+problem.title));
    if(isSolved(progress(problem.id))){const badge=el('span','solved-badge');badge.append(document.createTextNode('已解答'),icon('check'));titleRow.append(badge);}view.append(titleRow);
    const tags=el('div','problem-tags');tags.append(el('span','tag difficulty-'+problem.difficulty,difficulty[problem.difficulty]||problem.difficulty),el('span','tag',problem.category),el('span','tag acm-tag','ACM 模式'));view.append(tags);
    view.append(el('p','description-text',problem.description));
    const addSection=(title,text)=>{const section=el('section','problem-section');section.append(el('h3','',title),el('p','format-text',text));view.append(section);};
    addSection('输入格式',problem.input_format);addSection('输出格式',problem.output_format);
    (problem.examples||[]).forEach((example,index)=>{
      const section=el('section','problem-section');section.append(el('h3','example-heading','示例 '+(index+1)+'：'));
      const block=el('div','example-block');[['输入：',example.input],['输出：',example.output]].forEach(([label,text])=>{const part=el('div','example-part');part.append(el('b','',label),el('pre','',text));block.append(part);});
      if(example.explanation)block.append(el('p','example-explanation','解释：'+example.explanation));section.append(block);view.append(section);
    });
    if(problem.constraints && problem.constraints.length){const section=el('section','problem-section');section.append(el('h3','','提示：'));const list=el('ul','constraints');problem.constraints.forEach(c=>list.append(el('li','',c)));section.append(list);view.append(section);}
    const note=el('div','acm-notice');note.append(icon('info'),el('span','','请编写可独立运行的 Python 3 程序，从标准输入读取数据，向标准输出打印答案。无需定义 Solution 类。'));view.append(note);
  }
  function renderFavorite(){if(!state.current)return;const value=!!progress(state.current.id).favorite;$('favorite').classList.toggle('is-favorite',value);$('favorite').setAttribute('aria-pressed',String(value));$('favorite').lastElementChild.textContent=value?'已收藏':'收藏';}
  function renderCases(){
    if(!state.current)return;const p=state.current,id=p.id;
    if(!state.inputs.has(id)){const value=p.examples?.[0]?.input||'';state.inputs.set(id,{value,customValue:value,active:0});}
    const input=state.inputs.get(id);$('stdin').value=input.value;$('case-buttons').replaceChildren();
    (p.examples||[]).forEach((example,index)=>{const button=el('button','case-button'+(input.active===index?' active':''),'示例 '+(index+1));button.onclick=()=>{if(!canEdit(id))return;input.value=example.input;input.active=index;renderCases();};$('case-buttons').append(button);});
    const custom=el('button','case-button'+(input.active===-1?' active':''),'自定义');custom.onclick=()=>{if(!canEdit(id))return;input.value=input.customValue;input.active=-1;renderCases();$('stdin').focus();};$('case-buttons').append(custom);
  }
  async function openProblem(id, {updateHash=true}={}) {
    if(state.importing)return;
    if(state.reloadRequired){toast('请先刷新页面，重新读取导入的数据');return;}
    id=Number(id);if(!state.problems.some(p=>p.id===id))id=state.problems[0]?.id;if(!id)return;
    if(state.current?.id===id&&!state.loading){closeDrawer();return;}
    if(state.current)flushSave(state.current.id);
    state.loading=true;state.targetId=id;const navigation=++state.navigation;setEditorEnabled(false);closeDrawer();
    $('description-view').replaceChildren(loading('正在加载题目…'));$('solution-view').replaceChildren(loading());$('submissions-view').replaceChildren(loading());
    try{
      const problem=state.cache.get(id)||await api('/api/problems/'+id);state.cache.set(id,problem);
      if(navigation!==state.navigation)return;
      state.current=problem;state.loading=false;
      const p=progress(id);if(typeof p.code!=='string')p.code=problem.starter||'';setCode(p.code);$('notes').value=p.notes||'';
      if(cm)cm.clearHistory();renderDescription(problem);renderFavorite();renderCases();renderResult();
      const position=state.problems.findIndex(p=>p.id===id);$('problem-position').textContent=(position+1)+' / '+state.problems.length;
      $('previous').disabled=position===0;$('next').disabled=position===state.problems.length-1;
      if(updateHash)history.replaceState(null,'','#'+id);store.set('last-problem',id);document.title=problem.id+'. '+problem.title+' · ACM Hot 100';
      setEditorEnabled(true);updateSaveStatus();renderList();activateTab(state.tab);refreshEditor();document.querySelector('.problem-scroll').scrollTop=0;
    }catch(err){if(navigation!==state.navigation)return;state.loading=false;state.current=null;setEditorEnabled(false);$('description-view').replaceChildren(errorView(err,()=>openProblem(id)));activateTab('description');}
  }
  function navigate(direction){const id=state.targetId||state.current?.id,position=state.problems.findIndex(p=>p.id===id);const next=state.problems[position+direction];if(next)openProblem(next.id);}
  function activateTab(tab){
    state.tab=tab;document.querySelectorAll('[data-tab]').forEach(b=>{const active=b.dataset.tab===tab;b.classList.toggle('active',active);b.setAttribute('aria-selected',String(active));});
    ['description','solution','submissions','notes'].forEach(t=>$(t+'-view').hidden=t!==tab);
    if(state.loading||!state.current)return;
    if(tab==='solution')loadSolution(state.current.id);if(tab==='submissions')loadSubmissions(state.current.id);
  }
  async function loadSolution(id){
    $('solution-view').replaceChildren(loading('正在加载题解…'));
    try{const data=await api('/api/problems/'+id+'/solution');if(state.current?.id!==id||state.loading)return;
      const view=$('solution-view');view.replaceChildren();const head=el('div','section-heading');head.append(el('h2','','参考题解'),el('span','muted','Python 3 · ACM'));view.append(head,el('div','solution-explanation',data.explanation));
      const code=el('pre','solution-code',data.solution);view.append(code);const actions=el('div','solution-actions');const copy=el('button','secondary-button');copy.append(icon('copy'),document.createTextNode('复制代码'));copy.onclick=()=>copyText(data.solution);
      const apply=el('button','secondary-button','放入编辑器');apply.onclick=()=>{if(!canEdit(id))return;if(!confirm('用参考解法替换当前代码？当前代码将被覆盖。'))return;setCode(data.solution);codeChanged();toast('参考解法已放入编辑器');};actions.append(copy,apply);view.append(actions);
    }catch(err){if(state.current?.id===id)$('solution-view').replaceChildren(errorView(err,()=>loadSolution(id)));}
  }
  async function loadSubmissions(id){
    const request=++submissionRequest;
    $('submissions-view').replaceChildren(loading('正在加载提交记录…'));
    try{const data=await api('/api/problems/'+id+'/submissions');if(state.current?.id!==id||state.loading||request!==submissionRequest)return;const view=$('submissions-view');view.replaceChildren();
      const head=el('div','section-heading');head.append(el('h2','','提交记录'),el('span','muted',(data.submissions||[]).length+' 次提交'));view.append(head);
      if(!data.submissions?.length){view.append(empty('还没有提交记录','写好代码后，点击顶部「提交」检查全部用例。'));return;}
      const details=el('div','submission-detail');
      data.submissions.forEach(sub=>{
        const row=el('button','submission-row'),primary=el('span','submission-primary');primary.append(el('strong',sub.status==='Accepted'?'accepted':'',statusText[sub.status]||sub.status),el('small','',formatDate(sub.created_at)));
        const meta=el('span','submission-meta',sub.passed+' / '+sub.total+' 用例 · '+formatTime(sub.elapsed_ms));row.append(primary,meta,icon('right'));
        row.onclick=()=>{details.replaceChildren(el('h3','','本次提交的代码'),el('pre','submission-code',sub.code));const restore=el('button','secondary-button','恢复这份代码');restore.onclick=()=>{if(!canEdit(id))return;if(!confirm('用这次提交的代码替换当前代码？'))return;setCode(sub.code);codeChanged();toast('已恢复提交代码');};details.append(restore);details.scrollIntoView({behavior:'smooth',block:'nearest'});};view.append(row);
      });view.append(details);
    }catch(err){if(state.current?.id===id&&request===submissionRequest)$('submissions-view').replaceChildren(errorView(err,()=>loadSubmissions(id)));}
  }
  function formatDate(value){let date=new Date(typeof value==='number'&&value<1e12?value*1000:value);return Number.isNaN(date.getTime())?String(value||''):date.toLocaleString('zh-CN',{hour12:false});}
  function formatTime(ms){return Number.isFinite(Number(ms))?Math.round(Number(ms))+' ms':'—';}
  function activateTestTab(tab){state.testTab=tab;document.querySelectorAll('[data-test-tab]').forEach(b=>{const active=b.dataset.testTab===tab;b.classList.toggle('active',active);b.setAttribute('aria-selected',String(active));});$('testcase-view').hidden=tab!=='testcase';$('result-view').hidden=tab!=='result';if(tab==='result')$('result-dot').hidden=true;}
  function resultSection(container,label,value,error=false){
    const section=el('div','result-section'),text=value===undefined||value===''?'（空）':String(value),limit=65536;
    section.append(el('label','',label),el('pre','result-pre'+(error?' error-output':''),text.slice(0,limit)));
    if(text.length>limit)section.append(el('p','result-info','内容较长，仅显示前 65,536 个字符。显示截断不影响运行和判题使用的完整数据。'));
    container.append(section);
  }
  function renderResult(){
    const view=$('result-view'),record=state.results.get(state.current?.id);view.replaceChildren();
    if(!record){const node=el('div','empty-result');node.append(icon('terminal'),el('p','','运行代码，查看测试结果'),el('span','','运行测试当前输入 · 提交检查全部内置用例'));view.append(node);return;}
    if(record.pending){view.append(loading(record.submit?'正在检查全部内置用例…':'正在运行 Python 代码…'));return;}
    if(record.error){view.append(errorView(record.error));return;}
    const data=record.data,success=data.status==='Accepted'||data.status==='Finished';
    const head=el('div','result-heading');head.append(el('span','result-status'+(success?'':' failure'),statusText[data.status]||data.status),el('span','result-metrics',(record.submit?data.passed+' / '+data.total+' 用例通过 · ':'')+formatTime(data.elapsed_ms)));view.append(head);
    if(record.submit){
      if(data.status==='Accepted'){const banner=el('div','result-success');banner.append(icon('check'),el('span','','全部内置用例通过'));view.append(banner,el('p','result-info','已记录本次提交。内置评测覆盖常见情况，不能保证覆盖全部边界。'));}
      if(data.case){const c=data.case;view.append(el('p','result-info','未通过用例'+(c.index!==undefined?' '+c.index:'')));resultSection(view,'输入',c.input);resultSection(view,'预期输出',c.expected);resultSection(view,'实际输出',c.actual);if(c.stderr)resultSection(view,'错误信息',c.stderr,true);}
    }else{resultSection(view,'标准输出 stdout',data.stdout);if(data.stderr)resultSection(view,'错误信息 stderr',data.stderr,true);view.append(el('p','result-info','运行仅执行当前输入，不判断答案。点击「提交」进行评测。'));}
  }
  async function execute(submit){
    if(state.loading||state.busy||state.backupBusy||state.reloadRequired||!state.current)return;const id=state.current.id,code=getCode(),stdin=$('stdin').value;
    state.busy=true;updateExecutionButtons();state.results.set(id,{pending:true,submit});activateTestTab('result');renderResult();
    const button=$(submit?'submit':'run'),previous=button.innerHTML;button.replaceChildren(el('span','spinner'),document.createTextNode(submit?'评测中':'运行中'));
    try{
      const data=await api(submit?'/api/submit':'/api/run',submit?{problem_id:id,code}:{problem_id:id,code,stdin});state.results.set(id,{data,submit});
      if(submit){const p=progress(id);if(data.status==='Accepted')p.status='solved';else if(!isSolved(p))p.status='attempted';renderList();if(state.current?.id===id){renderDescription(state.current);if(state.tab==='submissions')loadSubmissions(id);}}
      if(state.current?.id===id){renderResult();if(state.testTab!=='result')$('result-dot').hidden=false;}else toast(id+' 题：'+(statusText[data.status]||data.status));
    }catch(error){state.results.set(id,{error,submit});if(state.current?.id===id)renderResult();else toast(id+' 题执行失败：'+error.message);}
    finally{state.busy=false;button.innerHTML=previous;updateExecutionButtons();}
  }

  function renderList(){
    const solved=state.problems.filter(p=>isSolved(progress(p.id))).length;$('solved-count').textContent=solved;$('total-count').textContent=state.problems.length;$('progress-fill').style.width=(state.problems.length?solved/state.problems.length*100:0)+'%';
    $('difficulty-progress').replaceChildren();Object.keys(difficulty).forEach(d=>{const list=state.problems.filter(p=>p.difficulty===d),node=el('span','difficulty-'+d,difficulty[d]);node.append(el('b','',list.filter(p=>isSolved(progress(p.id))).length+'/'+list.length));$('difficulty-progress').append(node);});
    const q=$('problem-search').value.trim().toLowerCase(),category=$('category-filter').value,d=$('difficulty-filter').value,status=$('status-filter').value;
    const filtered=state.problems.filter(p=>{const pr=progress(p.id);return(!q||(p.id+' '+p.title+' '+p.slug).toLowerCase().includes(q))&&(!category||p.category===category)&&(!d||p.difficulty===d)&&(!status||(status==='solved'?isSolved(pr):status==='attempted'?isAttempted(pr):status==='favorite'?pr.favorite:!isSolved(pr)&&!isAttempted(pr)));});
    $('filtered-count').textContent=filtered.length+' 道题目';const list=$('problem-list');list.replaceChildren();let lastCategory='';
    if(!filtered.length){list.append(empty('没有找到匹配的题目','试试其他关键词或筛选条件。'));return;}
    filtered.forEach(p=>{if(p.category!==lastCategory){list.append(el('div','list-category',p.category));lastCategory=p.category;}
      const pr=progress(p.id),row=el('button','problem-item'+(state.current?.id===p.id?' current':''));row.title=p.id+'. '+p.title;const solved=isSolved(pr),attempted=isAttempted(pr),status=el('span','list-status'+(solved?' solved':attempted?' attempted':''));status.innerHTML=svg(solved?'check':attempted?'attempt':'circle');
      const name=el('span','problem-name');name.append(el('span','problem-id',p.id+'.'),document.createTextNode(p.title));row.append(status,name);if(pr.favorite)row.append(el('span','list-star','★'));row.append(el('span','difficulty-label difficulty-'+p.difficulty,difficulty[p.difficulty]||p.difficulty));row.onclick=()=>openProblem(p.id);list.append(row);
    });
  }
  function openDrawer(){drawerFocus=document.activeElement;$('drawer-backdrop').hidden=false;$('problem-drawer').classList.add('open');$('problem-drawer').removeAttribute('inert');$('problem-drawer').setAttribute('aria-hidden','false');$('list-toggle').setAttribute('aria-expanded','true');$('problem-search').focus();}
  function closeDrawer(){const wasOpen=$('problem-drawer').classList.contains('open');$('drawer-backdrop').hidden=true;$('problem-drawer').classList.remove('open');$('problem-drawer').setAttribute('inert','');$('problem-drawer').setAttribute('aria-hidden','true');$('list-toggle').setAttribute('aria-expanded','false');if(wasOpen&&drawerFocus?.isConnected)drawerFocus.focus();}
  $('list-toggle').onclick=()=>openDrawer();$('close-list').onclick=closeDrawer;$('drawer-backdrop').onclick=closeDrawer;
  $('previous').onclick=()=>navigate(-1);$('next').onclick=()=>navigate(1);
  ['problem-search','category-filter','difficulty-filter','status-filter'].forEach(id=>$(id).addEventListener(id==='problem-search'?'input':'change',renderList));
  document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>activateTab(b.dataset.tab));document.querySelectorAll('[data-test-tab]').forEach(b=>b.onclick=()=>activateTestTab(b.dataset.testTab));
  $('favorite').onclick=()=>{if(!canEdit())return;const id=state.current.id;progress(id).favorite=!progress(id).favorite;scheduleSave(id);renderFavorite();renderList();};
  $('notes').oninput=()=>{if(!canEdit())return;progress(state.current.id).notes=$('notes').value;scheduleSave(state.current.id);};
  $('stdin').oninput=()=>{if(!canEdit())return;const value=$('stdin').value;state.inputs.set(state.current.id,Object.assign(state.inputs.get(state.current.id)||{},{value,customValue:value,active:-1}));$('case-buttons').querySelectorAll('.case-button').forEach((b,i,all)=>b.classList.toggle('active',i===all.length-1));};
  $('run').onclick=()=>execute(false);$('submit').onclick=()=>execute(true);
  $('reset-code').onclick=()=>{if(!canEdit()||!confirm('恢复初始代码？当前编辑器中的代码将被覆盖。'))return;setCode(state.current.starter||'');codeChanged();toast('已恢复初始代码');};
  function download(name,content,type){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),link=el('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);}
  $('download-code').onclick=()=>{if(state.current)download(state.current.id+'_'+(state.current.slug||'solution')+'.py',getCode(),'text/x-python;charset=utf-8');};
  async function copyText(text){try{await navigator.clipboard.writeText(text);toast('已复制代码');}catch(_){const t=el('textarea');t.value=text;t.style.cssText='position:fixed;left:-9999px';document.body.append(t);t.select();const ok=document.execCommand('copy');t.remove();toast(ok?'已复制代码':'复制失败，请手动选择代码复制');}}
  function setFont(size){state.fontSize=Math.max(11,Math.min(22,size));document.documentElement.style.setProperty('--code-size',state.fontSize+'px');store.set('font-size',state.fontSize);$('font-decrease').disabled=state.fontSize<=11;$('font-increase').disabled=state.fontSize>=22;refreshEditor();}
  setFont(Number(store.get('font-size',14))||14);$('font-decrease').onclick=()=>setFont(state.fontSize-1);$('font-increase').onclick=()=>setFont(state.fontSize+1);
  function setTheme(dark){document.body.classList.toggle('dark',dark);$('theme').innerHTML=svg(dark?'sun':'moon');store.set('dark',dark);document.querySelector('meta[name=theme-color]').content=dark?'#1a1a1a':'#f0f0f0';}
  setTheme(!!store.get('dark',false));$('theme').onclick=()=>setTheme(!document.body.classList.contains('dark'));

  let timerElapsed=Number(store.get('timer',0))||0,timerStarted=null;
  function paintTimer(){const elapsed=timerElapsed+(timerStarted?Date.now()-timerStarted:0),seconds=Math.floor(elapsed/1000),minutes=Math.floor(seconds/60),hours=Math.floor(minutes/60);$('timer-text').textContent=(hours?String(hours).padStart(2,'0')+':':'')+String(minutes%60).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');$('timer').classList.toggle('running',timerStarted!==null);$('timer').setAttribute('aria-pressed',String(timerStarted!==null));}
  $('timer').onclick=()=>{if(timerStarted!==null){timerElapsed+=Date.now()-timerStarted;timerStarted=null;store.set('timer',timerElapsed);}else timerStarted=Date.now();paintTimer();};paintTimer();setInterval(paintTimer,1000);
  $('help').onclick=()=>{$('help-dialog').showModal();};$('close-help').onclick=()=>{$('help-dialog').close();};$('help-dialog').addEventListener('click',e=>{if(e.target===$('help-dialog')){const r=$('help-dialog').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('help-dialog').close();}});
  $('reset-timer').onclick=()=>{timerElapsed=0;timerStarted=null;store.set('timer',0);paintTimer();toast('计时器已重置');};
  function setBackupBusy(busy){state.backupBusy=busy;['export-data','import-data'].forEach(id=>$(id).disabled=busy);updateExecutionButtons();}
  $('export-data').onclick=async()=>{
    if(state.backupBusy)return;if(state.busy){toast('请等待当前代码运行结束后再导出备份');return;}
    setBackupBusy(true);
    try{await flushAll();if(state.errors.size)throw new Error('部分草稿尚未保存，请先恢复服务连接后再导出。');const data=await api('/api/export');download('acm-hot100-backup-'+new Date().toISOString().slice(0,10)+'.json',JSON.stringify(data,null,2),'application/json');toast('备份已导出');}catch(e){toast('导出失败：'+e.message);}finally{setBackupBusy(false);}
  };
  $('import-data').onclick=()=>{if(!state.backupBusy)$('import-file').click();};$('import-file').onchange=async()=>{
    const file=$('import-file').files[0];if(!file)return;$('import-file').value='';
    if(state.backupBusy)return;
    if(state.busy){toast('请等待当前代码运行结束后再导入备份');return;}
    if(state.loading){toast('请等待题目加载完成后再导入备份');return;}
    if(file.size>32*1024*1024){toast('备份文件过大，请使用不超过 32 MiB 的 JSON 文件');return;}
    if(!confirm('导入后会合并备份中的进度、代码和笔记。相同题目的当前数据可能被覆盖，建议先导出备份。继续导入？'))return;
    setBackupBusy(true);state.importing=true;setEditorEnabled(false);++submissionRequest;
    let imported=false;
    try{
      const data=JSON.parse(await file.text());await flushAll();if(state.errors.size)throw new Error('当前草稿未能保存，请恢复连接后重试。');
      await api('/api/import',data);imported=true;
      const boot=await api('/api/bootstrap');state.progress=boot.progress||{};state.token=boot.token;state.reloadRequired=false;
      const id=state.current?.id||state.targetId||state.problems[0]?.id;state.current=null;state.cache.clear();state.results.clear();renderList();state.importing=false;if(id)await openProblem(id);toast('备份已导入');
    }catch(e){
      if(imported){state.current=null;state.loading=false;state.reloadRequired=true;$('description-view').replaceChildren(errorView(new Error('备份已导入，但页面刷新失败。请刷新页面后继续，避免覆盖导入的数据。\n'+e.message),()=>location.reload()));activateTab('description');toast('备份已导入，请刷新页面重新加载');}
      else toast('导入失败：'+e.message);
    }finally{state.importing=false;setBackupBusy(false);setEditorEnabled(!!state.current&&!state.loading);}
  };

  function divider(id,axis){const node=$(id);let start;
    const adjust=(value)=>{if(axis==='x'){const percent=Math.max(28,Math.min(68,value));document.documentElement.style.setProperty('--left-width',percent+'%');store.set('left-width',percent);}else{const percent=Math.max(20,Math.min(66,value));document.documentElement.style.setProperty('--test-height',percent+'%');store.set('test-height',percent);}refreshEditor();};
    node.onpointerdown=e=>{if(e.button!==0)return;e.preventDefault();node.setPointerCapture(e.pointerId);start=true;document.body.classList.add('resizing');};
    node.onpointermove=e=>{if(!start)return;const r=(axis==='x'?$('workspace'):document.querySelector('.right-column')).getBoundingClientRect();adjust(axis==='x'?(e.clientX-r.left)/r.width*100:(r.bottom-e.clientY)/r.height*100);};
    const stop=()=>{start=false;document.body.classList.remove('resizing');refreshEditor();};node.onpointerup=stop;node.onpointercancel=stop;
    node.onkeydown=e=>{const property=axis==='x'?'--left-width':'--test-height',current=parseFloat(getComputedStyle(document.documentElement).getPropertyValue(property));if((axis==='x'&&['ArrowLeft','ArrowRight'].includes(e.key))||(axis==='y'&&['ArrowUp','ArrowDown'].includes(e.key))){e.preventDefault();adjust(current+(['ArrowRight','ArrowUp'].includes(e.key)?2:-2));}};
  }
  const left=Number(store.get('left-width',50)),test=Number(store.get('test-height',32));document.documentElement.style.setProperty('--left-width',Math.max(28,Math.min(68,left))+'%');document.documentElement.style.setProperty('--test-height',Math.max(20,Math.min(66,test))+'%');divider('column-divider','x');divider('row-divider','y');
  if(window.ResizeObserver)new ResizeObserver(refreshEditor).observe($('editor-container'));
  document.addEventListener('keydown',e=>{
    if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){if(e.defaultPrevented)return;e.preventDefault();execute(e.shiftKey);return;}
    if(e.key==='Escape')closeDrawer();
    if(e.key==='/'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName)&&!document.activeElement?.isContentEditable&&!document.activeElement?.closest('.CodeMirror')){e.preventDefault();openDrawer();}
    if(e.key==='Tab'&&$('problem-drawer').classList.contains('open')){const focusable=Array.from($('problem-drawer').querySelectorAll('button:not([disabled]),input,select')).filter(n=>n.offsetParent!==null),first=focusable[0],last=focusable[focusable.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}
  });
  window.addEventListener('hashchange',()=>{if(state.problems.length)openProblem(location.hash.slice(1),{updateHash:false});});
  window.addEventListener('beforeunload',()=>{store.set('timer',timerElapsed+(timerStarted?Date.now()-timerStarted:0));for(const [id] of state.timers){persistDraft(id);}});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){if(state.current)flushSave(state.current.id);store.set('timer',timerElapsed+(timerStarted?Date.now()-timerStarted:0));}});
  window.addEventListener('online',()=>{for(const id of state.errors)flushSave(id);});

  async function bootstrap(){
    try{
      const data=await api('/api/bootstrap');state.problems=data.problems||[];state.progress=data.progress||{};state.token=data.token;
      if(!state.problems.length)throw new Error('题库为空，请检查 catalog 目录。');
      Object.entries(unsavedDrafts).forEach(([id,draft])=>{if(!state.problems.some(p=>p.id===Number(id)))return;const pr=progress(id);['code','notes','favorite'].forEach(k=>{if(draft[k]!==undefined)pr[k]=draft[k];});state.revisions[id]=1;flushSave(Number(id));});
      $('python-version').textContent='Python '+data.python_version;$('help-runtime').textContent='Python '+data.python_version;
      const categories=[...new Set(state.problems.map(p=>p.category))];categories.forEach(c=>{const option=el('option','',c);option.value=c;$('category-filter').append(option);});renderList();
      const initial=Number(location.hash.slice(1))||Number(store.get('last-problem',1))||1;await openProblem(initial);
    }catch(error){const view=$('description-view');view.replaceChildren(errorView(new Error('无法连接本地题库。\n'+error.message),()=>location.reload()));state.loading=false;setEditorEnabled(false);toast('加载失败，请检查本地服务是否已启动');}
  }
  bootstrap();
})();
