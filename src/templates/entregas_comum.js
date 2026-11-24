const $=id=>document.getElementById(id);
const format=new Intl.NumberFormat('pt-BR',{maximumFractionDigits:6});
const fmt=v=>v===null||v===undefined||v===''?'—':typeof v==='number'?format.format(v):String(v);
function el(tag,text,className){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(className)n.className=className;return n;}
function link(item,download=false){const a=el('a',item.nome);a.href=item.href;if(download)a.download='';return a;}
function table(id,columns,rows,caption,empty='Nenhum registro para esta consulta.'){
 const host=$(id);host.replaceChildren();let page=0,sortKey=null,asc=true;const size=40;
 function draw(){host.replaceChildren();if(!rows.length){host.append(el('div',empty,'empty'));return;}
  const ordered=[...rows];if(sortKey!==null)ordered.sort((a,b)=>{const x=a[sortKey],y=b[sortKey];const numeric=x!==null&&y!==null&&x!==''&&y!==''&&Number.isFinite(Number(x))&&Number.isFinite(Number(y));const c=numeric?Number(x)-Number(y):String(x??'').localeCompare(String(y??''),'pt-BR');return asc?c:-c;});
  const wrap=el('div',undefined,'table-wrap'),t=el('table');wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label',caption);t.append(el('caption',caption));const head=el('thead'),tr=el('tr');
  for(const c of columns){const th=el('th');th.scope='col';if(c.key===sortKey)th.setAttribute('aria-sort',asc?'ascending':'descending');const b=el('button',c.label+(c.key===sortKey?(asc?' ↑':' ↓'):''));b.type='button';b.title='Ordenar por '+c.label;b.onclick=()=>{asc=sortKey===c.key?!asc:true;sortKey=c.key;page=0;draw();};th.append(b);tr.append(th);}head.append(tr);t.append(head);
  const body=el('tbody');for(const row of ordered.slice(page*size,(page+1)*size)){const tr=el('tr');for(const c of columns){const td=el('td',c.display?c.display(row[c.key],row):fmt(row[c.key]),c.code?'code':'');tr.append(td);}body.append(tr);}t.append(body);wrap.append(t);host.append(wrap);
  if(rows.length>size){const bar=el('div',undefined,'pagination');bar.append(el('span',`${page*size+1}–${Math.min((page+1)*size,rows.length)} de ${format.format(rows.length)} registros`));const prev=el('button','← Anterior'),next=el('button','Próxima →');prev.type=next.type='button';prev.disabled=page===0;next.disabled=(page+1)*size>=rows.length;prev.onclick=()=>{page--;draw();};next.onclick=()=>{page++;draw();};bar.append(prev,next);host.append(bar);}}
 draw();
}
function filtered(rows,term){term=term.trim().toLocaleLowerCase('pt-BR');return !term?rows:rows.filter(row=>Object.values(row).some(value=>String(value??'').toLocaleLowerCase('pt-BR').includes(term)));}
