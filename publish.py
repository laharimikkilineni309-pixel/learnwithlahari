#!/usr/bin/env python3
"""Publish a Markdown draft into the static site. No third-party packages."""
from pathlib import Path
import re, html, sys
ROOT=Path(__file__).resolve().parent

def inline(s):
    s=html.escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    return s

def markdown(s):
    out=[]; in_list=False; in_code=False; para=[]
    def flush():
        if para: out.append('<p>'+inline(' '.join(para))+'</p>');para.clear()
    for line in s.splitlines():
        if line.startswith('```'):
            flush()
            if in_list:out.append('</ul>');in_list=False
            out.append('</code></pre>' if in_code else '<pre><code>');in_code=not in_code;continue
        if in_code:out.append(html.escape(line)+'\n');continue
        if not line.strip():flush();continue
        if line.startswith('#'):
            flush()
            if in_list:out.append('</ul>');in_list=False
            n=min(len(line)-len(line.lstrip('#')),3)
            out.append(f'<h{n+1}>'+inline(line[n:].strip())+f'</h{n+1}>');continue
        if line.startswith('- '):
            flush()
            if not in_list:out.append('<ul>');in_list=True
            out.append('<li>'+inline(line[2:])+'</li>');continue
        if in_list:out.append('</ul>');in_list=False
        para.append(line.strip())
    flush()
    if in_list:out.append('</ul>')
    if in_code:out.append('</code></pre>')
    return '\n'.join(out)

def publish(file):
    raw=Path(file).read_text(encoding='utf-8'); metadata,sep,body=raw.partition('\n\n')
    if not sep:raise ValueError('Add a blank line after title/category/summary/slug metadata')
    meta=dict(line.split(':',1) for line in metadata.splitlines() if ':' in line)
    meta={k.strip():v.strip() for k,v in meta.items()}
    for k in ('title','category','summary','slug'):
        if not meta.get(k):raise ValueError('Missing '+k)
    slug=meta['slug']
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError('Slug must be lowercase letters, numbers and hyphens')
    target=ROOT/'articles'/f'{slug}.html'
    if target.exists():raise FileExistsError(f'{target} already exists; choose another slug')
    template=(ROOT/'articles'/'python-pytest-starter.html').read_text()
    head=template[:template.index('<main>')]
    foot=template[template.index('</main>')+7:]
    head=re.sub(r'<title>.*?</title>',f'<title>{html.escape(meta["title"])} | Learn With Lahari</title>',head)
    head=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{html.escape(meta["summary"],quote=True)}">',head)
    head=re.sub(r'<link rel="canonical" href="[^"]*">',f'<link rel="canonical" href="https://learnwithlahari.com/articles/{slug}.html">',head)
    head=re.sub(r'<meta property="og:url" content="[^"]*">',f'<meta property="og:url" content="https://learnwithlahari.com/articles/{slug}.html">',head)
    main=f'<main><div class="container"><article class="article-layout"><div class="breadcrumbs"><a href="/">Home</a> / <a href="/explore.html">Explore</a> / {html.escape(meta["category"])}</div><h1>{html.escape(meta["title"])}</h1><p class="intro">{html.escape(meta["summary"])}</p>{markdown(body)}<p><a class="button secondary" href="/explore.html">← Back to all guides</a></p></article></div></main>'
    target.write_text(head+main+foot,encoding='utf-8')
    index=ROOT/'explore.html';s=index.read_text(encoding='utf-8')
    card=f'<article class="article-card" data-category="{html.escape(meta["category"],quote=True)}"><div class="meta"><span class="tag coding">{html.escape(meta["category"])}</span></div><h3><a href="/articles/{slug}.html">{html.escape(meta["title"])}</a></h3><p>{html.escape(meta["summary"])}</p><a class="text-link" href="/articles/{slug}.html">Read guide →</a></article>'
    s=s.replace('<div class="grid-3" id="article-grid">','<div class="grid-3" id="article-grid">'+card)
    if f'data-filter="{html.escape(meta["category"],quote=True)}"' not in s:
        s=s.replace('<div class="filters" role="group" aria-label="Filter articles by topic">',f'<div class="filters" role="group" aria-label="Filter articles by topic"><button class="filter" data-filter="{html.escape(meta["category"],quote=True)}" aria-pressed="false">{html.escape(meta["category"])}</button>')
    index.write_text(s,encoding='utf-8')
    sitemap=ROOT/'sitemap.xml'
    if sitemap.exists():
        xml=sitemap.read_text();xml=xml.replace('</urlset>',f'<url><loc>https://learnwithlahari.com/articles/{slug}.html</loc></url></urlset>');sitemap.write_text(xml)
    print('Published:',target)

if __name__=='__main__':
    if len(sys.argv)!=2:sys.exit('Usage: python3 publish.py content/your-post.md')
    publish(sys.argv[1])
