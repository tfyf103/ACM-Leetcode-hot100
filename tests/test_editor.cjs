// node --test tests/test_editor.cjs; editor logic without browser dependencies.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const support=require('../static/editor-support.js');

test('indentation respects tab stops and reports mixed leading whitespace',()=>{
  assert.deepEqual(support.indentation('        answer = 1'),{columns:8,mixed:false});
  assert.deepEqual(support.indentation('\t\tanswer'),{columns:8,mixed:false});
  assert.deepEqual(support.indentation('  \tanswer'),{columns:4,mixed:true});
  assert.deepEqual(support.indentation('answer = "  "'),{columns:0,mixed:false});
});
test('one-letter prefixes prefer names in the program, then Python builtins',()=>{
  const hints=support.suggestions('numbers = []\nnext_index = 0\nnode = None\nn','n');
  assert.deepEqual(hints.slice(0,3),['next_index','node','numbers']);
  assert.ok(hints.includes('next'));
  assert.ok(support.suggestions('','p').includes('print'));
  assert.equal(hints.includes('n'),false);
});
test('quoted, escaped, multiline and commented words do not pollute suggestions',()=>{
  const source='name = "not_variable\\\" still_string" # nonsense\ntext = \'\'\'nested_name\nnever_variable\'\'\'\nnumber = 2';
  assert.deepEqual(support.suggestions(source,'n').filter(x=>!['next','nonlocal','not'].includes(x)),['name','number']);
  assert.equal(support.maskStringsAndComments(source).length,source.length);
});
test('completion handles empty, numeric, underscore and case-sensitive prefixes',()=>{
  assert.deepEqual(support.suggestions('abc',''),[]);
  assert.deepEqual(support.suggestions('abc','1'),[]);
  assert.deepEqual(support.suggestions('_size = 3','_'),['_size']);
  assert.ok(!support.suggestions('Numbers=3','n').includes('Numbers'));
});

function editor(line='    numbers',ch=line.length,type='variable'){
  const listeners={},options={tabSize:4,indentUnit:4,readOnly:false};let lastHints,closed=0;
  const cm={on:(event,handler)=>listeners[event]=handler,getOption:key=>options[key],getCursor:()=>({line:0,ch}),
    getLine:()=>line,getValue:()=> 'numbers = []\nnext_index = 0\n'+line,getTokenAt:()=>({type}),
    somethingSelected:()=>false,defaultCharWidth:()=>8,removeLineClass(){},addLineClass(){},refresh(){},
    addKeyMap(map){this.keys=map;},showHint(settings){lastHints=settings.hint(this);},closeHint(){closed++;}};
  const controller=support.install(cm,{Pos:(line,ch)=>({line,ch})});
  return {cm,controller,listeners,options,hints:()=>lastHints,closed:()=>closed};
}
test('hint replaces the identifier as a whole when cursor is inside a word',()=>{
  const e=editor('    numbers',5);const hint=e.controller.hint(e.cm);
  assert.deepEqual(hint.from,{line:0,ch:4});assert.deepEqual(hint.to,{line:0,ch:11});
  assert.ok(hint.list.includes('next_index'));
});
test('strings, comments and attributes do not get unrelated variable hints',()=>{
  assert.equal(editor('"num',4,'string').controller.hint(editor('"num',4,'string').cm),null);
  const comment=editor('# num',5,'comment');assert.equal(comment.controller.hint(comment.cm),null);
  const member=editor('array.ap',8);assert.equal(member.controller.hint(member.cm),null);
});
test('read-only and disabled completion cannot open a popup',()=>{
  const e=editor('n',1);e.options.readOnly=true;e.cm.keys['Ctrl-Space']();assert.equal(e.hints(),undefined);
  e.options.readOnly=false;e.controller.setOptions({guides:true,completion:false});e.cm.keys['Ctrl-Space']();
  assert.equal(e.hints(),undefined);assert.ok(e.closed()>0);
});
test('indentation lines use measured character width and disappear when disabled',()=>{
  const e=editor();const element={style:{}};e.listeners.renderLine(e.cm,{text:'        pass'},element);
  assert.equal(element.style.backgroundPosition,'35px 0,67px 0');
  e.controller.setOptions({guides:false,completion:true});e.listeners.renderLine(e.cm,{text:'        pass'},element);
  assert.equal(element.style.backgroundImage,'');
});
test('refresh dismisses completion before cursor geometry changes',()=>{
  const e=editor('n',1);e.cm.keys['Ctrl-Space']();assert.ok(e.hints());
  const before=e.closed();e.listeners.refresh();assert.equal(e.closed(),before+1);
});
