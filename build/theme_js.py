JS = r"""
/* ============ 工具 ============ */
function $(s,r){return (r||document).querySelector(s)}
function $all(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))}
var C = {
  ink:function(){return getComputedStyle(document.documentElement).getPropertyValue('--ink').trim()||'#141A1B'},
  ink3:function(){return getComputedStyle(document.documentElement).getPropertyValue('--ink-3').trim()||'#7E8A8C'},
  rule:function(){return getComputedStyle(document.documentElement).getPropertyValue('--rule').trim()||'#D9DCD3'},
  paper:function(){return getComputedStyle(document.documentElement).getPropertyValue('--paper').trim()||'#F2F3EF'},
  surface:function(){return getComputedStyle(document.documentElement).getPropertyValue('--surface').trim()||'#fff'},
  accent:function(){return getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()||'#9C3B2E'}
};
var REDUCE = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function toast(msg){
  var t = $('#toast');
  if(!t){t=document.createElement('div');t.id='toast';t.className='toast';document.body.appendChild(t);}
  t.textContent = msg; t.classList.add('on');
  clearTimeout(t._h); t._h = setTimeout(function(){t.classList.remove('on')},1600);
}
function scrollToId(id){
  var el = document.getElementById(id);
  if(!el) return;
  var top = el.getBoundingClientRect().top + window.pageYOffset - 12;
  window.scrollTo({top:top, behavior: REDUCE ? 'auto' : 'smooth'});
  if(history.replaceState) history.replaceState(null,'','#'+id);
}

/* ============ 主题 / 字号 ============ */
(function(){
  var root = document.documentElement;
  var t='light', f='2';
  try{ t = localStorage.getItem('aitut-theme') || 'light'; f = localStorage.getItem('aitut-font') || '2'; }catch(e){}
  root.setAttribute('data-theme', t);
  var SIZES={'1':'16.5px','2':'17.5px','3':'19.5px'};
  root.style.setProperty('--doc-size', SIZES[f]||SIZES['2']);

  document.addEventListener('click', function(ev){
    var el = ev.target.closest('[data-act]');
    if(!el) return;
    var act = el.getAttribute('data-act');
    if(act==='theme'){
      var cur = root.getAttribute('data-theme');
      var next = cur==='dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try{localStorage.setItem('aitut-theme', next);}catch(e){}
      el.textContent = next==='dark' ? '浅色' : '深色';
      redrawAll();
    }
    if(act==='font'){
      var order=['1','2','3'], i=order.indexOf(root.getAttribute('data-fs')||f);
      var nf=order[(i+1)%3];
      root.setAttribute('data-fs',nf);
      root.style.setProperty('--doc-size', SIZES[nf]);
      try{localStorage.setItem('aitut-font', nf);}catch(e){}
      toast('字号 '+nf+'/3');
    }
    if(act==='top'){ window.scrollTo({top:0,behavior:REDUCE?'auto':'smooth'}); }
    if(act==='rail'){ $('.rail').classList.toggle('open'); }
    if(act==='railstop'){ $('.rail').classList.remove('open'); }
    if(act==='copy'){
      var box = el.closest('.code'), code = box && box.querySelector('pre code');
      if(!code) return;
      var text = code.innerText;
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(text).then(function(){toast('已复制');},function(){fallbackCopy(text);});
      } else { fallbackCopy(text); }
      el.textContent='已复制';
      setTimeout(function(){el.textContent='复制';},1400);
    }
  });
  function fallbackCopy(text){
    var ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed'; ta.style.opacity='0';
    document.body.appendChild(ta); ta.select();
    try{document.execCommand('copy'); toast('已复制');}catch(e){toast('复制失败，请手动选择');}
    document.body.removeChild(ta);
  }
  root.setAttribute('data-fs', f);
})();

/* ============ 目录 / 滚动定位 ============ */
(function(){
  var links = $all('.ch-link'), subs = $all('.sub-link');
  var chapters = $all('.chapter');
  function current(){
    var y = window.pageYOffset + 140, idx = 0;
    for(var i=0;i<chapters.length;i++){
      if(chapters[i].offsetTop <= y) idx = i;
    }
    return chapters[idx] ? chapters[idx].id : null;
  }
  var raf = null;
  function update(){
    var id = current();
    links.forEach(function(a){ a.classList.toggle('active', a.getAttribute('data-target')===id); });
    var bar = $('#progressbar'), pct = $('#pct');
    var h = document.body.scrollHeight - window.innerHeight;
    var p = h>0 ? Math.min(100, Math.max(0, window.pageYOffset/h*100)) : 0;
    if(bar) bar.style.width = p.toFixed(1)+'%';
    if(pct) pct.textContent = Math.round(p)+'%';
    raf = null;
  }
  window.addEventListener('scroll', function(){ if(!raf) raf = requestAnimationFrame(update); }, {passive:true});
  window.addEventListener('resize', update);
  links.forEach(function(a){ a.addEventListener('click', function(){ scrollToId(a.getAttribute('data-target')); $('.rail').classList.remove('open'); }); });
  subs.forEach(function(a){ a.addEventListener('click', function(){ scrollToId(a.getAttribute('data-target')); $('.rail').classList.remove('open'); }); });
  update();
})();

/* ============ 全文检索 ============ */
(function(){
  var input = $('#q'), panel = $('#searchPanel');
  if(!input || !panel) return;
  var IDX = window.__SEARCH__ || [];
  var timer = null;
  function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function run(){
    var q = input.value.trim().toLowerCase();
    if(q.length < 1){ panel.classList.remove('on'); panel.innerHTML=''; return; }
    var hits = [];
    for(var i=0;i<IDX.length && hits.length<14;i++){
      var item = IDX[i], text = item.t || '';
      var pos = text.toLowerCase().indexOf(q), hp = item.h.toLowerCase().indexOf(q);
      if(pos<0 && hp<0) continue;
      var snip = '';
      if(pos>=0){ var s=Math.max(0,pos-24); snip = (s>0?'…':'') + text.slice(s,pos+q.length+46) + '…'; }
      hits.push({h:item.h, s:item.s, id:item.id, snip:snip, title:item.k==='c'});
    }
    if(!hits.length){ panel.innerHTML = '<div class="sr-empty">没有匹配「'+esc(input.value)+'」。换个更短的关键词试试。</div>'; panel.classList.add('on'); return; }
    panel.innerHTML = hits.map(function(x){
      var mark = x.snip ? x.snip.replace(new RegExp('('+input.value.replace(/[.*+?^$\{\}()|[\]\\\\]/g,'\\$&')+')','ig'),'<b>$1</b>') : '';
      return '<div class="sr-item" data-go="'+x.id+'"><span class="sr-t">'+esc(x.h)+'</span><span class="sr-x">'+mark+'</span></div>';
    }).join('');
    panel.classList.add('on');
  }
  input.addEventListener('input', function(){ clearTimeout(timer); timer=setTimeout(run,120); });
  input.addEventListener('keydown', function(e){
    if(e.key==='Enter'){ var first = panel.querySelector('.sr-item'); if(first){ scrollToId(first.getAttribute('data-go')); panel.classList.remove('on'); } }
    if(e.key==='Escape'){ panel.classList.remove('on'); input.blur(); }
  });
  panel.addEventListener('click', function(e){
    var it = e.target.closest('.sr-item'); if(!it) return;
    scrollToId(it.getAttribute('data-go')); panel.classList.remove('on');
  });
  document.addEventListener('click', function(e){ if(!e.target.closest('.search-wrap')) panel.classList.remove('on'); });
})();
/* ============ 公式渲染 ============ */
(function(){
  function render(){
    var blocks = $all('.math-block'), inlines = $all('.m-inline');
    if(!window.katex){
      blocks.forEach(function(el){ el.textContent = '$$' + el.getAttribute('data-tex') + '$$'; });
      return;
    }
    blocks.forEach(function(el){
      try{ katex.render(el.getAttribute('data-tex'), el, {displayMode:true, throwOnError:false, strict:false}); }catch(e){}
    });
    inlines.forEach(function(el){
      try{ katex.render(el.getAttribute('data-tex'), el, {displayMode:false, throwOnError:false, strict:false}); }catch(e){}
    });
  }
  if(document.readyState === 'complete'){ render(); }
  else { window.addEventListener('load', render); }
})();
"""

WIDGETS_JS = r"""
/* ============ 实验台 ============ */
var W_REDRAW = [];
function redrawAll(){ W_REDRAW.forEach(function(f){ try{f();}catch(e){} }); }
(function(){
  function setupCanvas(cv, ratio){
    var cssW = cv.clientWidth || 420;
    var dpr = Math.min(2, window.devicePixelRatio||1);
    var cssH = Math.round(cssW * (ratio||0.62));
    cv.width = Math.round(cssW*dpr); cv.height = Math.round(cssH*dpr);
    cv.style.height = cssH+'px';
    var ctx = cv.getContext('2d');
    ctx.setTransform(dpr,0,0,dpr,0,0);
    return {ctx:ctx, w:cssW, h:cssH};
  }

  /* ---- 1. 梯度下降 ---- */
  function gradient(el){
    var cv = el.querySelector('canvas'), lr = el.querySelector('[data-lr]'), out = el.querySelector('[data-lrout]');
    var read = el.querySelector('[data-read]'), runBtn = el.querySelector('[data-run]'), stepBtn = el.querySelector('[data-step]'), resetBtn = el.querySelector('[data-reset]');
    var F = function(x,y){ return 0.62*x*x + 1.55*y*y; };
    var G = function(x,y){ return [1.24*x, 3.10*y]; };
    var start = [2.35,1.55], p, path, step, running=false, timer=null, view;
    function reset(){ p = start.slice(); path=[p.slice()]; step=0; draw(); }
    function doStep(){
      var g = G(p[0],p[1]), l = parseFloat(lr.value);
      p = [p[0]-l*g[0], p[1]-l*g[1]];
      path.push(p.slice()); step++;
      if(Math.abs(g[0])+Math.abs(g[1]) < 1e-4){ stop(); }
      if(step>900) stop();
      draw();
    }
    function stop(){ running=false; if(timer){clearInterval(timer);timer=null;} runBtn.textContent='运行'; }
    function draw(){
      var s = setupCanvas(cv, 0.66), ctx=s.ctx, w=s.w, h=s.h;
      var cx=w*0.46, cy=h*0.5, sx=Math.min(w,h*1.5)/6.4;
      view = {cx:cx, cy:cy, sx:sx};
      ctx.clearRect(0,0,w,h);
      var paper=C.paper(); ctx.fillStyle=paper; ctx.fillRect(0,0,w,h);
      // 等高线
      for(var k=1;k<=14;k++){
        var r = k*0.26*sx, rx=r*1.27, ry=r*0.8;
        ctx.beginPath(); ctx.ellipse(cx,cy,rx,ry,0,0,Math.PI*2);
        ctx.strokeStyle = k%2===0 ? 'rgba(120,132,120,.30)' : 'rgba(120,132,120,.16)';
        ctx.lineWidth = k%2===0?1:0.8; ctx.stroke();
      }
      // 网格
      ctx.strokeStyle='rgba(120,132,120,.14)'; ctx.lineWidth=.7;
      for(var gx=0; gx<=w; gx+=32){ ctx.beginPath(); ctx.moveTo(gx,0); ctx.lineTo(gx,h); ctx.stroke(); }
      for(var gy=0; gy<=h; gy+=32){ ctx.beginPath(); ctx.moveTo(0,gy); ctx.lineTo(w,gy); ctx.stroke(); }
      // 轨迹
      ctx.beginPath();
      path.forEach(function(pt,i){
        var X=cx+pt[0]*sx, Y=cy-pt[1]*sx*1.0;
        if(i===0) ctx.moveTo(X,Y); else ctx.lineTo(X,Y);
      });
      ctx.strokeStyle=C.accent(); ctx.lineWidth=1.6; ctx.stroke();
      // 起点
      if(path.length){
        var PX=cx+path[0][0]*sx, PY=cy-path[0][1]*sx;
        ctx.beginPath(); ctx.arc(PX,PY,2.6,0,Math.PI*2);
        ctx.strokeStyle=C.ink3(); ctx.lineWidth=1; ctx.stroke();
      }
      // 当前点 + 负梯度箭头
      var X=cx+p[0]*sx, Y=cy-p[1]*sx;
      var gv=G(p[0],p[1]), n=Math.hypot(gv[0],gv[1])||1;
      ctx.beginPath(); ctx.moveTo(X,Y); ctx.lineTo(X-gv[0]/n*36*sx/60, Y+gv[1]/n*36*sx/60);
      ctx.strokeStyle=C.accent(); ctx.lineWidth=2; ctx.stroke();
      ctx.beginPath(); ctx.arc(X,Y,3.6,0,Math.PI*2); ctx.fillStyle=C.accent(); ctx.fill();
      // 标注
      ctx.fillStyle=C.ink3(); ctx.font='11px ui-monospace, Consolas, monospace';
      ctx.fillText('f(x,y) = 0.62x² + 1.55y²', 12, 20);
      ctx.fillText('起点 ('+start[0].toFixed(2)+', '+start[1].toFixed(2)+')', 12, h-14);
      ctx.fillText('当前 ('+p[0].toFixed(3)+', '+p[1].toFixed(3)+')', 12, h-30);
      if(out) out.textContent = parseFloat(lr.value).toFixed(2);
      if(read) read.textContent = 'f = '+F(p[0],p[1]).toFixed(4)+'　迭代 '+step;
    }
    runBtn.addEventListener('click', function(){
      if(running){ stop(); return; }
      running=true; runBtn.textContent='暂停';
      timer=setInterval(doStep, 90);
    });
    stepBtn.addEventListener('click', doStep);
    resetBtn.addEventListener('click', function(){ stop(); reset(); });
    lr.addEventListener('input', draw);
    cv.addEventListener('click', function(e){
      var r=cv.getBoundingClientRect(), x=e.clientX-r.left, y=e.clientY-r.top;
      if(!view) return;
      var px=(x-view.cx)/view.sx, py=(view.cy-y)/view.sx;
      if(Math.abs(py)>1.9 || Math.abs(px)>2.9) return;
      stop(); p=[px,py]; path=[p.slice()]; step=0; draw();
    });
    W_REDRAW.push(draw);
    reset();
  }

  /* ---- 2. softmax 温度 ---- */
  function softmax(el){
    var logits = el.querySelectorAll('[data-logit]'), temp = el.querySelector('[data-temp]'), out=el.querySelector('[data-tout]');
    var bars = el.querySelector('[data-bars]'), read=el.querySelector('[data-read]');
    var names = ['A','B','C','D'];
    function draw(){
      var T = parseFloat(temp.value), z = [];
      logits.forEach(function(i){ z.push(parseFloat(i.value)); });
      out.textContent = T.toFixed(2);
      var m = Math.max.apply(null, z), ex=[], sum=0;
      z.forEach(function(v){ var e=Math.exp((v-m)/T); ex.push(e); sum+=e; });
      var p = ex.map(function(e){ return e/sum; });
      bars.innerHTML = p.map(function(pi,i){
        var pct = (pi*100);
        return '<div style="margin-bottom:.4rem">'+
          '<div style="display:flex;justify-content:space-between;font-family:var(--mono);font-size:.7rem;color:var(--ink-2)">'+
          '<span>'+names[i]+'　logit '+z[i].toFixed(1)+'</span><span>'+(pct<0.1?'&lt;0.1':pct.toFixed(1))+'%</span></div>'+
          '<div style="height:9px;background:var(--paper-2);position:relative"><i style="position:absolute;inset:0 auto 0 0;width:'+Math.max(0.4,pct.toFixed(1))+'%;background:var(--accent);display:block"></i></div>'+
          '</div>';
      }).join('');
      var H = 0; p.forEach(function(pi){ if(pi>1e-12) H -= pi*Math.log2(pi); });
      read.textContent = '熵 H(p) = '+H.toFixed(3)+' bit　最大概率 '+Math.max.apply(null,p).toFixed(3);
    }
    z_listen: for(var i=0;i<logits.length;i++) logits[i].addEventListener('input',draw);
    temp.addEventListener('input',draw);
    W_REDRAW.push(draw);
    draw();
  }

  /* ---- 3. 卷积窗口 ---- */
  function conv(el){
    var cv=el.querySelector('canvas'), ksel=el.querySelectorAll('[data-k]'), psel=el.querySelectorAll('[data-p]');
    var read=el.querySelector('[data-read]');
    var kernels = {
      edge: [[-1,-1,-1],[0,0,0],[1,1,1]],
      blur: [[1/9,1/9,1/9],[1/9,1/9,1/9],[1/9,1/9,1/9]],
      sharpen: [[0,-1,0],[-1,5,-1],[0,-1,0]]
    };
    var patterns = {
      hline: function(r,c){ return (r>=3&&r<=4)?1:0.08; },
      diag: function(r,c){ return Math.abs(r-c)<=1?1:0.08; },
      dot: function(r,c){ return (r-3)*(r-3)+(c-3)*(c-3)<=4?1:0.08; },
      noise: function(r,c){ return ((r*7+c*13)%5)/5*0.6+0.2; }
    };
    var N=7, k=1, K=2, pat='hline', ox=1, oy=1;
    function input(r,c){ return patterns[pat](r,c); }
    function draw(){
      var s=setupCanvas(cv,0.44), ctx=s.ctx, w=s.w, h=s.h;
      ctx.clearRect(0,0,w,h); ctx.fillStyle=C.paper(); ctx.fillRect(0,0,w,h);
      var pad=10, gap=Math.min(2, w/300);
      var cw=(w-pad*2)/ (N+N-K+1+N-K+1 + 1.6);
      var cell=cw;
      var x0=pad, y0=(h-(N*cell+(N-1)*gap))/2;
      function grid(x,y,size,fn,highlight){
        for(var r=0;r<size;r++) for(var c=0;c<size;c++){
          var v=fn(r,c), X=x+c*(cell+gap), Y=y+r*(cell+gap);
          ctx.fillStyle='rgba(20,30,32,'+(0.06+v*0.62)+')';
          ctx.fillRect(X,Y,cell,cell);
          if(cell>16){
            ctx.fillStyle=v>0.5?'#fff':C.ink3(); ctx.font='9px ui-monospace,Consolas,monospace';
            ctx.fillText((typeof v==='number' && isFinite(v))?v.toFixed(1):'', X+2, Y+cell-3);
          }
        }
      }
      // 输入
      grid(x0,y0,N,function(r,c){ return input(r,c); });
      ctx.strokeStyle=C.accent(); ctx.lineWidth=1.5;
      ctx.strokeRect(x0+oy*(cell+gap)-1, y0+ox*(cell+gap)-1, K*cell+(K-1)*gap+2, K*cell+(K-1)*gap+2);
      ctx.fillStyle=C.ink3(); ctx.font='10px ui-monospace,Consolas,monospace';
      ctx.fillText('输入 7×7', x0, h-6);
      // 卷积核
      var x1=x0+N*(cell+gap)+16;
      var kk=kernels[k];
      for(var r=0;r<K;r++) for(var c=0;c<K;c++){
        var X=x1+c*(cell+gap), Y=y0+r*(cell+gap), v=kk[r][c];
        ctx.fillStyle = v>0 ? 'rgba(156,59,46,'+Math.min(.75,v*.7)+')' : (v<0?'rgba(27,74,107,'+Math.min(.75,-v*.6)+')':C.surface());
        ctx.fillRect(X,Y,cell,cell);
        if(cell>16){ ctx.fillStyle=C.ink(); ctx.font='9px ui-monospace,Consolas,monospace'; ctx.fillText(v.toFixed(2).replace('-','−'), X+2, Y+cell-3); }
      }
      ctx.fillStyle=C.ink3(); ctx.fillText('卷积核 3×3', x1, h-6);
      // 输出
      var x2=x1+K*(cell+gap)+18, M=N-K+1;
      for(var r=0;r<M;r++) for(var c=0;c<M;c++){
        var sum=0;
        for(var i=0;i<K;i++) for(var j=0;j<K;j++){ sum += input(r+i, c+j)*kk[i][j]; }
        var v=Math.max(0,Math.min(1,sum));
        var X=x2+c*(cell+gap), Y=y0+r*(cell+gap);
        ctx.fillStyle='rgba(20,30,32,'+(0.05+v*0.7)+')'; ctx.fillRect(X,Y,cell,cell);
        if(cell>16){ ctx.fillStyle=v>0.5?'#fff':C.ink3(); ctx.font='9px ui-monospace,Consolas,monospace'; ctx.fillText(v.toFixed(1), X+2, Y+cell-3); }
      }
      ctx.fillStyle=C.ink3(); ctx.fillText('特征图 5×5', x2, h-6);
      // 加权和读数
      var parts=[], sum=0;
      for(var i2=0;i2<K;i2++) for(var j2=0;j2<K;j2++){
        var iv=input(oy+i2, ox+j2), kv=kernels[k][i2][j2];
        sum += iv*kv;
        if(Math.abs(kv)>0.001) parts.push(iv.toFixed(1)+'×'+kv.toFixed(2).replace('-','−'));
      }
      if(read) read.textContent = '窗口左上角 ('+oy+','+ox+') · '+parts.join(' + ')+' = '+sum.toFixed(2);
    }
    ksel.forEach(function(b){ b.addEventListener('click', function(){
      k=b.getAttribute('data-k'); ksel.forEach(function(x){x.style.borderColor='';}); b.style.borderColor='var(--accent)'; draw(); }); });
    psel.forEach(function(b){ b.addEventListener('click', function(){
      pat=b.getAttribute('data-p'); psel.forEach(function(x){x.style.borderColor='';}); b.style.borderColor='var(--accent)'; draw(); }); });
    cv.addEventListener('click', function(e){
      var r=cv.getBoundingClientRect(), x=e.clientX-r.left, y=e.clientY-r.top;
      var pad=10, cell=(cv.clientWidth-pad*2)/(N+N-K+1+N-K+1+1.6), gap=Math.min(2,cv.clientWidth/300);
      var y0=(cv.clientHeight-(N*cell+(N-1)*gap))/2;
      var c=Math.floor((x-pad)/(cell+gap)), rr=Math.floor((y-y0)/(cell+gap));
      if(c>=0&&c<N-K+1&&rr>=0&&rr<N-K+1){ ox=c; oy=rr; draw(); }
    });
    W_REDRAW.push(draw);
    draw();
  }

  /* ---- 4. 注意力热图 ---- */
  function attention(el){
    var toks = ['输入','的','每个','词','都','在','看','所有','词'];
    var base = [
      [.42,.10,.08,.06,.10,.06,.06,.06,.06],
      [.18,.16,.10,.08,.14,.10,.08,.08,.08],
      [.22,.14,.12,.06,.12,.10,.08,.08,.08],
      [.16,.10,.26,.08,.10,.10,.06,.06,.08],
      [.14,.08,.10,.10,.20,.12,.08,.08,.10],
      [.20,.10,.10,.08,.12,.14,.08,.08,.10],
      [.16,.12,.10,.08,.14,.12,.12,.06,.10],
      [.18,.08,.10,.06,.10,.08,.10,.18,.12],
      [.15,.09,.09,.07,.11,.09,.09,.11,.20]
    ];
    var wrap=el.querySelector('[data-heat]'), read=el.querySelector('[data-read]'), causal=false, maskBtn=el.querySelector('[data-mask]');
    function weights(row){
      var v = base[row].slice();
      for(var j=0;j<v.length;j++){ if(causal && j>row) v[j]=0; }
      var s=0; v.forEach(function(x){s+=x;}); return v.map(function(x){return x/(s||1);});
    }
    function draw(){
      var html='<div style="display:grid;grid-template-columns:2.9rem repeat(9,minmax(0,1fr));gap:2px;font-family:var(--mono);font-size:.62rem">';
      html+='<div></div>';
      toks.forEach(function(t){ html+='<div style="writing-mode:vertical-rl;text-orientation:upright;height:3rem;color:var(--ink-3);overflow:hidden">'+t+'</div>'; });
      toks.forEach(function(row,i){
        html+='<div style="color:var(--ink-3);display:flex;align-items:center;height:1.55rem">'+row+'</div>';
        var ws=weights(i);
        ws.forEach(function(p,j){
          var a=Math.min(.92, p*2.6);
          html+='<div data-cell="'+i+','+j+'" title="'+row+'→'+toks[j]+' : '+p.toFixed(3)+'" style="height:1.55rem;background:rgba(156,59,46,'+a.toFixed(3)+');display:flex;align-items:center;justify-content:center;color:'+(a>.45?'#fff':'var(--ink)')+';cursor:pointer">'+(p>0.14?Math.round(p*100):'')+'</div>';
        });
      });
      html+='</div>';
      wrap.innerHTML=html;
      wrap.querySelectorAll('[data-cell]').forEach(function(c){
        c.addEventListener('click', function(){
          var ij=c.getAttribute('data-cell').split(','), i=+ij[0], ws=weights(i), s=[];
          ws.forEach(function(p,j){ if(p>0.08) s.push(toks[j]+' '+(p*100).toFixed(0)+'%'); });
          read.textContent = '「'+toks[i]+'」的注意力分配：'+s.join('，');
        });
      });
      read.textContent = causal ? '因果掩码开启：第 i 行只能看到 j ≤ i 的词。点任一格看该词的分配。' : '点任一格查看该行词的注意力分配。数值为该行百分比。';
    }
    maskBtn.addEventListener('click', function(){
      causal=!causal; maskBtn.textContent = causal?'关闭因果掩码':'开启因果掩码'; draw();
    });
    W_REDRAW.push(draw);
    draw();
  }

  /* ---- 5. KV cache 显存账本 ---- */
  function kvcache(el){
    var inputs = el.querySelectorAll('[data-pt]'), read=el.querySelector('[data-read]'), bars=el.querySelector('[data-bars]');
    var dt = el.querySelector('[data-dtype]');
    function val(k){ var i=el.querySelector('[data-pt="'+k+'"]'); return parseFloat(i.value); }
    function draw(){
      var L=val('L'), H=val('dim'), S=val('seq'), B=val('b'), bytes = dt.value==='fp16'?2:1;
      var kvBytes = 2 * L * S * H * B * bytes;          // K 与 V，各 L×S×H
      var kvGB = kvBytes/Math.pow(1024,3);
      var wParams = 7e9, wGB = wParams*bytes/Math.pow(1024,3);
      el.querySelectorAll('[data-out]').forEach(function(o){ o.textContent = Math.round(val(o.getAttribute('data-out'))); });
      if(!bars) return;
      var total=kvGB+wGB, kp=kvGB/total*100, wp=wGB/total*100;
      bars.innerHTML =
        '<div style="font-family:var(--mono);font-size:.7rem;display:flex;justify-content:space-between"><span>KV cache '+kvGB.toFixed(2)+' GB</span><span>'+kp.toFixed(0)+'%</span></div>'+
        '<div style="height:14px;background:var(--accent);width:'+kp.toFixed(1)+'%"></div>'+
        '<div style="font-family:var(--mono);font-size:.7rem;display:flex;justify-content:space-between;margin-top:.5rem"><span>权重（7B, '+(bytes===2?'FP16':'INT8')+'） '+wGB.toFixed(2)+' GB</span><span>'+wp.toFixed(0)+'%</span></div>'+
        '<div style="height:14px;background:var(--ink-3);width:'+wp.toFixed(1)+'%"></div>';
      read.textContent = 'KV = 2 × L('+L+') × S('+S+') × H('+H+') × B('+B+') × '+(bytes*8)+'bit = '+kvGB.toFixed(2)+' GB　（batch 为并发序列数）';
    }
    inputs.forEach(function(i){ i.addEventListener('input', draw); });
    dt.addEventListener('change', draw);
    W_REDRAW.push(draw); draw();
  }

  /* ---- 6. 多项式拟合：过拟合 ---- */
  function fitpoly(el){
    var cv=el.querySelector('canvas'), deg=el.querySelector('[data-deg]'), out=el.querySelector('[data-degout]'), read=el.querySelector('[data-read]');
    var D = [[0.02,0.55],[0.10,0.72],[0.18,0.62],[0.27,0.95],[0.36,0.80],[0.45,1.22],[0.54,1.02],[0.63,1.15],[0.72,0.98],[0.81,1.02],[0.90,0.86],[0.97,0.80]];
    function solve(A,b){
      var n=A.length;
      for(var i=0;i<n;i++){
        var piv=i; for(var r=i+1;r<n;r++){ if(Math.abs(A[r][i])>Math.abs(A[piv][i])) piv=r; }
        var tmp=A[piv]; A[piv]=A[i]; A[i]=tmp; var tb=b[piv]; b[piv]=b[i]; b[i]=tb;
        if(Math.abs(A[i][i])<1e-12) continue;
        for(var r2=i+1;r2<n;r2++){
          var f=A[r2][i]/A[i][i];
          for(var c=i;c<n;c++) A[r2][c]-=f*A[i][c];
          b[r2]-=f*b[i];
        }
      }
      var x=new Array(n);
      for(var i2=n-1;i2>=0;i2--){
        var s=b[i2]; for(var j=i2+1;j<n;j++) s-=A[i2][j]*x[j];
        x[i2]= Math.abs(A[i2][i2])<1e-12 ? 0 : s/A[i2][i2];
      }
      return x;
    }
    function fit(d){
      var n=d+1, A=[], b=[];
      for(var i=0;i<n;i++){ A.push(new Array(n).fill(0)); b.push(0); }
      D.forEach(function(pt){
        var basis=[]; for(var k=0;k<n;k++) basis.push(Math.pow(pt[0],k));
        for(var i2=0;i2<n;i2++){ for(var j2=0;j2<n;j2++) A[i2][j2]+=basis[i2]*basis[j2]; b[i2]+=basis[i2]*pt[1]; }
      });
      for(var i3=0;i3<n;i3++) A[i3][i3]+= 1e-6;  // 轻微脊正则，稳定高阶病态
      return solve(A,b);
    }
    function draw(){
      var d=parseInt(deg.value,10); out.textContent=d;
      var s=setupCanvas(cv,0.52), ctx=s.ctx, w=s.w, h=s.h;
      ctx.clearRect(0,0,w,h); ctx.fillStyle=C.paper(); ctx.fillRect(0,0,w,h);
      var padL=30, padR=12, padT=12, padB=24;
      var X=function(x){ return padL + x*(w-padL-padR); };
      var Y=function(y){ return h-padB - (y-0.4)/1.1*(h-padT-padB); };
      ctx.strokeStyle=C.rule(); ctx.lineWidth=1;
      ctx.beginPath(); ctx.moveTo(padL,padT); ctx.lineTo(padL,h-padB); ctx.lineTo(w-padR,h-padB); ctx.stroke();
      ctx.fillStyle=C.ink3(); ctx.font='10px ui-monospace,Consolas,monospace';
      ctx.fillText('x', w-padR-6, h-padB+14); ctx.fillText('y', padL-6, padT+8);
      var co=fit(d), train=0;
      D.forEach(function(pt){
        var yh=0; for(var k=0;k<co.length;k++) yh+=co[k]*Math.pow(pt[0],k);
        train += Math.pow(yh-pt[1],2);
        ctx.strokeStyle=C.rule(); ctx.lineWidth=1;
        ctx.beginPath(); ctx.moveTo(X(pt[0]), Y(pt[1])); ctx.lineTo(X(pt[0]), Y(yh)); ctx.stroke();
        ctx.beginPath(); ctx.arc(X(pt[0]), Y(pt[1]), 2.6, 0, Math.PI*2); ctx.fillStyle=C.ink(); ctx.fill();
      });
      var pts=[];
      for(var i=0;i<=120;i++){
        var x=i/120, y=0;
        for(var k2=0;k2<co.length;k2++) y+=co[k2]*Math.pow(x,k2);
        pts.push([X(x),Y(Math.max(0.25,Math.min(1.6,y)))]);
      }
      ctx.beginPath(); pts.forEach(function(p,i){ i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]); });
      ctx.strokeStyle=C.accent(); ctx.lineWidth=2; ctx.stroke();
      var rmse=Math.sqrt(train/D.length);
      read.textContent = '训练 RMSE = '+rmse.toFixed(3)+'　（次数越高，曲线越能穿过每个点，但对新数据的方差越大）';
    }
    deg.addEventListener('input', draw);
    W_REDRAW.push(draw); draw();
  }

  var MAP = {gradient:gradient, softmax:softmax, conv:conv, attention:attention, kvcache:kvcache, fitpoly:fitpoly};
  window.__initWidgets = function(){
    $all('[data-widget]').forEach(function(el){
      var fn = MAP[el.getAttribute('data-widget')];
      if(fn){ try{ fn(el); }catch(e){ console.warn(e); } }
    });
  };
})();
"""

HERO_JS = r"""
/* ============ 首屏动画 ============ */
(function(){
  var cv = document.getElementById('heroCanvas');
  if(!cv) return;
  var scene = cv.getAttribute('data-scene');
  var ctx = cv.getContext('2d'), W=0, H=0, dpr = Math.min(2, window.devicePixelRatio||1);
  function size(){
    var r = cv.parentElement.getBoundingClientRect();
    W = r.width; H = r.height;
    cv.width = Math.round(W*dpr); cv.height = Math.round(H*dpr);
    cv.style.width = W+'px'; cv.style.height = H+'px';
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }
  size(); window.addEventListener('resize', size);

  var t0 = performance.now();
  function accent(){ return getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()||'#9C3B2E'; }

  function drawGradient(t){
    ctx.clearRect(0,0,W,H);
    var cx=W*0.68, cy=H*0.46, sx=Math.min(W,H)/5.2;
    var k;
    for(k=1;k<=16;k++){
      var r=k*0.24*sx;
      ctx.beginPath(); ctx.ellipse(cx,cy,r*1.32,r*0.78,0,0,Math.PI*2);
      ctx.strokeStyle='rgba(237,241,234,'+(0.05+k*0.006)+')'; ctx.lineWidth=1; ctx.stroke();
    }
    // 网格
    ctx.strokeStyle='rgba(237,241,234,.06)';
    for(k=0;k<W;k+=36){ ctx.beginPath(); ctx.moveTo(k,0); ctx.lineTo(k,H); ctx.stroke(); }
    for(k=0;k<H;k+=36){ ctx.beginPath(); ctx.moveTo(0,k); ctx.lineTo(W,k); ctx.stroke(); }
    // 下降轨迹（循环）
    var p=[2.9,1.9], lr=0.28, path=[p.slice()];
    for(var i=0;i<160;i++){ p=[p[0]-lr*1.24*p[0], p[1]-lr*3.1*p[1]]; path.push(p.slice()); if(Math.abs(p[0])<0.002&&Math.abs(p[1])<0.002) break; }
    var T = 6.5, prog = (t % T)/T, idx = Math.min(path.length-1, Math.floor(prog*path.length*1.05));
    ctx.beginPath();
    for(var j=0;j<=idx;j++){ var X=cx+path[j][0]*sx, Y=cy-path[j][1]*sx; j?ctx.lineTo(X,Y):ctx.moveTo(X,Y); }
    ctx.strokeStyle=accent(); ctx.lineWidth=1.4; ctx.globalAlpha=.85; ctx.stroke(); ctx.globalAlpha=1;
    var q=path[idx], QX=cx+q[0]*sx, QY=cy-q[1]*sx;
    var g=[1.24*q[0],3.1*q[1]], n=Math.hypot(g[0],g[1])||1, len=40;
    ctx.beginPath(); ctx.moveTo(QX,QY); ctx.lineTo(QX-g[0]/n*len, QY+g[1]/n*len);
    ctx.strokeStyle=accent(); ctx.lineWidth=2.2; ctx.stroke();
    ctx.beginPath(); ctx.arc(QX,QY,4,0,Math.PI*2); ctx.fillStyle=accent(); ctx.fill();
    ctx.beginPath(); ctx.arc(cx,cy,2.5,0,Math.PI*2); ctx.fillStyle='rgba(237,241,234,.5)'; ctx.fill();
    ctx.font='11px ui-monospace,Consolas,monospace'; ctx.fillStyle='rgba(237,241,234,.34)';
    ctx.fillText('θ  ←  θ − η∇L(θ)', 22, H-24);
    ctx.fillText('f(x,y)=0.62x²+1.55y²', cx-sx*2.4, cy+sx*1.5);
  }

  function drawMap(t){
    ctx.clearRect(0,0,W,H);
    var nodes=[
      {x:.72,y:.16,l:'数学'},
      {x:.55,y:.34,l:'机器学习'},
      {x:.78,y:.42,l:'深度学习'},
      {x:.86,y:.66,l:'大模型'},
      {x:.62,y:.66,l:'强化学习'},
      {x:.44,y:.56,l:'工程部署'},
      {x:.70,y:.86,l:'应用与智能体'}
    ];
    var edges=[[0,1],[1,2],[2,3],[1,4],[1,5],[5,3],[3,6],[4,6],[5,6],[2,5]];
    var cx=W*0.72, cy=H*0.52;
    edges.forEach(function(e,ei){
      var a=nodes[e[0]], b=nodes[e[1]];
      var ax=a.x*W*0.8+W*0.1, ay=a.y*H, bx=b.x*W*0.8+W*0.1, by=b.y*H;
      ctx.beginPath(); ctx.moveTo(ax,ay);
      ctx.quadraticCurveTo((ax+bx)/2+(ei%2?12:-12),(ay+by)/2, bx,by);
      ctx.strokeStyle='rgba(237,241,234,.16)'; ctx.lineWidth=1; ctx.stroke();
      var ph=((t/4)+ei/edges.length)%1, tt=ph;
      var px=(1-tt)*(1-tt)*ax+2*(1-tt)*tt*((ax+bx)/2+(ei%2?12:-12))+tt*tt*bx;
      var py=(1-tt)*(1-tt)*ay+2*(1-tt)*tt*((ay+by)/2)+tt*tt*by;
      ctx.beginPath(); ctx.arc(px,py,2.2,0,Math.PI*2); ctx.fillStyle=accent(); ctx.globalAlpha=.8; ctx.fill(); ctx.globalAlpha=1;
    });
    nodes.forEach(function(nd,i){
      var x=nd.x*W*0.8+W*0.1, y=nd.y*H;
      var pull=Math.sin(t/2.4+i)*1.6;
      ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(x,y); ctx.strokeStyle='rgba(237,241,234,.05)'; ctx.stroke();
      ctx.beginPath(); ctx.arc(x,y,3.5+pull,0,Math.PI*2); ctx.fillStyle=i===3?accent():'rgba(237,241,234,.55)'; ctx.fill();
      ctx.font='11px ui-monospace,Consolas,monospace'; ctx.fillStyle='rgba(237,241,234,.42)';
      ctx.fillText(nd.l, x+9, y+4);
    });
    ctx.font='10px ui-monospace,Consolas,monospace'; ctx.fillStyle='rgba(237,241,234,.26)';
    ctx.fillText('知识不是一条直线，而是互相引用的网', W*0.5, H-22);
  }

  function drawStream(t){
    ctx.clearRect(0,0,W,H);
    var toks=['<','B','O','S','>','深','度','学','习','的','本','质','是','函','数','逼','近'];
    var y0=H*0.42, x0=W*0.5, gap=Math.min(46, (W*0.46)/toks.length);
    ctx.font='11px ui-monospace,Consolas,monospace';
    toks.forEach(function(tk,i){
      var ph=(t/7 - i*0.06)%1; if(ph<0) ph+=1;
      var x=x0+i*gap, y=y0 + Math.sin(ph*Math.PI*2)*3;
      var a = ph<0.75 ? 0.85 : 0.85-(ph-0.75)*2.8;
      ctx.globalAlpha=Math.max(.12,a);
      ctx.strokeStyle='rgba(237,241,234,.3)'; ctx.strokeRect(x,y-13,Math.max(16,ctx.measureText(tk).width+8),20);
      ctx.fillStyle='rgba(237,241,234,.8)'; ctx.fillText(tk,x+4,y+2);
      ctx.globalAlpha=1;
    });
    // 注意力矩阵
    var n=7, cell=Math.min(26, W/26), mx=W*0.68, my=H*0.1;
    for(var i=0;i<n;i++) for(var j=0;j<n;j++){
      var wgt = (j<=i? (0.15+0.3*Math.abs(Math.sin(i*0.7+j*0.4+t*0.25))) : 0.03);
      ctx.fillStyle='rgba(156,59,46,'+wgt.toFixed(3)+')';
      ctx.fillRect(mx+j*(cell+2), my+i*(cell+2), cell, cell);
    }
    ctx.strokeStyle='rgba(237,241,234,.18)';
    ctx.strokeRect(mx-1, my-1, n*(cell+2)+1, n*(cell+2)+1);
    ctx.fillStyle='rgba(237,241,234,.32)';
    ctx.fillText('attention: 每个位置看到哪些位置', mx-2, my+n*(cell+2)+18);
    // 光束
    var beamX = mx-20 + Math.sin(t*0.6)*8;
    ctx.beginPath(); ctx.moveTo(x0+toks.length*gap, y0); ctx.lineTo(beamX, my+n*cell/2);
    ctx.strokeStyle='rgba(156,59,46,.35)'; ctx.lineWidth=1.2; ctx.stroke();
  }

  var DRAW = {gradient:drawGradient, map:drawMap, stream:drawStream}[scene] || drawGradient;
  if(REDUCE){ DRAW(3.2); return; }
  function loop(now){
    DRAW((now-t0)/1000);
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
  document.addEventListener('visibilitychange', function(){ if(!document.hidden){ t0 = performance.now(); } });
})();
"""

EXERCISE_JS = r"""
/* ============ 章末动作 ============ */
(function(){
  document.addEventListener('click', function(e){
    var b = e.target.closest('[data-fold]');
    if(!b) return;
    var box = document.getElementById(b.getAttribute('data-fold'));
    if(!box) return;
    var on = box.hasAttribute('hidden');
    if(on){ box.removeAttribute('hidden'); b.textContent='收起答案'; }
    else { box.setAttribute('hidden',''); b.textContent='看答案'; }
  });
})();
"""
