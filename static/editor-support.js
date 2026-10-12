/* Offline indentation guides and lexical Python completion; no code execution. */
(function(root, factory) {
  const support=factory();
  if(typeof module==='object'&&module.exports)module.exports=support;
  else root.ACMEditor=support;
})(typeof window==='object'?window:globalThis,function(){
  'use strict';
  const keywords='and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield False None True'.split(' ');
  const builtins='abs all any bool bytes dict enumerate filter float input int isinstance len list map max min next open ord pow print range reversed round set sorted str sum tuple zip'.split(' ');
  function indentation(text,tabSize=4){
    let columns=0,spaces=false,tabs=false;
    for(const char of text){if(char===' '){columns++;spaces=true;}else if(char==='\t'){columns+=tabSize-columns%tabSize;tabs=true;}else break;}
    return {columns,mixed:spaces&&tabs};
  }
  function maskStringsAndComments(source){
    let result='',quote='',triple=false,comment=false;
    for(let i=0;i<source.length;i++){
      const char=source[i];
      if(comment){if(char==='\n')comment=false;result+=char==='\n'?'\n':' ';continue;}
      if(quote){
        if(char==='\\'){result+=' ';if(i+1<source.length){i++;result+=source[i]==='\n'?'\n':' ';}}
        else if(char===quote&&(!triple||source.slice(i,i+3)===quote.repeat(3))){result+=' '.repeat(triple?3:1);if(triple)i+=2;quote='';triple=false;}
        else result+=char==='\n'?'\n':' ';
      }else if(char==='#'){comment=true;result+=' ';}
      else if(char==='"'||char==="'"){quote=char;triple=source.slice(i,i+3)===char.repeat(3);result+=' '.repeat(triple?3:1);if(triple)i+=2;}
      else result+=char;
    }
    return result;
  }
  function suggestions(source,prefix){
    if(!/^[A-Za-z_][A-Za-z_0-9]*$/.test(prefix))return [];
    const words=new Set(maskStringsAndComments(source).match(/[A-Za-z_][A-Za-z_0-9]*/g)||[]);
    const reserved=new Set([...keywords,...builtins]),matching=word=>word.startsWith(prefix)&&word!==prefix;
    return [...Array.from(words).filter(word=>!reserved.has(word)&&matching(word)).sort(),...builtins.filter(matching).sort(),...keywords.filter(matching).sort()].slice(0,40);
  }
  function install(cm,CodeMirror,options={}){
    let guides=options.guides!==false,completion=options.completion!==false,activeLine=null,hintTimer=null;
    function render(editor,line,element){
      ['backgroundImage','backgroundPosition','backgroundSize','backgroundRepeat'].forEach(key=>element.style[key]='');
      if(!guides)return;
      const columns=indentation(line.text,editor.getOption('tabSize')).columns,unit=editor.getOption('indentUnit'),width=editor.defaultCharWidth(),positions=[];
      for(let col=unit;col<=columns;col+=unit)positions.push((col*width+3)+'px 0');
      if(positions.length){element.style.backgroundImage=positions.map(()=> 'linear-gradient(var(--indent-guide),var(--indent-guide))').join(',');element.style.backgroundPosition=positions.join(',');element.style.backgroundSize=positions.map(()=> '1px 100%').join(',');element.style.backgroundRepeat='no-repeat';}
    }
    function highlight(){if(activeLine!==null)cm.removeLineClass(activeLine,'background','acm-active-line');activeLine=cm.getCursor().line;if(guides)cm.addLineClass(activeLine,'background','acm-active-line');}
    function hint(editor){
      const cursor=editor.getCursor(),line=editor.getLine(cursor.line),token=editor.getTokenAt(cursor);
      if(token.type&&/comment|string/.test(token.type))return null;
      const before=line.slice(0,cursor.ch),match=before.match(/[A-Za-z_][A-Za-z_0-9]*$/);
      if(!match||/\.[A-Za-z_0-9]*$/.test(before)||editor.somethingSelected())return null;
      const prefix=match[0],from=cursor.ch-prefix.length;
      if(from>0&&/[A-Za-z_0-9]/.test(line[from-1]))return null;
      let end=cursor.ch;while(end<line.length&&/[A-Za-z_0-9]/.test(line[end]))end++;
      const list=suggestions(editor.getValue(),prefix);
      return list.length?{list,from:CodeMirror.Pos(cursor.line,from),to:CodeMirror.Pos(cursor.line,end)}:null;
    }
    function show(){if(completion&&!cm.getOption('readOnly')&&cm.showHint)cm.showHint({hint,completeSingle:false});}
    function close(){clearTimeout(hintTimer);if(cm.closeHint)cm.closeHint();}
    cm.on('renderLine',render);cm.on('cursorActivity',highlight);
    cm.on('inputRead',(editor,change)=>{clearTimeout(hintTimer);if(!completion||change.origin!=='+input'||change.text.length!==1||! /^[A-Za-z_]$/.test(change.text[0]))return;hintTimer=setTimeout(show,100);});
    cm.on('blur',()=>clearTimeout(hintTimer));cm.on('refresh',close);
    if(typeof window==='object')window.addEventListener('resize',close);
    cm.addKeyMap({'Ctrl-Space':show,'Cmd-Space':show});highlight();cm.refresh();
    return {setOptions(next){guides=next.guides;completion=next.completion;clearTimeout(hintTimer);if(!completion&&cm.closeHint)cm.closeHint();highlight();cm.refresh();},hint};
  }
  return {indentation,maskStringsAndComments,suggestions,install};
});
