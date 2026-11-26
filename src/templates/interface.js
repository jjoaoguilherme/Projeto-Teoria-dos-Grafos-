'use strict';
const $=id=>document.getElementById(id);
let catalog={},token='',job=null,poll=null,animation=null,mapResult=null,step=0,filesPage=0;
const titles={inicio:'Visão geral',labirintos:'Labirintos',dataset:'Rede do Reddit',figuras:'Visualizações',arquivos:'Entregas e documentos',geracao:'Gerar e verificar'};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n}
function error(e){$('erro').textContent=e.message||String(e);$('erro').hidden=false}
function tab(name){if(!titles[name])name='inicio';document.querySelectorAll('.page').forEach(p=>p.classList.toggle('active',p.id===name));document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));$('titulo').textContent=titles[name];history.replaceState(null,'','#'+name)}
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.tab)));
window.addEventListener('hashchange',()=>tab(location.hash.slice(1)));
async function api(url,body){const response=await fetch(url,body?{method:'POST',headers:{'Content-Type':'application/json','X-Project-Token':token},body:JSON.stringify(body)}:{});const d=await response.json();if(!response.ok)throw Error(d.erro||'Falha na requisição.');return d}
function stat(parent,value,label){const n=el('div',undefined,'stat');n.append(el('strong',value??'—'),el('span',label));parent.append(n)}
function option(select,value,label){const o=el('option',label);o.value=value;select.append(o)}
function pretty(v){return typeof v==='object'&&v!==null?JSON.stringify(v):String(v??'—')}
function table(parent,rows,columns,onClick){const wrap=el('div',undefined,'table-wrap'),t=el('table'),head=el('thead'),tr=el('tr'),body=el('tbody');let data=[...rows],sortDirection=1;for(const key of columns){const th=el('th',key);th.tabIndex=0;const sort=()=>{data.sort((a,b)=>typeof a[key]==='number'&&typeof b[key]==='number'?sortDirection*(a[key]-b[key]):sortDirection*pretty(a[key]).localeCompare(pretty(b[key]),'pt-BR',{numeric:true}));sortDirection*=-1;draw()};th.onclick=sort;th.onkeydown=e=>{if(e.key==='Enter')sort()};tr.append(th)}head.append(tr);t.append(head,body);wrap.append(t);parent.append(wrap);function draw(){body.replaceChildren();for(const row of data){const line=el('tr');for(const key of columns){const td=el('td',pretty(row[key]));line.append(td)}if(onClick){const td=el('td'),button=el('button','Detalhes','secondary');button.onclick=()=>onClick(row);td.append(button);line.append(td)}body.append(line)}if(!data.length){const td=el('td','Nenhum registro encontrado.');td.colSpan=columns.length;body.append(td)}}draw()}
function jsonExplorer(parent,obj){const path=[];function draw(){parent.replaceChildren();let value=obj;for(const k of path)value=value[k];const top=el('div',undefined,'controls'),back=el('button','Voltar um nível','secondary');back.disabled=!path.length;back.onclick=()=>{path.pop();draw()};top.append(back,el('span','Raiz'+path.map(k=>' / '+k).join('')));parent.append(top);if(Array.isArray(value)){let page=0;const area=el('div');parent.append(area);function render(){area.replaceChildren();const slice=value.slice(page*50,page*50+50);if(slice.every(r=>r&&typeof r==='object'&&!Array.isArray(r))){const keys=[...new Set(slice.flatMap(Object.keys))];table(area,slice,keys,row=>{path.push(value.indexOf(row));draw()})}else{const rows=slice.map((v,i)=>({indice:page*50+i,valor:v}));table(area,rows,['indice','valor'],r=>{path.push(r.indice);draw()})}pager(area,page,value.length,p=>{page=p;render()})}render()}else if(value&&typeof value==='object'){const rows=Object.entries(value).map(([campo,v])=>({campo,valor:typeof v==='object'&&v!==null?(Array.isArray(v)?v.length+' registros':Object.keys(v).length+' campos'):v}));table(parent,rows,['campo','valor'],r=>{path.push(r.campo);draw()})}else parent.append(el('pre',pretty(value)))}draw()}
function pager(parent,page,total,change){const d=el('div',undefined,'pagination'),prev=el('button','Anterior','secondary'),next=el('button','Próxima','secondary');prev.disabled=page===0;next.disabled=(page+1)*50>=total;prev.onclick=()=>change(page-1);next.onclick=()=>change(page+1);d.append(prev,el('span',`${total} registros · página ${page+1} de ${Math.max(1,Math.ceil(total/50))}`),next);parent.append(d)}
async function refresh(){catalog=await api('/api/catalogo');token=catalog.token;const old=$('mapa').value;$('mapa').replaceChildren();catalog.mapas.forEach(m=>option($('mapa'),m.caminho,m.nome));if(catalog.mapas.some(m=>m.caminho===old))$('mapa').value=old;for(const id of ['alg-mapa','alg-dataset'])if(!$(id).options.length)catalog.algoritmos.forEach(a=>option($(id),a,a));$('stats').replaceChildren();stat($('stats'),catalog.mapas.length,'mapas disponíveis');stat($('stats'),4,'algoritmos compartilhados');stat($('stats'),catalog.arquivos.filter(f=>f.tipo==='png'&&!f.caminho.includes('/interface/')).length,'figuras exportadas');stat($('stats'),catalog.arquivos.filter(f=>!f.cache).length,'arquivos de entrega');$('checklist').replaceChildren();for(const [label,path]of [['Labirinto interativo obrigatório','out/parte1/labirinto_interativo.html'],['Métricas e camadas','out/parte1/camadas.json'],['Experimentos consolidados','out/parte2/parte2_report.json'],['Escalabilidade','out/parte2/escalabilidade_report.json'],['Manual técnico da Parte 1','docs/manual_tecnico_parte1.pdf'],['Declaração de IA','docs/DECLARACAO_IA.pdf']]){const row=el('div',undefined,'check-row'),f=catalog.arquivos.find(f=>f.caminho===path);row.append(el('span',label));if(f){const a=el('a','Disponível','ok');a.href=f.url;a.target='_blank';row.append(a)}else row.append(el('span','Arquivo não encontrado','missing'));$('checklist').append(row)}renderFiles();gallery();renderActions();await benchmarks();const active=catalog.trabalhos.find(t=>t.status==='executando');if(active&&!job){job=active.id;watch()}}
function renderFiles(){const search=$('busca-arquivos').value.toLowerCase(),group=$('grupo-arquivos').value;const files=catalog.arquivos.filter(f=>(!f.cache||$('mostrar-cache').checked)&&f.caminho.includes(group)&&f.caminho.toLowerCase().includes(search));filesPage=Math.min(filesPage,Math.max(0,Math.ceil(files.length/50)-1));const parent=$('lista-arquivos');parent.replaceChildren();for(const f of files.slice(filesPage*50,filesPage*50+50)){const row=el('div',undefined,'check-row'),info=el('div');info.append(el('strong',f.nome),el('div',f.caminho,'muted'));const links=el('div',undefined,'controls'),a=el('a','Abrir / baixar');a.href=f.url;a.target='_blank';a.rel='noopener';links.append(a);if(['csv','tsv','json'].includes(f.tipo)){const b=el('button','Consultar','secondary');b.onclick=()=>inspect(f).catch(error);links.append(b)}row.append(info,links);parent.append(row)}pager(parent,filesPage,files.length,p=>{filesPage=p;renderFiles()})}
async function inspect(f){tab('arquivos');$('inspector').hidden=false;$('nome-arquivo').textContent=f.nome;$('baixar-arquivo').href=f.url;const parent=$('conteudo-arquivo');parent.replaceChildren(el('p','Carregando…'));if(f.tipo==='json'){jsonExplorer(parent,await api('/api/tabela?arquivo='+encodeURIComponent(f.caminho)))}else{let page=0;const search=el('input');search.placeholder='Filtrar registros';search.type='search';const button=el('button','Pesquisar','secondary'),controls=el('div',undefined,'controls'),area=el('div');controls.append(search,button);parent.replaceChildren(controls,area);async function load(){area.textContent='Carregando…';const d=await api('/api/tabela?arquivo='+encodeURIComponent(f.caminho)+'&offset='+page*50+'&busca='+encodeURIComponent(search.value));area.replaceChildren();table(area,d.linhas,d.colunas||[]);pager(area,page,d.total,p=>{page=p;load().catch(error)})}button.onclick=()=>{page=0;load().catch(error)};await load()}$('inspector').scrollIntoView({behavior:'smooth',block:'start'})}
function gallery(){const parent=$('galeria');parent.replaceChildren();for(const f of catalog.arquivos.filter(f=>f.tipo==='png'&&f.caminho.includes($('grupo-figuras').value))){const card=el('article',undefined,'card'),a=el('a');a.href=f.url;a.target='_blank';const img=el('img');img.src=f.url;img.alt=f.nome;img.loading='lazy';a.append(img);card.append(a,el('h3',f.nome),el('p',f.caminho,'muted'));parent.append(card)}}
async function benchmarks(){const parent=$('benchmarks');parent.replaceChildren();const f=catalog.arquivos.find(f=>f.caminho==='out/parte2/parte2_report.json');if(!f){parent.textContent='Relatório consolidado ainda não disponível.';return}const d=await api('/api/tabela?arquivo='+encodeURIComponent(f.caminho));const rows=(d.experimentos||[]).map((x,i)=>({registro:i+1,algoritmo:x.algoritmo,origem:x.origem,vertices:x.vertices,arcos:x.arestas,repeticoes:x.repeticoes,media_segundos:x.tempo_medio_segundos}));table(parent,rows,['registro','algoritmo','origem','vertices','arcos','repeticoes','media_segundos'],row=>{const box=el('div');jsonExplorer(box,d.experimentos[row.registro-1]);const old=parent.querySelector('.benchmark-detail');if(old)old.remove();box.className='benchmark-detail';parent.append(box)})}
function renderActions(){const parent=$('acoes');parent.replaceChildren();for(const [key,name]of Object.entries(catalog.acoes)){const b=el('button',name);b.disabled=!$('confirmar-geracao').checked;b.onclick=()=>run({acao:key}).catch(error);parent.append(b)}}
async function run(data){$('erro').hidden=true;const d=await api('/api/executar',data);job=d.id;$('trabalho').hidden=false;$('ver-saidas').hidden=true;$('log').textContent='Iniciando processo Python…';$('trabalho').scrollIntoView({behavior:'smooth',block:'nearest'});await watch()}
async function watch(){clearTimeout(poll);if(!job)return;try{const d=await api('/api/trabalho/'+job);$('trabalho').hidden=false;$('titulo-trabalho').textContent=catalog.acoes[d.acao]|| (d.acao==='mapa'?'Execução do labirinto':'Consulta no dataset');$('situacao-trabalho').textContent='Estado: '+d.status;$('log').textContent=d.log||'Processando…';$('cancelar').hidden=d.status!=='executando';if(d.status==='executando'){poll=setTimeout(watch,900);return}$('ver-saidas').hidden=false;$('ver-saidas').onclick=()=>{tab('arquivos');$('grupo-arquivos').value='out/interface/';$('busca-arquivos').value=d.pasta;renderFiles()};if(d.resultado?.tipo==='mapa')showMap(d.resultado);if(d.resultado?.tipo==='dataset')showDataset(d.resultado);if(d.status==='erro')error(Error('A execução falhou. O log abaixo contém o erro do Python.'));job=null;await refresh()}catch(e){error(e);poll=setTimeout(watch,3000)}}
function stop(){clearInterval(animation);animation=null;$('reproduzir').textContent='Reproduzir'}
function showMap(d){stop();mapResult=d;step=0;const r=d.relatorio;$('status-mapa').textContent=r.status;$('resumo-mapa').replaceChildren();stat($('resumo-mapa'),r.passos,'passos');stat($('resumo-mapa'),r.custo,'custo');stat($('resumo-mapa'),r.estados_alcancaveis,'estados');$('camada').replaceChildren();option($('camada'),'*','Todas');[...new Set(d.estados.map(e=>e.chaves))].sort().forEach(c=>option($('camada'),c,c==='-'?'Sem chaves':c));renderMapAnalysis(d);$('passo').max=Math.max(0,r.percurso.length-1);for(const id of ['reiniciar','anterior','proximo','reproduzir','passo'])$(id).disabled=!r.percurso.length;renderMaze();tab('labirintos')}
function numberText(value, maximumFractionDigits=6){
    return typeof value==='number'&&Number.isFinite(value)
        ? value.toLocaleString('pt-BR',{maximumFractionDigits}) : '—';
}
function stateText(value){
    if(value==='ALVO')return 'Alvo virtual (fim do percurso)';
    if(typeof value!=='string')return '—';
    const parts=value.split('|');
    if(parts.length!==3)return value;
    return `Posição ${parts[0]} · chaves: ${parts[1]==='-'?'nenhuma':parts[1]} · bônus: ${parts[2]==='{}'?'nenhum':parts[2].replace(/[{}]/g,'')}`;
}
function analysisSection(parent,title,description){
    const section=el('section',undefined,'analysis-section');
    section.append(el('h3',title));
    if(description)section.append(el('p',description,'muted'));
    parent.append(section);
    return section;
}
function analysisTable(parent,rows,columns,label){
    // Paginação e filtro mantêm listas grandes, como os estados do m08, navegáveis.
    let page=0;
    const labelNode=el('label',`Pesquisar em ${label}`),search=el('input');
    search.type='search';search.placeholder='Digite uma posição, chave ou tipo';
    labelNode.append(search);
    const area=el('div');
    parent.append(labelNode,area);
    function draw(){
        const query=search.value.toLocaleLowerCase('pt-BR');
        const filtered=rows.filter(row=>Object.values(row).some(v=>String(v??'').toLocaleLowerCase('pt-BR').includes(query)));
        area.replaceChildren();
        table(area,filtered.slice(page*50,page*50+50),columns);
        if(filtered.length>50)pager(area,page,filtered.length,p=>{page=p;draw()});
        else area.append(el('p',`${filtered.length} registro(s)`,'muted'));
    }
    search.addEventListener('input',()=>{page=0;draw()});
    draw();
}
function renderMapAnalysis(d){
    const r=d.relatorio,m=r.metricas_globais||{},parent=$('detalhes-mapa');
    parent.replaceChildren();$('analise-mapa').hidden=false;
    $('identidade-mapa').textContent=`${r.mapa} · ${r.algoritmo}${r.fonte_consumivel?' · fonte consumível':''}`;
    const messages={
        OK: r.algoritmo==='DFS'?'Busca em profundidade concluída. O percurso encontrado pela DFS não é necessariamente o menor.':'Percurso encontrado. Os valores abaixo correspondem a esta execução.',
        RECUSA:r.motivo_recusa||'Este algoritmo recusou os pesos do mapa.',
        SEM_SOLUCAO:'Não existe caminho do início até a saída. As métricas descrevem os estados alcançados pela exploração.',
        CICLO_NEGATIVO:r.ciclo_afeta_alvo?'Ciclo negativo alcançável e com acesso à saída: o custo até a saída não tem limite inferior.':'Foi detectado um ciclo negativo alcançável. Consulte abaixo se ele afeta o alvo.'
    };
    $('mensagem-mapa').textContent=messages[r.status]||r.status;
    $('mensagem-mapa').className='result-message '+(r.status==='OK'?'result-ok':'result-warning');

    const global=analysisSection(parent,'Tamanho e ocupação do grafo','As métricas excluem o alvo virtual e seus arcos. G_pos representa casas; G_est representa posição, chaves e consumíveis.');
    const cards=el('div',undefined,'stats');
    stat(cards,numberText(m.G_est?.ordem),'estados alcançáveis');
    stat(cards,numberText(m.G_est?.tamanho),'arcos entre estados');
    stat(cards,numberText(m.teto_teorico),'teto teórico de estados');
    stat(cards,typeof m.taxa_ocupacao==='number'?numberText(100*m.taxa_ocupacao,2)+'%':'—','ocupação do teto');
    global.append(cards);
    table(global,[['Grafo de posições',m.G_pos],['Grafo de estados',m.G_est]].map(([name,g])=>({
        'Grafo':name,'Vértices (ordem)':g?.ordem??'—','Arcos (tamanho)':g?.tamanho??'—','Densidade dirigida':numberText(g?.densidade)
    })),['Grafo','Vértices (ordem)','Arcos (tamanho)','Densidade dirigida']);
    global.append(el('p',`Casas livres: ${numberText(m.casas_livres)} · Chaves: ${(m.chaves||[]).join(', ')||'nenhuma'} · Bônus: ${numberText(m.numero_bonus)} · Fontes consumíveis: ${numberText(m.numero_fontes_consumiveis)}`,'muted'));
    const path=analysisSection(parent,'Métricas do percurso','Passos contam movimentos na grade, sem a ligação virtual ao alvo.');
    const pathCards=el('div',undefined,'stats');
    stat(pathCards,numberText(r.passos),'passos');
    stat(pathCards,r.custo_sem_limite?'Sem limite inferior':numberText(r.custo),'custo do percurso');
    stat(pathCards,numberText(r.metricas_percurso?.custo_medio_por_movimento),'custo médio por movimento');
    stat(pathCards,numberText(r.metricas_percurso?.casas_distintas),'casas distintas visitadas');
    path.append(pathCards);
    if(!r.percurso.length)path.append(el('p','Não há percurso finito disponível nesta execução. “—” indica uma medida indisponível, não zero.','muted'));

    const layers=d.camadas||{},trans=layers.arcos_entre_camadas||{};
    const layerSection=analysisSection(parent,'Camadas por conjunto de chaves','Cada linha descreve o subgrafo induzido pelos estados que possuem o mesmo conjunto de chaves.');
    table(layerSection,Object.entries(layers.camadas||{}).map(([key,g])=>({
        'Chaves':key==='-'?'Sem chaves':key,'Estados':g.ordem,'Arcos internos':g.tamanho,'Densidade':numberText(g.densidade)
    })),['Chaves','Estados','Arcos internos','Densidade']);
    layerSection.append(el('h4',`Mudanças de camada · ${numberText(trans.quantidade)} arcos`));
    if(trans.transicoes?.length){
        table(layerSection,trans.transicoes.map(t=>({'Origem':t.origem==='-'?'Sem chaves':t.origem,'Destino':t.destino==='-'?'Sem chaves':t.destino,'Arcos':t.quantidade})),['Origem','Destino','Arcos']);
        table(layerSection,(trans.por_casa||[]).map(c=>({'Casa':`(${c.posicao.join(', ')})`,'Chave coletada':c.chave,'Arcos de transição':c.quantidade})),['Casa','Chave coletada','Arcos de transição']);
    }else layerSection.append(el('p','Não há arcos entre conjuntos diferentes de chaves neste mapa.','muted'));

    const degrees=analysisSection(parent,'Graus e rankings','Graus de entrada e saída dos estados reais; o alvo virtual não participa. A ordenação das tabelas aplica-se à página visível.');
    table(degrees,[['Maior grau de entrada',m.rankings?.maior_grau_entrada],['Maior grau de saída',m.rankings?.maior_grau_saida]].map(([name,v])=>({'Ranking':name,'Estado':stateText(v?.estado),'Grau':v?.grau??'—'})),['Ranking','Estado','Grau']);
    const degreeDetails=el('details');degreeDetails.append(el('summary','Consultar graus de todos os estados'));degrees.append(degreeDetails);
    if(Array.isArray(d.graus))analysisTable(degreeDetails,d.graus.map(g=>({'Estado':stateText(g.estado),'Entrada':g.grau_entrada,'Saída':g.grau_saida})),['Estado','Entrada','Saída'],'graus');
    else degreeDetails.append(el('p','Execute novamente para carregar os graus individuais.','muted'));

    const mult=m.multiplicidade||{};
    const structure=analysisSection(parent,'Multiplicidade, becos e armadilhas','Multiplicidade é a quantidade de estados na mesma casa. Becos não têm saída e não estão em G; armadilhas são estados sem caminho até o alvo.');
    const structureCards=el('div',undefined,'stats');
    stat(structureCards,numberText(mult.maxima),'multiplicidade máxima');
    stat(structureCards,numberText(mult.quantidade_casas_maximas),'casas que atingem o máximo');
    stat(structureCards,numberText(m.becos?.quantidade),'estados em becos');
    stat(structureCards,numberText(d.estados.filter(e=>e.armadilha).length),'estados-armadilha');
    structure.append(structureCards);
    const sections=[
        ['Multiplicidade por casa',(mult.por_casa||[]).map(c=>({'Casa':`(${c.posicao.join(', ')})`,'Estados':c.multiplicidade})),['Casa','Estados']],
        ['Estados em becos',(m.becos?.estados||[]).map(v=>({'Estado':stateText(v)})),['Estado']],
        ['Estados-armadilha',d.estados.filter(e=>e.armadilha).map(e=>({'Estado':stateText(e.rotulo)})),['Estado']]
    ];
    for(const [title,rows,columns]of sections){const details=el('details');details.append(el('summary',title));structure.append(details);analysisTable(details,rows,columns,title.toLowerCase())}

    const cycle=analysisSection(parent,'Ciclos negativos');
    if(r.ciclo_negativo?.length){
        const cc=el('div',undefined,'stats mini');
        stat(cc,numberText(r.custo_ciclo),'custo total do ciclo');
        stat(cc,(r.arestas_ciclo||[]).length,'arcos no ciclo');
        stat(cc,r.ciclo_afeta_alvo?'Sim':'Não','ciclo afeta o alvo');cycle.append(cc);
        cycle.append(el('p','Sequência de estados que fecha o ciclo:','muted'));
        const sequence=el('ol',undefined,'cycle-sequence');
        r.ciclo_negativo.forEach(v=>sequence.append(el('li',stateText(v))));cycle.append(sequence);
        table(cycle,(r.arestas_ciclo||[]).map(([u,v,w])=>({'De':stateText(u),'Para':stateText(v),'Peso':w})),['De','Para','Peso']);
    }else cycle.append(el('p',r.algoritmo==='BELLMAN_FORD'?'Bellman-Ford não detectou ciclo negativo alcançável nesta execução.':'A detecção de ciclos negativos requer Bellman-Ford. Execute esse algoritmo para verificar.','muted'));

    const dfs=analysisSection(parent,'Classificação DFS');
    if(r.algoritmo!=='DFS'){
        dfs.append(el('p','Esta execução utilizou '+r.algoritmo+'. Selecione DFS e execute o mapa para visualizar a classificação dos arcos.','muted'));
    }else{
        dfs.append(el('p',r.tem_ciclo?'A DFS encontrou ciclo no grafo alcançado.':'A DFS não encontrou ciclo no grafo alcançado.','result-message'));
        const names={arvore:'Árvore',retorno:'Retorno',avanco:'Avanço',cruzamento:'Cruzamento'};
        const meanings={arvore:'Descobre um novo estado.',retorno:'Retorna a um ancestral ainda em exploração.',avanco:'Liga a um descendente já descoberto.',cruzamento:'Liga a outro ramo da busca.'};
        const counts={arvore:0,retorno:0,avanco:0,cruzamento:0};
        (r.classificacao_arestas||[]).forEach(a=>{counts[a[2]]=(counts[a[2]]||0)+1});
        table(dfs,Object.keys(names).map(k=>({'Tipo de arco':names[k],'Quantidade':counts[k],'Significado':meanings[k]})),['Tipo de arco','Quantidade','Significado']);
        dfs.append(el('p','A classificação segue a busca a partir do início e inclui a ligação virtual ao alvo quando alcançada.','muted'));
        const details=el('details');details.append(el('summary','Consultar arcos classificados'));dfs.append(details);
        analysisTable(details,(r.classificacao_arestas||[]).map(([u,v,k])=>({'Origem':stateText(u),'Destino':stateText(v),'Tipo':names[k]||k})),['Origem','Destino','Tipo'],'arcos DFS');
    }
}
function renderMaze(){if(!mapResult)return;const {matriz,estados,relatorio:r}=mapResult,path=r.percurso,current=path[step],layer=$('camada').value,trap=$('armadilhas').checked;const grid=$('maze');grid.replaceChildren();const cols=matriz[0].length;grid.style.gridTemplateColumns=`repeat(${cols},var(--size))`;grid.style.setProperty('--size',Math.max(12,Math.min(30,Math.floor(750/cols)))+'px');const groups=new Map;for(const e of estados){if(layer!=='*'&&e.chaves!==layer)continue;const key=e.posicao.join(',');if(!groups.has(key))groups.set(key,[]);groups.get(key).push(e)}const trail=new Set(path.slice(0,step+1).map(s=>s.posicao.join(',')));const types={'#':'wall','~':'water',',':'mud','+':'bonus','*':'bonus','G':'goal','S':'start'};matriz.forEach((row,i)=>Array.from(row).forEach((c,j)=>{const key=i+','+j,list=groups.get(key)||[],n=el('div',c==='#'||c==='.'?'':c,'cell '+(types[c]||(/[a-d]/.test(c)?'key':/[A-D]/.test(c)?'door':'><^v'.includes(c)?'belt':'')));n.title=`(${key}) · ${list.length} estados · ${list.filter(e=>e.armadilha).length} armadilhas`;if(layer!=='*'&&!list.length&&c!=='#')n.style.opacity='.25';if(trap&&list.some(e=>e.armadilha))n.classList.add('trap');if(trail.has(key))n.classList.add('trail');if(current?.posicao.join(',')===key){n.classList.add('player');n.textContent='●';n.style.opacity=1}grid.append(n)}));$('passo').value=step;$('estado-atual').textContent=current?`Passo ${step} de ${path.length-1} · Posição (${current.posicao}) · Chaves: ${current.chaves.join(', ')||'nenhuma'} · Bônus/fontes consumidos: ${current.consumidos_posicoes.length} · Custo acumulado: ${current.custo_acumulado}`:`${r.status}: ${r.motivo_recusa||'Não há percurso finito para animar. Consulte os detalhes.'}`}
function showDataset(d){$('resumo-dataset').replaceChildren();stat($('resumo-dataset'),d.vertices,'vértices');stat($('resumo-dataset'),d.arcos,'arcos');stat($('resumo-dataset'),d.segundos.toFixed(4)+' s','tempo da consulta');$('escopo-dataset').textContent=d.escopo+' · Pesos: '+d.pesos;$('caminho-dataset').replaceChildren(...d.caminho.map(v=>el('span',v)));$('detalhes-dataset').textContent=JSON.stringify(d,null,2);tab('dataset')}
$('form-mapa').onsubmit=e=>{e.preventDefault();run({acao:'mapa',mapa:$('mapa').value,texto:$('texto-mapa').value,algoritmo:$('alg-mapa').value,consumivel:$('consumivel').checked}).catch(error)};
$('importar-mapa').onchange=async e=>{try{if(e.target.files[0])$('texto-mapa').value=await e.target.files[0].text()}catch(e){error(e)}};
$('limpar-mapa').onclick=()=>{$('texto-mapa').value='';$('importar-mapa').value=''};
$('form-dataset').onsubmit=e=>{e.preventDefault();run({acao:'dataset',origem:$('origem').value,destino:$('destino').value,algoritmo:$('alg-dataset').value,limite:Number($('limite').value)}).catch(error)};
$('cancelar').onclick=()=>api('/api/cancelar',{id:job}).then(watch).catch(error);
$('atualizar').onclick=()=>refresh().catch(error);
for(const id of ['busca-arquivos','grupo-arquivos','mostrar-cache'])$(id).addEventListener('input',()=>{filesPage=0;renderFiles()});
$('grupo-figuras').onchange=gallery;$('confirmar-geracao').onchange=renderActions;
for(const id of ['camada','armadilhas'])$(id).onchange=renderMaze;
$('reiniciar').onclick=()=>{stop();step=0;renderMaze()};$('anterior').onclick=()=>{stop();step=Math.max(0,step-1);renderMaze()};$('proximo').onclick=()=>{stop();step=Math.min(mapResult.relatorio.percurso.length-1,step+1);renderMaze()};$('passo').oninput=()=>{stop();step=Number($('passo').value);renderMaze()};
$('reproduzir').onclick=()=>{if(animation){stop();return}if(!mapResult?.relatorio.percurso.length)return;if(step>=mapResult.relatorio.percurso.length-1)step=0;$('reproduzir').textContent='Pausar';animation=setInterval(()=>{step=Math.min(step+1,mapResult.relatorio.percurso.length-1);renderMaze();if(step>=mapResult.relatorio.percurso.length-1)stop()},Number($('velocidade').value))};$('velocidade').onchange=stop;
for(const id of ['reiniciar','anterior','proximo','reproduzir','passo'])$(id).disabled=true;
tab(location.hash.slice(1));refresh().catch(error);
