CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
:root{
  --paper:#F2F3EF;
  --paper-2:#E9EBE4;
  --surface:#FFFFFF;
  --ink:#141A1B;
  --ink-2:#4B5658;
  --ink-3:#7E8A8C;
  --rule:#D9DCD3;
  --rule-2:#BFC4B8;
  --accent:#9C3B2E;
  --accent-deep:#742A20;
  --accent-wash:#F1E4E0;
  --hero-bg:#12181A;
  --hero-ink:#EFF2EC;
  --mono:"Cascadia Code","JetBrains Mono",Consolas,"SFMono-Regular",ui-monospace,monospace;
  --sans:"HarmonyOS Sans SC","Microsoft YaHei UI","Microsoft YaHei","PingFang SC",system-ui,sans-serif;
  --serif:"Noto Serif SC","Source Han Serif SC","Songti SC",Georgia,serif;
  --doc-size:17.5px;
  --rail:17.5rem;
}
[data-theme="dark"]{
  --paper:#111719;
  --paper-2:#182024;
  --surface:#161E21;
  --ink:#E6EAE3;
  --ink-2:#A7B2B3;
  --ink-3:#7C888A;
  --rule:#283336;
  --rule-2:#374447;
  --accent-wash:#222B2C;
  --hero-bg:#0C1113;
  --hero-ink:#EDF1EA;
}
html[data-theme="dark"] body{background:var(--paper);color:var(--ink)}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--sans);font-size:var(--doc-size);line-height:1.85;
  letter-spacing:.01em;
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}
img{max-width:100%;height:auto}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid color-mix(in oklab,var(--accent) 35%,transparent)}
a:hover{border-bottom-color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}

/* ---------- 布局 ---------- */
.shell{display:block}
.rail{
  position:fixed;inset:0 auto 0 0;width:86vw;max-width:20rem;z-index:60;
  background:var(--paper);border-right:1px solid var(--rule);
  transform:translateX(-102%);transition:transform .28s cubic-bezier(.2,.7,.2,1);
  display:flex;flex-direction:column;overflow:hidden;
}
.rail.open{transform:translateX(0);box-shadow:0 0 0 100vmax rgba(10,14,15,.42)}
.doc{min-width:0}
@media (min-width:900px){
  .shell{display:grid;grid-template-columns:var(--rail) minmax(0,1fr)}
  .rail{position:sticky;top:0;transform:none;width:auto;max-width:none;height:100vh;box-shadow:none}
  .rail-toggle{display:none}
  .rail-scrim{display:none}
}

.rail-scrim{position:fixed;inset:0;background:rgba(10,14,15,.42);z-index:55;opacity:0;pointer-events:none;transition:opacity .25s}
.rail.open+.rail-scrim{opacity:1;pointer-events:auto}

/* ---------- 侧栏 ---------- */
.rail-head{padding:1.15rem 1.15rem .85rem;border-bottom:1px solid var(--rule)}
.series{font-family:var(--mono);font-size:.68rem;letter-spacing:.14em;color:var(--accent);margin:0 0 .5rem}
.rail-title{font-size:.98rem;font-weight:600;line-height:1.5;margin:0;letter-spacing:.01em}
.rail-sub{font-size:.74rem;color:var(--ink-3);margin:.35rem 0 0;line-height:1.5}
.rail-search{padding:.8rem 1.15rem 0}
.search-wrap{position:relative}
#q{
  width:100%;font-family:var(--sans);font-size:16px;color:var(--ink);
  background:var(--surface);border:1px solid var(--rule-2);padding:.5rem .6rem;
  border-radius:0;appearance:none;
}
#q::placeholder{color:var(--ink-3)}
#q:focus{outline:none;border-color:var(--accent)}
.search-hint{font-size:.7rem;color:var(--ink-3);padding:.35rem .1rem 0}
.search-panel{
  position:absolute;left:0;right:0;top:calc(100% + 4px);max-height:52vh;overflow:auto;
  background:var(--surface);border:1px solid var(--rule-2);z-index:70;display:none;
}
.search-panel.on{display:block}
.sr-item{padding:.55rem .6rem;border-bottom:1px solid var(--rule);cursor:pointer;font-size:.8rem;line-height:1.5}
.sr-item:hover{background:var(--accent-wash)}
.sr-t{font-weight:600;display:block}
.sr-x{color:var(--ink-3);font-size:.72rem}
.sr-empty{padding:.7rem;font-size:.78rem;color:var(--ink-3)}

.toc{overflow:auto;flex:1;padding:.4rem 0 2rem;scrollbar-width:thin}
.toc-group{border:0}
.ch-link{
  display:grid;grid-template-columns:2.1rem 1fr;gap:.35rem;align-items:baseline;
  padding:.45rem 1.15rem;cursor:pointer;border:0;background:none;width:100%;text-align:left;
  font-family:var(--sans);color:var(--ink-2);font-size:.82rem;line-height:1.45;
}
.ch-link:hover{color:var(--accent)}
.ch-link .n{font-family:var(--mono);font-size:.7rem;color:var(--ink-3);text-align:right}
.ch-link.active{color:var(--accent);font-weight:600}
.ch-link.active .n{color:var(--accent)}
.sub-list{padding:0 1.15rem .5rem 3.35rem}
.sub-link{display:block;width:100%;text-align:left;border:0;background:none;cursor:pointer;
  font-family:var(--sans);font-size:.75rem;color:var(--ink-3);padding:.18rem 0;line-height:1.4}
.sub-link:hover{color:var(--accent)}
.rail-foot{border-top:1px solid var(--rule);padding:.6rem 1.15rem;display:flex;align-items:center;gap:.6rem}
.rail-foot .meter{flex:1;height:3px;background:var(--rule);position:relative}
.rail-foot .meter i{position:absolute;inset:0 auto 0 0;width:0%;background:var(--accent)}
.rail-foot .pct{font-family:var(--mono);font-size:.68rem;color:var(--ink-3)}

/* ---------- 顶栏控件 ---------- */
.hud{
  position:fixed;right:.8rem;bottom:.9rem;z-index:50;display:flex;gap:.35rem;
  background:color-mix(in oklab,var(--surface) 92%,transparent);
  border:1px solid var(--rule-2);padding:.3rem;backdrop-filter:blur(6px);
}
.hud button{
  font-family:var(--mono);font-size:.72rem;font-variant-numeric:tabular-nums;
  background:none;border:0;color:var(--ink-2);padding:.45rem .55rem;cursor:pointer;min-height:34px
}
.hud button:hover{color:var(--accent);background:var(--accent-wash)}
.rail-toggle{
  position:fixed;left:.8rem;bottom:.9rem;z-index:50;background:var(--ink);color:var(--paper);
  border:0;padding:.6rem .85rem;font-family:var(--sans);font-size:.78rem;cursor:pointer;min-height:44px
}
.progressbar{position:fixed;top:0;left:0;height:2px;background:var(--accent);width:0;z-index:80;transition:width .1s linear}

/* ---------- 首屏 ---------- */
.cover{
  position:relative;background:var(--hero-bg);color:var(--hero-ink);
  min-height:88svh;display:flex;flex-direction:column;justify-content:flex-end;
  overflow:hidden;padding:4.5rem 1.35rem 2.2rem;
}
@media (min-width:900px){.cover{padding:5rem 3.2rem 3rem;min-height:86vh}}
#heroCanvas{position:absolute;inset:0;width:100%;height:100%;opacity:.9}
.cover-inner{position:relative;z-index:2;max-width:52rem}
.cover-kicker{font-family:var(--mono);font-size:.7rem;letter-spacing:.16em;color:color-mix(in oklab,var(--hero-ink) 62%,transparent);margin:0 0 1.1rem}
.cover h1{
  font-size:clamp(1.9rem,6.2vw,3.5rem);line-height:1.16;font-weight:600;margin:0 0 .9rem;
  letter-spacing:-.01em;max-width:22ch;
}
.cover h1 em{font-style:normal;color:var(--accent)}
.cover-lede{font-size:clamp(.92rem,2.6vw,1.05rem);line-height:1.75;color:color-mix(in oklab,var(--hero-ink) 78%,transparent);max-width:38rem;margin:0 0 1.6rem}
.cover-meta{display:flex;flex-wrap:wrap;gap:.5rem 1.4rem;font-family:var(--mono);font-size:.7rem;color:color-mix(in oklab,var(--hero-ink) 58%,transparent);border-top:1px solid rgba(255,255,255,.16);padding-top:.9rem}
.cover-meta span b{color:var(--hero-ink);font-weight:600}

/* ---------- 正文 ---------- */
.article-wrap{padding:0 1.1rem}
@media (min-width:900px){.article-wrap{padding:0 3.2rem}}
article{padding:2.4rem 0 1rem;max-width:47rem}
@media (min-width:900px){article{padding:3.4rem 0 2rem}}

.chapter{padding-top:.4rem;margin-bottom:3.4rem;scroll-margin-top:1rem}
.ch-head{border-top:2px solid var(--ink);padding-top:.75rem;margin-bottom:1.6rem}
.ch-num{font-family:var(--mono);font-size:.74rem;letter-spacing:.1em;color:var(--accent);display:block;margin-bottom:.4rem}
.ch-head h2{font-size:clamp(1.35rem,4.4vw,1.9rem);line-height:1.3;margin:0 0 .6rem;font-weight:600;letter-spacing:-.005em}
.ch-abs{font-family:var(--serif);font-size:.92rem;line-height:1.8;color:var(--ink-2);margin:0;padding-left:.9rem;border-left:2px solid var(--rule-2)}
.ch-stats{font-family:var(--mono);font-size:.68rem;color:var(--ink-3);margin-top:.7rem}

h3{font-size:1.12rem;line-height:1.5;margin:2.2rem 0 .8rem;font-weight:600;letter-spacing:.004em}
h3 .sn{font-family:var(--mono);font-size:.78rem;color:var(--accent);font-weight:500;margin-right:.55rem;font-variant-numeric:tabular-nums}
h4{font-size:.98rem;margin:1.5rem 0 .5rem;font-weight:600;color:var(--ink)}
p{margin:0 0 1.05rem;text-align:left}
p.lead{font-size:1.02rem;color:var(--ink)}
strong{font-weight:600}
.dim{color:var(--ink-3)}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}

ul,ol{margin:0 0 1.15rem;padding-left:1.35rem}
li{margin-bottom:.45rem;line-height:1.8}
li ul,li ol{margin-top:.4rem;margin-bottom:.2rem}
ol li::marker{font-family:var(--mono);font-size:.86em;color:var(--accent)}

blockquote{margin:1.2rem 0;padding:.2rem 0 .2rem 1rem;border-left:2px solid var(--rule-2);color:var(--ink-2);font-family:var(--serif)}
hr{border:0;border-top:1px solid var(--rule);margin:2.2rem 0}

/* 提示块 */
.note{margin:1.3rem 0;padding:.1rem 0 .1rem .95rem;border-left:3px solid var(--accent);background:linear-gradient(90deg,var(--accent-wash),transparent 88%)}
.note .lbl{font-family:var(--mono);font-size:.68rem;letter-spacing:.08em;color:var(--accent);display:block;margin:.75rem 0 .2rem}
.note p{margin:.15rem 0 .8rem;font-size:.94rem;line-height:1.78}
.note.warn{border-left-color:#8A5A15;background:linear-gradient(90deg,#F3EBDA,transparent 88%)}
.note.warn .lbl{color:#8A5A15}
.note.eng{border-left-color:#1F4A63;background:linear-gradient(90deg,#E4EDF1,transparent 88%)}
.note.eng .lbl{color:#1F4A63}
[data-theme="dark"] .note.warn{background:linear-gradient(90deg,#2A2418,transparent 88%)}
[data-theme="dark"] .note.eng{background:linear-gradient(90deg,#16242C,transparent 88%)}

/* 代码 */
.code{margin:1.2rem 0;border:1px solid var(--rule-2);background:var(--surface)}
.code-head{display:flex;align-items:center;justify-content:space-between;padding:.3rem .6rem;border-bottom:1px solid var(--rule);font-family:var(--mono);font-size:.68rem;color:var(--ink-3)}
.code-head .lang{letter-spacing:.06em}
.code-head .copy{border:0;background:none;color:var(--ink-3);font-family:var(--mono);font-size:.68rem;cursor:pointer;padding:.25rem .4rem;min-height:30px}
.code-head .copy:hover{color:var(--accent)}
.code pre{margin:0;padding:.9rem .95rem;overflow-x:auto;font-family:var(--mono);font-size:.8rem;line-height:1.65;color:var(--ink);tab-size:2}
.code pre code{font-family:inherit}

/* 表格 */
.tbl{margin:1.3rem 0;overflow-x:auto}
table{width:100%;table-layout:fixed;border-collapse:collapse;font-size:.84rem;line-height:1.6}
th,td{border:1px solid var(--rule);padding:.5rem .55rem;vertical-align:top;text-align:left;word-break:break-word}
th{background:var(--paper-2);font-weight:600;font-size:.8rem;color:var(--ink)}
td .mono{font-size:.9em}

/* 公式 */
.math-block{margin:1.15rem 0;overflow-x:auto;overflow-y:hidden;padding:.15rem 0;text-align:center}
.math-block .katex{font-size:.98em}
.katex{font-size:.95em}
.formula-cap{font-family:var(--mono);font-size:.68rem;color:var(--ink-3);text-align:center;margin:-.6rem 0 1.1rem}

/* 图片 / SVG 图 */
.figure{margin:1.5rem 0;border:1px solid var(--rule);background:var(--surface);padding:.85rem}
.figure svg,.figure img{display:block;width:100%;height:auto}
.figcap{font-family:var(--mono);font-size:.7rem;color:var(--ink-3);margin-top:.55rem;line-height:1.5}

/* 实验台 */
.widget{margin:1.5rem 0;border:1px solid var(--rule-2);background:var(--surface)}
.widget-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:.4rem .9rem;padding:.55rem .75rem;border-bottom:1px solid var(--rule);background:var(--paper-2)}
.widget-head .w-title{font-size:.86rem;font-weight:600}
.widget-head .w-hint{font-family:var(--mono);font-size:.68rem;color:var(--ink-3)}
.widget-body{padding:.85rem .75rem}
.w-row{display:flex;flex-wrap:wrap;gap:.9rem;align-items:flex-start}
.w-col{flex:1 1 15rem;min-width:0}
.w-ctl{display:flex;align-items:center;gap:.6rem;font-size:.78rem;color:var(--ink-2);margin-bottom:.55rem}
.w-ctl label{min-width:4.4rem;color:var(--ink-2)}
.w-ctl output{font-family:var(--mono);font-size:.74rem;color:var(--accent);min-width:3.2rem}
input[type=range]{-webkit-appearance:none;appearance:none;flex:1;height:20px;background:none;cursor:pointer;min-width:6rem}
input[type=range]::-webkit-slider-runnable-track{height:2px;background:var(--rule-2)}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;margin-top:-6px;background:var(--accent);border:0;border-radius:0}
input[type=range]::-moz-range-track{height:2px;background:var(--rule-2)}
input[type=range]::-moz-range-thumb{width:14px;height:14px;background:var(--accent);border:0;border-radius:0}
.w-btn{font-family:var(--sans);font-size:.78rem;padding:.4rem .7rem;border:1px solid var(--ink);background:none;color:var(--ink);cursor:pointer;min-height:34px}
.w-btn:hover{background:var(--ink);color:var(--paper)}
.w-btn.primary{border-color:var(--accent);color:var(--accent)}
.w-btn.primary:hover{background:var(--accent);color:#fff}
.w-btn.sm{min-height:28px;padding:.2rem .5rem;font-size:.72rem}
.w-canvas{display:block;width:100%;height:auto;border:1px solid var(--rule);background:var(--paper)}
.w-note{font-family:var(--mono);font-size:.7rem;color:var(--ink-3);margin-top:.5rem;line-height:1.5}
.w-read{font-family:var(--mono);font-size:.74rem;color:var(--ink-2);margin-top:.4rem}

/* 习题 / 结束 */
.q-list{counter-reset:q;margin:1rem 0}
.q-item{counter-increment:q;margin:0 0 1rem;padding-bottom:.7rem;border-bottom:1px dotted var(--rule)}
.q-item::before{content:"Q" counter(q);font-family:var(--mono);font-size:.7rem;color:var(--accent);margin-right:.55rem}
.ch-end{border-top:1px solid var(--rule);margin-top:2rem;padding-top:.8rem;display:flex;justify-content:space-between;gap:1rem;font-family:var(--mono);font-size:.7rem;color:var(--ink-3)}
.ch-end button{border:0;background:none;color:var(--ink-2);font-family:var(--mono);font-size:.7rem;cursor:pointer;padding:.2rem 0}
.ch-end button:hover{color:var(--accent)}

footer.end{padding:2.5rem 1.1rem 5rem;border-top:1px solid var(--rule);color:var(--ink-3);font-size:.8rem;line-height:1.8}
@media (min-width:900px){footer.end{padding:2.5rem 3.2rem 5rem}}
footer.end .series-note{max-width:44rem}

.toast{position:fixed;left:50%;bottom:5.2rem;transform:translate(-50%,12px);background:var(--ink);color:var(--paper);font-size:.78rem;padding:.5rem .85rem;opacity:0;pointer-events:none;transition:.22s;z-index:90;font-family:var(--sans)}
.toast.on{opacity:1;transform:translate(-50%,0)}

@media (prefers-reduced-motion:reduce){
  *{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important}
}
@media print{
  .rail,.hud,.rail-toggle,.progressbar,.toast,.widget{display:none!important}
  .cover{min-height:auto;padding:2rem 0}
  #heroCanvas{display:none}
  body{font-size:10.5pt}
  .chapter{page-break-inside:auto}
  .code,.note{page-break-inside:avoid}
}
"""
