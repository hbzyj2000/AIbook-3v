# -*- coding: utf-8 -*-
"""把 content/*.md 组装成单文件交互式 HTML 教程。"""
import os, re, json, html, urllib.parse, sys
from theme_css import CSS
from theme_js import JS, WIDGETS_JS, HERO_JS, EXERCISE_JS

BASE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(BASE, '..', 'content')
OUT = os.path.join(BASE, '..')

KATEX_CSS = 'https://fastly.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css'
KATEX_JS = 'https://fastly.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js'

WIDGET_DEF = {
    'gradient': ('梯度下降实验台', '拖学习率、点画布换起点，观察步长与收敛的关系', '''
      <div class="w-row">
        <div class="w-col">
          <canvas class="w-canvas"></canvas>
          <div class="w-note">点一下画布任意位置可以换起点；箭头是负梯度方向。</div>
        </div>
        <div class="w-col" style="flex:0 1 13rem">
          <div class="w-ctl"><label>学习率 η</label><input type="range" data-lr min="0.02" max="0.62" step="0.01" value="0.28"><output data-lrout></output></div>
          <div style="display:flex;gap:.4rem;flex-wrap:wrap;margin:.2rem 0 .6rem">
            <button class="w-btn primary" data-run>运行</button>
            <button class="w-btn" data-step>单步</button>
            <button class="w-btn" data-reset>重置</button>
          </div>
          <div class="w-read" data-read></div>
          <div class="w-note">η 太小时像蜗牛，太大时会越过谷底甚至发散。</div>
        </div>
      </div>'''),
    'softmax': ('Softmax 温度实验台', '调 logits 与温度，看概率分布怎么变尖或变平', '''
      <div class="w-row">
        <div class="w-col" style="flex:0 1 16rem">
          <div class="w-ctl"><label>logit A</label><input type="range" data-logit min="-3" max="5" step="0.1" value="2.4"></div>
          <div class="w-ctl"><label>logit B</label><input type="range" data-logit min="-3" max="5" step="0.1" value="1.2"></div>
          <div class="w-ctl"><label>logit C</label><input type="range" data-logit min="-3" max="5" step="0.1" value="0.4"></div>
          <div class="w-ctl"><label>logit D</label><input type="range" data-logit min="-3" max="5" step="0.1" value="-0.8"></div>
        </div>
        <div class="w-col">
          <div class="w-ctl"><label>温度 T</label><input type="range" data-temp min="0.2" max="6" step="0.05" value="1"><output data-tout></output></div>
          <div data-bars></div>
          <div class="w-read" data-read></div>
        </div>
      </div>'''),
    'conv': ('卷积滑窗实验台', '换核与图案、点输入网格移动窗口，看特征图怎样被算出来', '''
      <div style="display:flex;gap:.4rem;flex-wrap:wrap;margin-bottom:.6rem">
        <button class="w-btn sm" data-k="edge" style="border-color:var(--accent)">竖直边缘</button>
        <button class="w-btn sm" data-k="blur">均值模糊</button>
        <button class="w-btn sm" data-k="sharpen">锐化</button>
        <span style="width:.4rem"></span>
        <button class="w-btn sm" data-p="hline" style="border-color:var(--accent)">横边</button>
        <button class="w-btn sm" data-p="diag">斜线</button>
        <button class="w-btn sm" data-p="dot">圆点</button>
        <button class="w-btn sm" data-p="noise">纹理</button>
      </div>
      <canvas class="w-canvas"></canvas>
      <div class="w-read" data-read></div>'''),
    'attention': ('注意力热图', '点任一格，看一个词把注意力分给了谁；试试因果掩码', '''
      <div style="display:flex;gap:.5rem;align-items:center;margin-bottom:.6rem;flex-wrap:wrap">
        <button class="w-btn sm" data-mask>开启因果掩码</button>
        <span class="w-note" style="margin:0">掩码 = 解码阶段不许看后面的词</span>
      </div>
      <div data-heat></div>
      <div class="w-read" data-read></div>'''),
    'kvcache': ('KV cache 显存账本', '改层数、隐藏维、序列长度与并发，看推理显存花在哪', '''
      <div class="w-row">
        <div class="w-col" style="flex:0 1 15rem">
          <div class="w-ctl"><label>层数 L</label><input type="range" data-pt="L" min="6" max="96" step="1" value="32"><output data-out="L"></output></div>
          <div class="w-ctl"><label>隐藏维 H</label><input type="range" data-pt="dim" min="512" max="16384" step="512" value="4096"><output data-out="dim"></output></div>
          <div class="w-ctl"><label>序列 S</label><input type="range" data-pt="seq" min="256" max="32768" step="256" value="4096"><output data-out="seq"></output></div>
          <div class="w-ctl"><label>并发 B</label><input type="range" data-pt="b" min="1" max="64" step="1" value="8"><output data-out="b"></output></div>
          <div class="w-ctl"><label>精度</label>
            <select data-dtype style="font-size:16px;padding:.25rem"><option value="fp16">FP16</option><option value="int8">INT8</option></select></div>
        </div>
        <div class="w-col" data-bars></div>
      </div>
      <div class="w-read" data-read></div>''' ),
    'fitpoly': ('过拟合实验台', '同一批数据，把多项式次数从 1 拉到 9，看训练误差与泛化', '''
      <div class="w-ctl"><label>多项式次数</label><input type="range" data-deg min="1" max="9" step="1" value="1"><output data-degout></output></div>
      <canvas class="w-canvas"></canvas>
      <div class="w-read" data-read></div>'''),
}

CHAPTER_DEFAULT_READ = 4

def esc(s):
    return html.escape(s, quote=False)

def attr(s):
    return html.escape(s, quote=True)

# ---------------- 行内解析 ----------------
def inline(text):
    """返回 html：保护 math 与 code，处理粗体/斜体/链接。"""
    slots = []
    def stash(html_frag):
        slots.append(html_frag)
        return '\x00%d\x00' % (len(slots) - 1)

    def code_repl(m):
        return stash('<code>%s</code>' % esc(m.group(1)))

    text = re.sub(r'`([^`]+)`', code_repl, text)

    def math_repl(m):
        tex = m.group(1)
        return stash('<span class="m-inline" data-tex="%s">%s</span>' % (attr(tex), esc(tex)))

    text = re.sub(r'\$([^$\n]+?)\$', math_repl, text)

    text = esc(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<![\w*])\*([^*\n]+?)\*(?![\w*])', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: '<a href="%s">%s</a>' % (attr(m.group(2)), m.group(1)), text)
    for i, frag in enumerate(slots):
        text = text.replace('\x00%d\x00' % i, frag)
    return text

def raw_math(s):
    """原样透传的 HTML 片段里，仅把 $...$ 转成公式节点，其余不动。"""
    def repl(m):
        tex = m.group(1)
        return '<span class="m-inline" data-tex="%s">%s</span>' % (attr(tex), esc(tex))
    return re.sub(r'\$([^$\n]+?)\$', repl, s)

def render_table(rows):
    header, sep, body = rows[0], rows[1], rows[2:]
    n = max(len(r) for r in rows)
    w = round(100.0 / n, 2)
    cols = ''.join('<col style="width:%s%%">' % w for _ in range(n))
    def cells(r, tag):
        r = r + [''] * (n - len(r))
        return ''.join('<%s>%s</%s>' % (tag, inline(c.strip()), tag) for c in r)
    return ('<div class="tbl"><table><colgroup>%s</colgroup><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (cols, cells(header, 'th'), ''.join('<tr>%s</tr>' % cells(r, 'td') for r in body)))

def split_row(line):
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c for c in s.split('|')]

# ---------------- 章节解析 ----------------
def parse_fragment(md):
    """注释块内部：只处理段落与无序列表。"""
    out = []
    blocks = re.split(r'\n\s*\n', md.strip())
    for b in blocks:
        lines = [x for x in b.split('\n') if x.strip()]
        if not lines:
            continue
        if all(re.match(r'^\s*-\s+', x) for x in lines):
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % inline(re.sub(r'^\s*-\s+', '', x)) for x in lines))
        else:
            out.append('<p>%s</p>' % inline(' '.join(x.strip() for x in lines)))
    return ''.join(out)


def parse_chapter(md, num, secs, state):
    lines = md.split('\n')
    meta = {}
    i = 0
    while i < len(lines) and (lines[i].startswith(':') or not lines[i].strip()):
        m = re.match(r'^:(\w+)\s+(.*)$', lines[i])
        if m:
            meta[m.group(1)] = m.group(2).strip()
        i += 1
    body = lines[i:]
    title = '未命名'
    out = []
    buf_para = []
    plain = []
    in_raw = False
    cur = {'sec': None}

    def add_plain(txt):
        plain.append(txt)
        if cur['sec'] is not None:
            cur['sec']['text'].append(txt)

    def flush_para():
        if buf_para:
            txt = ' '.join(x.strip() for x in buf_para)
            out.append('<p>%s</p>' % inline(txt))
            add_plain(re.sub(r'[`*$]', '', txt))
            buf_para.clear()

    idx = 0
    while idx < len(body):
        line = body[idx]
        s = line.strip()

        if in_raw:
            out.append(line)
            if '<!--/svg-->' in line:
                in_raw = False
            idx += 1
            continue

        if not s:
            flush_para(); idx += 1; continue

        if s.startswith('# ') and not s.startswith('## '):
            flush_para()
            title = s[2:].strip()
            idx += 1; continue

        if s.startswith('<!--svg-->'):
            flush_para(); in_raw = True; out.append(line); idx += 1; continue

        if s.startswith('$$'):
            flush_para()
            if s.endswith('$$') and len(s) > 4:
                tex = s[2:-2].strip()
                out.append('<div class="math-block" data-tex="%s">%s</div>' % (attr(tex), esc(tex)))
                idx += 1; continue
            chunk = [s[2:]]
            idx += 1
            while idx < len(body) and not body[idx].strip().endswith('$$'):
                chunk.append(body[idx].strip())
                idx += 1
            if idx < len(body):
                chunk.append(body[idx].strip()[:-2])
                idx += 1
            tex = '\n'.join(chunk).strip()
            out.append('<div class="math-block" data-tex="%s">%s</div>' % (attr(tex), esc(tex)))
            continue

        if s.startswith('```'):
            flush_para()
            lang = s[3:].strip() or 'text'
            chunk = []
            idx += 1
            while idx < len(body) and not body[idx].strip().startswith('```'):
                chunk.append(body[idx])
                idx += 1
            idx += 1
            src = '\n'.join(chunk)
            if lang == 'svg':
                out.append('<div class="figure">%s</div>' % src)
            else:
                add_plain(src)
                out.append('<div class="code"><div class="code-head"><span class="lang">%s</span>'
                           '<button class="copy" data-act="copy">复制</button></div>'
                           '<pre><code>%s</code></pre></div>' % (esc(lang), esc(src)))
            continue

        if s.startswith(':::'):
            flush_para()
            kind = s[3:].strip() or 'note'
            head = kind.split()
            k = head[0] if head else 'note'
            lbl = ' '.join(head[1:]) if len(head) > 1 else {'note': '要点', 'warn': '常见坑', 'eng': '工程视角'}.get(k, k)
            chunk = []
            idx += 1
            while idx < len(body) and body[idx].strip() != ':::':
                chunk.append(body[idx])
                idx += 1
            idx += 1
            inner = parse_fragment('\n'.join(chunk))
            out.append('<div class="note %s"><span class="lbl">%s</span>%s</div>' % (k, esc(lbl), inner))
            continue

        if s.startswith('@widget'):
            flush_para()
            parts = s.split(None, 1)
            name = parts[1].strip() if len(parts) > 1 else 'gradient'
            t, hint, body_html = WIDGET_DEF.get(name, WIDGET_DEF['gradient'])
            out.append('<div class="widget" data-widget="%s"><div class="widget-head">'
                       '<span class="w-title">%s</span><span class="w-hint">%s</span></div>'
                       '<div class="widget-body">%s</div></div>' % (name, esc(t), esc(hint), body_html))
            idx += 1; continue

        if s.startswith('## '):
            flush_para()
            state['sec'] += 1
            t2 = s[3:].strip()
            sid = 'ch%d-s%d' % (num, state['sec'])
            out.append('<h3 id="%s"><span class="sn">%d.%d</span>%s</h3>' % (sid, num, state['sec'], inline(t2)))
            rec = {'id': sid, 'title': '%d.%d %s' % (num, state['sec'], t2), 'text': [t2]}
            secs.append(rec)
            cur['sec'] = rec
            add_plain(t2)
            idx += 1; continue

        if s.startswith('### '):
            flush_para()
            t3 = s[4:].strip()
            out.append('<h4>%s</h4>' % inline(t3))
            add_plain(t3)
            idx += 1; continue

        if s.startswith('|'):
            flush_para()
            rows = []
            while idx < len(body) and body[idx].strip().startswith('|'):
                rows.append(split_row(body[idx]))
                idx += 1
            for r in rows:
                for cell in r:
                    if cell.strip():
                        add_plain(re.sub(r'[`*$]', '', cell))
            if len(rows) >= 2 and re.match(r'^[-: ]+$', rows[1][0].replace('|', '').strip() or '-'):
                out.append(render_table(rows))
            else:
                out.append(render_table([rows[0], ['---'] * len(rows[0])] + rows[1:]))
            continue

        m = re.match(r'^(\s*)-\s+(.*)$', line)
        if m:
            flush_para()
            items = []
            base_indent = len(m.group(1))
            while idx < len(body):
                cur_l = body[idx]
                mm = re.match(r'^(\s*)-\s+(.*)$', cur_l)
                if mm and len(mm.group(1)) <= base_indent + 2:
                    items.append([len(mm.group(1)), mm.group(2)])
                else:
                    break
                idx += 1
            html_list = '<ul>'
            depth = 0
            for ind, txt in items:
                if ind > base_indent and depth == 0:
                    html_list += '<ul>'
                    depth = 1
                elif ind <= base_indent and depth == 1:
                    html_list += '</ul>'
                    depth = 0
                html_list += '<li>%s</li>' % inline(txt)
                add_plain(txt)
            if depth == 1:
                html_list += '</ul>'
            html_list += '</ul>'
            out.append(html_list)
            continue

        if re.match(r'^\d+\.\s+', s):
            flush_para()
            items = []
            while idx < len(body):
                mm = re.match(r'^\s*(\d+)\.\s+(.*)$', body[idx])
                if not mm:
                    break
                items.append(mm.group(2))
                add_plain(mm.group(2))
                idx += 1
            out.append('<ol>%s</ol>' % ''.join('<li>%s</li>' % inline(x) for x in items))
            continue

        if s.startswith('> '):
            flush_para()
            chunk = []
            while idx < len(body) and body[idx].strip().startswith('>'):
                chunk.append(body[idx].strip().lstrip('>').strip())
                idx += 1
            out.append('<blockquote>%s</blockquote>' % inline(' '.join(chunk)))
            continue

        if s in ('---', '***'):
            flush_para(); out.append('<hr>'); idx += 1; continue

        if s.startswith('<'):
            flush_para(); out.append(raw_math(line)); idx += 1; continue

        buf_para.append(line)
        idx += 1

    flush_para()
    return {'title': title, 'meta': meta, 'body': '\n'.join(out), 'plain': ' '.join(plain)}

# ---------------- 组装 ----------------
VOLS = {
    'vol1': dict(
        file='AI原理深读-从数学到模型.html',
        series='AI 教程 · 卷一',
        title='AI 原理深读：<br>从数学到模型的推导路线',
        hero='gradient',
        accent='#9C3B2E', accent_deep='#742A20', accent_wash='#F1E4E0',
        lede='给已经学过微积分、线性代数、离散数学与信号与系统，但没真正推过一遍的工程师。'
             '这一卷不回避公式：从内积与概率写到反向传播、注意力和扩散模型的似然，每一步都交代“为什么长这样”。',
        kicker='卷一 / 数学原理主线',
        scope='线性代数 · 概率与信息 · 最优化 · 传统学习 · 深度网络 · 生成模型 · 强化学习',
        tools='可交互：梯度下降 · Softmax 温度 · 卷积滑窗 · 注意力 · 过拟合曲线',
    ),
    'vol2': dict(
        file='AI知识全景-从概念到落地.html',
        series='AI 教程 · 卷二',
        title='AI 知识全景：<br>从概念到工程落地的一条主线',
        hero='map',
        accent='#1F4D3F', accent_deep='#153A2F', accent_wash='#E2EBE5',
        lede='把散落在论文、课程和博客里的名词接成一张能走通的地图：每个概念先回答“它解决什么问题”，'
             '再交代它的代价与边界，最后落到工程上怎么做、怎么评、怎么不翻车。',
        kicker='卷二 / 均衡全景',
        scope='方法论 · 经典模型 · 数据 · 视觉 · NLP · 大模型 · 生成 · 强化 · 部署 · 安全',
        tools='可交互：过拟合曲线 · Softmax · 卷积 · 梯度下降 · KV 显存',
    ),
    'vol3': dict(
        file='大模型与工程实践-从Token到Agent.html',
        series='AI 教程 · 卷三',
        title='大模型工程实践：<br>从 Token 到 Agent 的完整链路',
        hero='stream',
        accent='#1B4A6B', accent_deep='#123A55', accent_wash='#E1ECF2',
        lede='写给要把模型跑起来、还要跑得起的人。预训练与显存的账、微调与对齐的取舍、推理服务的延迟预算、'
             'RAG 与 Agent 的工程结构，以及 C++ 侧到底能优化什么。',
        kicker='卷三 / 大模型与工程实践',
        scope='Transformer · 分词 · 预训练 · 微调 · 对齐 · 推理 · 量化 · RAG · Agent · 评估 · C++ 部署',
        tools='可交互：注意力 · Softmax 采样 · KV cache 账本 · 梯度下降',
    ),
}

def build(vol):
    cfg = VOLS[vol]
    cdir = os.path.join(CONTENT, vol)
    files = sorted(f for f in os.listdir(cdir) if f.endswith('.md'))
    chapters = []
    all_plain = []
    total_sections = []
    for n, f in enumerate(files, start=1):
        with open(os.path.join(cdir, f), encoding='utf-8') as fh:
            md = fh.read()
        secs = []
        ch = parse_chapter(md, n, secs, {'sec': 0})
        ch['num'] = n
        ch['secs'] = secs
        chapters.append(ch)
        all_plain.append(ch['plain'])
        total_sections.extend(secs)

    # 目录
    toc = []
    for ch in chapters:
        sub = ''.join('<button class="sub-link" data-target="%s">%s</button>' % (s['id'], esc(s['title'])) for s in ch['secs'])
        toc.append('<div class="toc-group"><button class="ch-link" data-target="ch%d"><span class="n">%02d</span><span>%s</span></button>'
                   '<div class="sub-list">%s</div></div>' % (ch['num'], ch['num'], esc(ch['title']), sub))

    # 正文
    sec_html = []
    for ch in chapters:
        words = len(re.sub(r'\s', '', ch['plain']))
        mins = max(2, round(words / 380))
        sec_html.append('''
<section class="chapter" id="ch%(num)d">
  <div class="ch-head">
    <span class="ch-num">CHAPTER %(num)02d</span>
    <h2>%(title)s</h2>
    <p class="ch-abs">%(abs)s</p>
    <div class="ch-stats">%(tag)s　·　约 %(words)d 字　·　%(mins)d 分钟</div>
  </div>
%(body)s
  <div class="ch-end"><span>%(num)02d / %(total)02d</span><button data-act="top">回到顶部 ↑</button></div>
</section>''' % dict(num=ch['num'], title=ch['title'], abs=ch['meta'].get('abs', ''),
                     tag=ch['meta'].get('tag', ''), words=words, mins=mins,
                     body=ch['body'], total=len(chapters)))

    # 检索索引
    index = []
    for ch in chapters:
        index.append({'id': 'ch%d' % ch['num'], 'h': ch['title'], 'k': 'c', 's': '', 't': ch['plain'][:1200]})
        for s in ch['secs']:
            index.append({'id': s['id'], 'h': s['title'], 'k': 's', 's': ch['title'],
                          't': (' '.join(s['text']))[:900]})

    total_words = sum(len(re.sub(r'\s', '', x)) for x in all_plain)
    read_min = round(total_words / 380)

    icon_svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
                "<rect width='32' height='32' fill='%s'/>"
                "<path d='M7 24L16 8l9 16M11 20h10' stroke='%s' stroke-width='2' fill='none'/></svg>"
                % (urllib.parse.quote(cfg['accent_deep'], safe=''), urllib.parse.quote('#F2F3EF', safe='')))
    icon = 'data:image/svg+xml,' + icon_svg.replace('#', '%23')

    cover_meta = ''.join('<span>%s</span>' % x for x in [
        '章节 <b>%d</b>' % len(chapters),
        '正文 <b>%s</b> 字' % format(total_words, ','),
        '通读 <b>%d</b> 分钟' % read_min,
        cfg['tools'],
    ])

    html_doc = '''<!doctype html>
<html lang="zh-CN" data-theme="light" data-fs="2">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{doctitle}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{icon}">
<link rel="stylesheet" href="{katex_css}">
<style>{css}</style>
</head>
<body>
<div class="progressbar" id="progressbar"></div>
<div class="shell">
<aside class="rail" id="rail">
  <div class="rail-head">
    <p class="series">{series}</p>
    <p class="rail-title">{rail_title}</p>
    <p class="rail-sub">{scope}</p>
  </div>
  <div class="rail-search">
    <div class="search-wrap">
      <input id="q" type="search" autocomplete="off" placeholder="搜索章节、概念、关键词…">
      <div class="search-hint">共 {nsec} 个小节 · 回车跳到首条</div>
      <div class="search-panel" id="searchPanel"></div>
    </div>
  </div>
  <nav class="toc">{toc}</nav>
  <div class="rail-foot"><div class="meter"><i></i></div><span class="pct" id="pct">0%</span></div>
</aside>
<div class="rail-scrim" data-act="railstop"></div>
<main class="doc">
  <header class="cover">
    <canvas id="heroCanvas" data-scene="{scene}"></canvas>
    <div class="cover-inner">
      <p class="cover-kicker">{kicker}</p>
      <h1>{title}</h1>
      <p class="cover-lede">{lede}</p>
      <div class="cover-meta">{meta}</div>
    </div>
  </header>
  <div class="article-wrap">
    <article>
{chapters}
    </article>
  </div>
  <footer class="end">
    <p class="series-note"><strong>{series}</strong>　{scope}</p>
    <p>{note}</p>
  </footer>
</main>
</div>
<button class="rail-toggle" data-act="rail">目录</button>
<div class="hud">
  <button data-act="font" title="切换字号">Aa</button>
  <button data-act="theme" title="切换明暗">深色</button>
  <button data-act="top" title="回到顶部">↑</button>
</div>
<script>window.__SEARCH__ = {search};</script>
<script src="{katex_js}"></script>
<script>{js}</script>
<script>{widgets}</script>
<script>window.__initWidgets && window.__initWidgets();</script>
<script>{hero}</script>
<script>{exercise}</script>
</body>
</html>'''

    color_vars = '''
:root{--accent:%s;--accent-deep:%s;--accent-wash:%s}
''' % (cfg['accent'], cfg['accent_deep'], cfg['accent_wash'])

    full_css = color_vars + CSS.replace('#9C3B2E', cfg['accent'])
    # 深色模式下的强调色提亮
    full_css += '''
[data-theme="dark"]{--accent:%s}
''' % cfg['accent']

    note = ('三卷并置：卷一给推导，卷二给地图，卷三给工程。图中的数值与曲线由页面内的脚本即时计算，'
            '用来观察趋势，不作为实验数据引用。公式由 KaTeX 排版，首次打开需要网络加载一次字体资源。')

    out_path = os.path.join(OUT, cfg['file'])
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(html_doc.format(
            doctitle=re.sub(r'<br>', ' ', cfg['title']),
            desc=cfg['lede'][:120],
            icon=icon,
            katex_css=KATEX_CSS,
            katex_js=KATEX_JS,
            css=full_css,
            series=cfg['series'],
            rail_title=re.sub(r'<br>', ' ', cfg['title']),
            scope=cfg['scope'],
            nsec=len(total_sections),
            toc=''.join(toc),
            scene=cfg['hero'],
            kicker=cfg['kicker'],
            title=cfg['title'],
            lede=cfg['lede'],
            meta=cover_meta,
            chapters=''.join(sec_html),
            note=note,
            search=json.dumps(index, ensure_ascii=False),
            js=JS,
            widgets=WIDGETS_JS,
            hero=HERO_JS,
            exercise=EXERCISE_JS,
        ))
    print('[%s] %d 章 / %d 小节 / %s 字 -> %s' % (vol, len(chapters), len(total_sections),
                                                  format(total_words, ','), cfg['file']))

if __name__ == '__main__':
    target = sys.argv[1:] or list(VOLS.keys())
    for v in target:
        build(v)
