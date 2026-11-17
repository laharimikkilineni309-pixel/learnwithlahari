#!/usr/bin/env python3
"""Build Pages CMS Markdown into static HTML; standard-library only."""
from pathlib import Path
import html, json, re
from datetime import date
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / 'content' / 'posts'
ARTICLES = ROOT / 'articles'
MANIFEST = ROOT / '.generated-posts.json'
START = '<!-- CMS POSTS START -->'
END = '<!-- CMS POSTS END -->'
CATEGORIES = {'QA','AI','Motherhood','Career Transition','Coding','Interview Prep'}

def esc(value):
    return html.escape(str(value), quote=True)

def parse(path):
    text = path.read_text(encoding='utf-8')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.S)
    if not match:
        raise ValueError(f'{path}: expected YAML front matter between --- lines')
    meta = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if ':' not in line:
            raise ValueError(f'{path}: invalid front matter line {line!r}')
        k,v = line.split(':',1)
        v=v.strip()
        if v.startswith(('"',"'")) and v.endswith(v[0]):
            v=v[1:-1]
        meta[k.strip()] = v
    for k in ('title','slug','category','summary','date'):
        if not meta.get(k): raise ValueError(f'{path}: missing {k}')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',meta['slug']):
        raise ValueError(f'{path}: invalid slug')
    if meta['category'] not in CATEGORIES:
        raise ValueError(f'{path}: unsupported category {meta["category"]}')
    date.fromisoformat(meta['date'])
    if meta.get('published','false').lower() not in ('true','false'):
        raise ValueError(f'{path}: published must be true or false')
    return meta, match.group(2)

def inline(text):
    text = esc(text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',lambda m: f'<a href="{m.group(2)}" rel="noopener noreferrer">{m.group(1)}</a>',text)
    text = re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
    text = re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    return text

def render_md(text):
    result=[]; paragraph=[]; list_open=False; code_open=False
    def flush():
        if paragraph:
            result.append('<p>'+inline(' '.join(paragraph))+'</p>')
            paragraph.clear()
    for line in text.splitlines():
        if line.strip().startswith('```'):
            flush()
            if list_open: result.append('</ul>');list_open=False
            result.append('</code></pre>' if code_open else '<pre><code>')
            code_open=not code_open
            continue
        if code_open:
            result.append(esc(line)+'\n')
            continue
        if not line.strip(): flush();continue
        match=re.match(r'^(#{1,3})\s+(.+)$',line)
        if match:
            flush()
            if list_open:result.append('</ul>');list_open=False
            level=len(match.group(1))+1
            result.append(f'<h{level}>{inline(match.group(2))}</h{level}>')
            continue
        if line.startswith('- '):
            flush()
            if not list_open:result.append('<ul>');list_open=True
            result.append('<li>'+inline(line[2:])+'</li>')
            continue
        if list_open:result.append('</ul>');list_open=False
        paragraph.append(line.strip())
    flush()
    if list_open:result.append('</ul>')
    if code_open:result.append('</code></pre>')
    return '\n'.join(result)

def main():
    template=(ARTICLES/'python-pytest-starter.html').read_text(encoding='utf-8')
    head=template.split('<main>',1)[0]
    footer=template.split('</main>',1)[1]
    old=set(json.loads(MANIFEST.read_text()) if MANIFEST.exists() else [])
    new=set(); entries=[]
    for file in sorted(POSTS.glob('*.md')):
        meta,body=parse(file)
        if meta.get('published','false').lower()!='true':continue
        slug=meta['slug']
        if slug in new:raise ValueError(f'Duplicate slug: {slug}')
        if slug not in old and (ARTICLES/f'{slug}.html').exists():
            raise ValueError(f'Slug conflicts with an existing article: {slug}')
        new.add(slug);entries.append(meta)
        title=meta['title'];summary=meta['summary'];category=meta['category']
        h=re.sub(r'<title>.*?</title>',f'<title>{esc(title)} | Learn With Lahari</title>',head)
        h=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{esc(summary)}">',h)
        h=re.sub(r'<link rel="canonical" href="[^"]*">',f'<link rel="canonical" href="https://learnwithlahari.com/articles/{slug}.html">',h)
        h=re.sub(r'<meta property="og:url" content="[^"]*">',f'<meta property="og:url" content="https://learnwithlahari.com/articles/{slug}.html">',h)
        h=re.sub(r'<meta property="og:title" content="[^"]*">',f'<meta property="og:title" content="{esc(title)}">',h)
        h=re.sub(r'<meta property="og:description" content="[^"]*">',f'<meta property="og:description" content="{esc(summary)}">',h)
        main=f'<main><div class="container"><article class="article-layout"><div class="breadcrumbs"><a href="/">Home</a> / <a href="/explore.html">Explore</a> / {esc(category)}</div><span class="eyebrow">{esc(category)} · {esc(meta["date"])}</span><h1>{esc(title)}</h1><p class="intro">{esc(summary)}</p>{render_md(body)}<p><a class="button secondary" href="/explore.html">← Back to all guides</a></p></article></div></main>'
        (ARTICLES/f'{slug}.html').write_text(h+main+footer,encoding='utf-8')
    for slug in old-new:
        (ARTICLES/f'{slug}.html').unlink(missing_ok=True)
    MANIFEST.write_text(json.dumps(sorted(new),indent=2)+'\n')
    entries.sort(key=lambda x:(x['date'],x['slug']),reverse=True)
    cards=[]
    for meta in entries:
        slug=meta['slug'];category=meta['category']
        cards.append(f'<article class="article-card" data-category="{esc(category)}"><div class="meta"><span class="tag coding">{esc(category)}</span><span>{esc(meta["date"])}</span></div><h3><a href="/articles/{slug}.html">{esc(meta["title"])}</a></h3><p>{esc(meta["summary"])}</p><a class="text-link" href="/articles/{slug}.html">Read guide →</a></article>')
    index=ROOT/'explore.html';s=index.read_text(encoding='utf-8')
    if START not in s:
        s=s.replace('<div class="grid-3" id="article-grid">','<div class="grid-3" id="article-grid">'+START+END)
    s=re.sub(re.escape(START)+r'.*?'+re.escape(END),START+''.join(cards)+END,s,flags=re.S)
    index.write_text(s,encoding='utf-8')
    sitemap=ROOT/'sitemap.xml';xml=sitemap.read_text(encoding='utf-8')
    xml=re.sub(r'<!-- CMS URLS START -->.*?<!-- CMS URLS END -->','',xml,flags=re.S)
    if '<!-- CMS URLS START -->' not in xml:
        xml=xml.replace('</urlset>','<!-- CMS URLS START --><!-- CMS URLS END --></urlset>')
    urls=''.join(f'<url><loc>https://learnwithlahari.com/articles/{slug}.html</loc></url>' for slug in sorted(new))
    xml=xml.replace('<!-- CMS URLS START --><!-- CMS URLS END -->','<!-- CMS URLS START -->'+urls+'<!-- CMS URLS END -->')
    sitemap.write_text(xml,encoding='utf-8')
    print(f'Built {len(entries)} published CMS posts; {len(old-new)} removed')

if __name__=='__main__':main()
