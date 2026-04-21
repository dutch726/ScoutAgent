#!/usr/bin/env python3
"""
Scout Advancement Plan — Markdown to styled HTML converter
Usage: python3 generate_report.py <input.md> [output.html]

Layout order: Achievements → Requirements → Gantt → Monthly Grid → Weekly Grid → Merit Badges → Notes
"""

import re, sys
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

CSS = """
  :root {
    --green:  #1A4D2E;
    --green2: #2E6B42;
    --red:    #C8102E;
    --tan:    #C8A96E;
    --tan2:   #E8D9B8;
    --light:  #F5EFE3;
    --border: #DDD0B8;
    --text:   #1C2B1A;
    --muted:  #6B7A62;
    --white:  #FFFFFF;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    font-size: 14px;
    line-height: 1.55;
    color: var(--text);
    background: var(--light);
  }

  /* ── Page wrapper ── */
  .page { max-width: 960px; margin: 0 auto; background: white; box-shadow: 0 2px 24px rgba(0,0,0,.10); }

  /* ── Banner ── */
  .banner {
    background: var(--green);
    color: white;
    padding: 28px 44px 24px;
    border-bottom: 5px solid var(--tan);
  }
  .banner h1 {
    font-size: 22px; font-weight: 700; letter-spacing: .4px;
    margin-bottom: 12px; color: white;
  }
  .meta-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px,1fr)); gap: 4px 20px; }
  .meta-item { font-size: 12.5px; color: rgba(255,255,255,.85); text-wrap: balance; }
  .meta-item strong { color: var(--tan); font-weight: 600; }

  /* ── Content ── */
  .content { padding: 28px 44px 52px; }

  /* ── Section wrapper ── */
  .section { margin-bottom: 36px; }
  .section-title {
    font-size: 17px; font-weight: 700; color: var(--green);
    border-bottom: 2px solid var(--tan);
    padding-bottom: 6px; margin-bottom: 16px;
  }

  /* ── Headings inside sections ── */
  h1,h2,h3,h4 { font-weight: 700; color: var(--green); margin: 18px 0 8px; text-wrap: balance; }
  h2 { font-size: 17px; border-bottom: 2px solid var(--tan); padding-bottom: 6px; margin-top: 28px; }
  h3 { font-size: 14.5px; }
  h4 { font-size: 13px; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); }
  hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
  p  { margin: 8px 0; text-wrap: pretty; }

  /* ── Status spans ── */
  .st-complete   { color: #1a7f3c; }
  .st-progress   { color: #b06000; }
  .st-notstarted { color: var(--muted); }
  .st-time       { color: #1a5fa8; }

  /* ── Tables ── */
  table { width: 100%; border-collapse: collapse; margin: 12px 0 16px; font-size: 12.5px; }
  thead th {
    background: var(--green); color: white;
    text-align: left; padding: 7px 10px;
    font-size: 11px; text-transform: uppercase; letter-spacing: .4px;
  }
  tbody tr:nth-child(even) { background: var(--light); }
  td { padding: 6px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
  td:first-child { font-weight: 500; }

  /* ── Lists ── */
  ul,ol { margin: 6px 0 6px 20px; }
  li    { margin: 3px 0; font-size: 13px; text-wrap: pretty; }
  li.checkbox-item { list-style: none; margin-left: -20px; display: flex; gap: 6px; align-items: baseline; }
  .checkbox { flex-shrink: 0; color: var(--muted); }
  li.checkbox-item.checked .checkbox { color: #1a7f3c; }
  li.checkbox-item.checked { color: var(--muted); text-decoration: line-through; }

  code { background: var(--light); border: 1px solid var(--border); border-radius: 3px; padding: 1px 4px; font-size: 12px; }
  strong { font-weight: 600; }

  /* ── GANTT ── */
  .gantt { margin: 8px 0 20px; overflow-x: auto; }
  .gantt-months {
    display: flex; margin-left: 38%; margin-bottom: 4px;
  }
  .gantt-month-label {
    flex: 1; font-size: 11px; font-weight: 600;
    color: var(--muted); text-align: center;
    text-transform: uppercase; letter-spacing: .3px;
  }
  .gantt-row { display: flex; align-items: center; margin: 3px 0; min-height: 26px; }
  .gantt-label {
    width: 38%; padding-right: 12px; font-size: 12px;
    color: var(--text); line-height: 1.3; flex-shrink: 0;
    overflow: hidden; text-overflow: ellipsis;
  }
  .gantt-track { flex: 1; position: relative; background: var(--light); height: 22px; border-radius: 4px; border: 1px solid var(--border); }
  .gantt-bar {
    position: absolute; top: 2px; height: 18px;
    border-radius: 3px; display: flex; align-items: center;
    padding: 0 6px; font-size: 10px; font-weight: 600;
    color: white; white-space: nowrap; overflow: hidden;
    min-width: 4px;
  }
  .gantt-dividers { display: flex; margin-left: 38%; }
  .gantt-divider  { flex: 1; border-left: 1px dashed var(--border); height: 100%; }

  /* ── Monthly grid ── */
  .month-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 4px 0 8px; }
  .month-card {
    border: 1px solid var(--border); border-radius: 8px;
    overflow: hidden; font-size: 12.5px; break-inside: avoid;
  }
  .month-card-header {
    background: var(--green); color: white;
    padding: 8px 12px; display: flex; justify-content: space-between; align-items: baseline;
  }
  .month-card-header .month-name { font-weight: 700; font-size: 13px; }
  .month-card-header .month-weeks { font-size: 11px; opacity: .8; }
  .month-card-theme {
    background: var(--tan2); color: var(--green);
    font-size: 11px; font-style: italic; padding: 4px 12px;
    border-bottom: 1px solid var(--border);
    text-wrap: balance;
  }
  .month-card-body { padding: 10px 12px; }
  .month-card-body h3 { display: none; }
  .month-card-body h4 { font-size: 10.5px; margin: 8px 0 3px; color: var(--muted); }
  .month-card-body p  { font-size: 12.5px; margin: 4px 0; }
  .month-card-body ul, .month-card-body ol { margin-left: 16px; }
  .month-card-body li { font-size: 12px; margin: 2px 0; }
  .month-card-body li.checkbox-item { margin-left: -16px; }
  .month-card-body table { font-size: 11px; }
  .month-card-body thead th { padding: 4px 8px; }
  .month-card-body td { padding: 4px 8px; }
  .leader-note { background: var(--light); border-top: 1px solid var(--border); padding: 8px 12px; font-size: 11px; color: var(--muted); }
  .timer-block { background: #EFF6F2; border-top: 1px solid var(--border); padding: 6px 12px; font-size: 11px; color: var(--green2); }

  /* ── Weekly grid ── */
  .week-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 4px 0 8px; }
  .week-card {
    border: 1px solid var(--border); border-radius: 8px;
    overflow: hidden; font-size: 12.5px; break-inside: avoid;
  }
  .week-card-header {
    background: var(--green2); color: white;
    padding: 7px 12px; display: flex; justify-content: space-between; align-items: baseline;
  }
  .week-card-header .week-num { font-weight: 700; font-size: 13px; }
  .week-card-header .week-dates { font-size: 11px; opacity: .8; }
  .week-card-theme { background: var(--tan2); color: var(--green); font-size: 11px; font-style: italic; padding: 4px 12px; border-bottom: 1px solid var(--border); text-wrap: balance; }
  .week-card-body { padding: 10px 12px; }
  .week-card-body h3 { display: none; }
  .week-card-body h4 { font-size: 10.5px; margin: 7px 0 3px; color: var(--muted); }
  .week-card-body p  { font-size: 12px; margin: 3px 0; }
  .week-card-body ul, .week-card-body ol { margin-left: 16px; }
  .week-card-body li { font-size: 12px; margin: 2px 0; }
  .week-card-body li.checkbox-item { margin-left: -16px; }
  .week-focus { background: #EFF6F2; border-top: 1px solid var(--border); padding: 6px 12px; font-size: 11.5px; color: var(--green2); font-style: italic; }

  /* ── Action items ── */
  .action-box {
    background: var(--green); color: white; border-radius: 8px;
    padding: 18px 22px; margin: 4px 0;
  }
  .action-box h3 { color: var(--tan); font-size: 13px; margin: 12px 0 4px; }
  .action-box h3:first-child { margin-top: 0; }
  .action-box li { font-size: 13px; color: rgba(255,255,255,.9); margin: 4px 0; }
  .action-box li.checkbox-item .checkbox { color: var(--tan); }
  .action-box p  { font-size: 13px; color: rgba(255,255,255,.9); }

  /* ── Merit badge requirement groups (weekly/monthly cards) ── */
  .mb-group { margin: 6px 0 4px; }
  .mb-group-name {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .6px; color: var(--green2);
    margin: 7px 0 1px; padding: 2px 0;
    border-bottom: 1px dotted var(--border);
  }
  .mb-group ul { margin-left: 16px; }
  .mb-req { font-weight: 600; color: var(--muted); font-size: 11px; margin-right: 3px; }

  /* ── Notes ── */
  .notes-box { background: var(--light); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; margin: 4px 0; }
  .notes-box li { font-size: 13px; margin: 4px 0; }

  /* ── Footer ── */
  .footer {
    background: var(--green); color: rgba(255,255,255,.5);
    font-size: 11.5px; text-align: center; padding: 12px;
    border-top: 3px solid var(--tan);
  }

  /* ── Print ── */
  @media print {
    body { background: white; font-size: 11px; }
    .page { box-shadow: none; max-width: 100%; }
    .banner, thead th, .month-card-header, .week-card-header, .action-box, .footer {
      -webkit-print-color-adjust: exact; print-color-adjust: exact;
    }
    .month-grid, .week-grid { grid-template-columns: 1fr 1fr; }
    .month-card, .week-card { break-inside: avoid; }
    h2 { page-break-after: avoid; }
    p, li { widows: 3; orphans: 3; }
  }
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MONTH_NAMES = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

BAR_COLOURS = ['#1A4D2E','#2E6B42','#C8102E','#7A5C1E','#1a5fa8','#6B3A2E']

# Matches "BadgeName Req#: description" — used to group requirements by badge in cards
# Handles "Communication 4:", "Citizenship in Community 7a–7c:", "SC 7a:", "FC 9d:", etc.
_MB_PAT = re.compile(r'^(⚡\s+)?([A-Z][A-Za-z ]{0,45}?)\s+(\d[\w.\u2013\-]*):\s+(.+)$')

def _parse_mb(text):
    """Return (badge, req, desc, synergy) if text matches a requirement pattern, else None."""
    if '+' in text[:70]:   # synergy items spanning multiple badges — leave ungrouped
        return None
    m = _MB_PAT.match(text.strip())
    if m:
        return m.group(2).strip(), m.group(3), m.group(4), bool(m.group(1))
    return None

def inline(text):
    for em, cls in [('✅','complete'),('🔄','progress'),('⬜','notstarted'),('⏱️','time')]:
        text = text.replace(em, f'<span class="st st-{cls}">{em}</span>')
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)
    return text

def is_table_line(l):  return l.strip().startswith('|')
def is_separator(l):   return bool(re.match(r'^\|[\s\-:|]+(\|[\s\-:|]+)*\|?\s*$', l.strip()))
def is_heading(l):     return bool(re.match(r'^#{1,6} ', l))
def is_hr(l):          return l.strip() in ('---','***','___')
def is_ul(l):          return bool(re.match(r'^[-*] ', l))
def is_ol(l):          return bool(re.match(r'^\d+\. ', l))
def is_blank(l):       return l.strip() == ''

def parse_table(lines):
    rows = [l for l in lines if not is_separator(l)]
    if not rows: return ''
    cells = lambda l: [c.strip() for c in l.strip().strip('|').split('|')]
    hdr = cells(rows[0])
    body = [cells(r) for r in rows[1:]]
    th = '<tr>' + ''.join(f'<th>{inline(h)}</th>' for h in hdr) + '</tr>'
    tb = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body)
    return f'<table><thead>{th}</thead><tbody>{tb}</tbody></table>'

def parse_list(items, ordered=False, group_badges=False):
    if not group_badges:
        out = []
        for line in items:
            m = re.match(r'^[-*] \[([ x])\] (.*)', line)
            if m:
                checked = m.group(1)=='x'
                cls = 'checked' if checked else ''
                icon = '☑' if checked else '☐'
                out.append(f'<li class="checkbox-item {cls}"><span class="checkbox">{icon}</span>{inline(m.group(2))}</li>')
            elif re.match(r'^[-*] ', line):
                out.append(f'<li>{inline(line[2:])}</li>')
            elif re.match(r'^\d+\. ', line):
                out.append(f'<li>{inline(re.sub(r"^\d+\. ","",line))}</li>')
        tag = 'ol' if ordered else 'ul'
        return f'<{tag}>{"".join(out)}</{tag}>'

    # ── Grouped mode: detect consecutive same-badge items and cluster them ──
    categorized = []
    for line in items:
        m_cb = re.match(r'^[-*] \[([ x])\] (.*)', line)
        m_ul = re.match(r'^[-*] (.*)', line)
        m_ol = re.match(r'^\d+\. (.*)', line)
        if m_cb:
            text = m_cb.group(2)
            mb = _parse_mb(text)
            categorized.append(('mb' if mb else 'checkbox', m_cb.group(1)=='x', text, mb))
        elif m_ul:
            text = m_ul.group(1)
            mb = _parse_mb(text)
            categorized.append(('mb' if mb else 'bullet', False, text, mb))
        elif m_ol:
            categorized.append(('ol', False, m_ol.group(1), None))

    html_parts = []
    pending_li = []

    def flush_pending():
        if pending_li:
            tag = 'ol' if ordered else 'ul'
            html_parts.append(f'<{tag}>{"".join(pending_li)}</{tag}>')
            pending_li.clear()

    i = 0
    while i < len(categorized):
        kind, checked, text, mb = categorized[i]
        if kind == 'mb':
            badge = mb[0]
            # Collect consecutive items for the same badge
            j = i + 1
            while j < len(categorized) and categorized[j][0] == 'mb' and categorized[j][3][0] == badge:
                j += 1
            if j - i >= 2:
                flush_pending()
                group_items = []
                for k in range(i, j):
                    _, c, _, (_, r, d, syn) = categorized[k]
                    icon = '☑' if c else '☐'
                    cls = 'checked' if c else ''
                    syn_mark = '⚡ ' if syn else ''
                    group_items.append(
                        f'<li class="checkbox-item {cls}">'
                        f'<span class="checkbox">{icon}</span>'
                        f'<span class="mb-req">{syn_mark}{r}:</span> {inline(d)}</li>'
                    )
                html_parts.append(
                    f'<div class="mb-group">'
                    f'<div class="mb-group-name">{badge}</div>'
                    f'<ul>{"".join(group_items)}</ul>'
                    f'</div>'
                )
                i = j
            else:
                # Single MB item — render normally
                icon = '☑' if checked else '☐'
                cls = 'checked' if checked else ''
                syn_mark = '⚡ ' if mb[3] else ''
                pending_li.append(
                    f'<li class="checkbox-item {cls}">'
                    f'<span class="checkbox">{icon}</span>'
                    f'{syn_mark}{inline(text)}</li>'
                )
                i += 1
        elif kind in ('checkbox', 'bullet'):
            icon = '☑' if checked else '☐'
            cls = 'checked' if checked else ''
            pending_li.append(
                f'<li class="checkbox-item {cls}">'
                f'<span class="checkbox">{icon}</span>'
                f'{inline(text)}</li>'
            )
            i += 1
        else:
            pending_li.append(f'<li>{inline(text)}</li>')
            i += 1

    flush_pending()
    return ''.join(html_parts)

def convert_md(md_text, group_badges=False):
    lines = md_text.split('\n')
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^(#{1,6}) (.+)', line)
        if m:
            lv = len(m.group(1))
            out.append(f'<h{lv}>{inline(m.group(2))}</h{lv}>')
            i += 1; continue
        if is_hr(line):
            out.append('<hr>'); i += 1; continue
        if is_blank(line):
            i += 1; continue
        if is_table_line(line):
            block = []
            while i < len(lines) and is_table_line(lines[i]):
                block.append(lines[i]); i += 1
            out.append(parse_table(block)); continue
        if is_ul(line) or re.match(r'^[-*] \[', line):
            block = []
            while i < len(lines) and (is_ul(lines[i]) or re.match(r'^[-*] \[', lines[i])):
                block.append(lines[i]); i += 1
            out.append(parse_list(block, group_badges=group_badges)); continue
        if is_ol(line):
            block = []
            while i < len(lines) and is_ol(lines[i]):
                block.append(lines[i]); i += 1
            out.append(parse_list(block, ordered=True)); continue
        # paragraph
        block = []
        while i < len(lines):
            l = lines[i]
            if is_blank(l) or is_heading(l) or is_hr(l) or is_table_line(l) or is_ul(l) or is_ol(l) or re.match(r'^[-*] \[', l):
                break
            block.append(inline(l.rstrip('  ')) + ('<br>' if l.endswith('  ') else ''))
            i += 1
        if block:
            out.append(f'<p>{"".join(block)}</p>')
    return '\n'.join(out)

# ---------------------------------------------------------------------------
# Section splitter / classifier
# ---------------------------------------------------------------------------

def split_h2_sections(md_text):
    """Returns list of (h2_title, content_str)."""
    sections, title, buf = [], None, []
    for line in md_text.split('\n'):
        m = re.match(r'^## (.+)', line)
        if m:
            if title is not None:
                sections.append((title, '\n'.join(buf)))
            title, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    if title:
        sections.append((title, '\n'.join(buf)))
    return sections

def classify(title):
    t = title.upper()
    if re.search(r'ACHIEVEMENT|CELEBRATION', t):         return 'achievements'
    if re.search(r'IN.PROGRESS MERIT|MERIT BADGE DETAIL', t): return 'merit_badges'
    if re.search(r'REQUIREMENT|FULL STATUS', t):         return 'requirements'
    if re.search(r'TIME.SENSITIVE|TIME.BASED|COUNTDOWN|TRACKER', t): return 'countdown'
    if re.search(r'SYNERGY|CROSS.REQUIREMENT', t):       return 'synergy'
    if re.search(r'MONTH', t):                           return 'monthly'
    if re.search(r'WEEK.BY.WEEK|WEEK.*DETAIL', t):       return 'weekly'
    if re.search(r'ACTION ITEM|THIS WEEK', t):           return 'action_items'
    if re.search(r'PACING|NOTES|CLARIF|RESOURCES|ADDITIONAL|FAMILY|COMMITMENT|EXPECTATION', t): return 'notes'
    return 'other'

SECTION_ORDER = ['achievements','requirements','countdown','monthly','weekly','merit_badges','action_items','notes','synergy','other']

# ---------------------------------------------------------------------------
# Gantt renderer
# ---------------------------------------------------------------------------

def parse_month_year(text):
    """Return (year, month 1-12) or None."""
    for i, name in enumerate(MONTH_NAMES):
        m = re.search(rf'\b{name}\b\s*\d*,?\s*(\d{{4}})', text, re.I)
        if m: return (int(m.group(1)), i+1)
    return None

def render_gantt(countdown_content):
    lines = countdown_content.strip().split('\n')
    tbl = [l for l in lines if is_table_line(l) and not is_separator(l)]
    if len(tbl) < 2:
        return f'<div class="section-content">{convert_md(countdown_content)}</div>'

    rows = []
    for row in tbl[1:]:
        cells = [c.strip() for c in row.strip().strip('|').split('|')]
        if len(cells) < 4: continue
        name  = re.sub(r'\*\*|\*', '', cells[0])        # strip bold markers
        start = parse_month_year(cells[2]) if len(cells)>2 else None
        end   = parse_month_year(cells[3]) if len(cells)>3 else None
        rows.append((name, start, end))

    rows = [(n,s,e) for n,s,e in rows if s and e]
    if not rows:
        return f'<div class="section-content">{convert_md(countdown_content)}</div>'

    all_ym = [s for _,s,_ in rows] + [e for _,_,e in rows]
    min_ym = min(all_ym, key=lambda x: x[0]*12+x[1])
    max_ym = max(all_ym, key=lambda x: x[0]*12+x[1])

    def to_f(ym):
        return (ym[0]-min_ym[0])*12 + (ym[1]-min_ym[1])

    total = max(to_f(max_ym)+1, 1)

    # Build month labels
    month_labels = []
    y, mi = min_ym
    while (y,mi) <= (max_ym[0], min(max_ym[1]+1,12)):
        month_labels.append(MONTH_NAMES[mi-1][:3])
        mi += 1
        if mi > 12: mi=1; y+=1
    pct = 100/max(len(month_labels),1)
    month_hdrs = ''.join(f'<div class="gantt-month-label" style="width:{pct:.1f}%">{lbl}</div>' for lbl in month_labels)

    bar_rows = []
    for idx, (name, start, end) in enumerate(rows):
        left  = to_f(start) / total * 100
        width = max((to_f(end)-to_f(start)+1) / total * 100, 3)
        color = BAR_COLOURS[idx % len(BAR_COLOURS)]
        short = name[:40]+('…' if len(name)>40 else '')
        bar_rows.append(
            f'<div class="gantt-row">'
            f'<div class="gantt-label" title="{name}">{short}</div>'
            f'<div class="gantt-track">'
            f'<div class="gantt-bar" style="left:{left:.1f}%;width:{width:.1f}%;background:{color};">'
            f'</div></div></div>'
        )

    lbl_html = ''.join(f'<div class="gantt-month-label" style="width:{pct:.1f}%">{l}</div>' for l in month_labels)
    return (
        f'<div class="gantt">'
        f'<div class="gantt-months" style="margin-left:38%;">{lbl_html}</div>'
        + ''.join(bar_rows) +
        f'</div>'
    )

# ---------------------------------------------------------------------------
# Monthly / Weekly card grids
# ---------------------------------------------------------------------------

def split_h3_blocks(content):
    """Split content into (h3_title, body) pairs at ### boundaries."""
    blocks, title, buf = [], None, []
    for line in content.split('\n'):
        m = re.match(r'^### (.+)', line)
        if m:
            if title is not None:
                blocks.append((title, '\n'.join(buf)))
            title, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    if title:
        blocks.append((title, '\n'.join(buf)))
    return blocks

def _pop_block(content, keyword):
    """Extract and remove a block that starts with a keyword line."""
    lines = content.split('\n')
    result_lines, block_lines = [], []
    in_block = False
    for line in lines:
        if re.search(keyword, line, re.I) and line.strip().startswith('**'):
            in_block = True
            block_lines.append(line)
        elif in_block and line.strip().startswith('**') and not re.search(keyword, line, re.I):
            in_block = False
            result_lines.append(line)
        elif in_block:
            block_lines.append(line)
        else:
            result_lines.append(line)
    return '\n'.join(result_lines).strip(), '\n'.join(block_lines).strip()

def render_month_grid(section_content):
    blocks = split_h3_blocks(section_content)
    if not blocks:
        return f'<div class="section-content">{convert_md(section_content)}</div>'

    cards = []
    for title, body in blocks:
        # Parse month name + week range from title e.g. "APRIL 2026 (Weeks 1–2)"
        m_title = re.match(r'([A-Z]+ \d{4})\s*(\([^)]+\))?', title, re.I)
        month_name = m_title.group(1) if m_title else title
        weeks_range = m_title.group(2).strip('()') if m_title and m_title.group(2) else ''

        # Extract theme
        theme_m = re.search(r'\*\*Theme:\*\*\s*(.+)', body)
        theme = theme_m.group(1).strip() if theme_m else ''

        # Separate leader actions and active timers for a lighter footer
        body2, leader = _pop_block(body, r'Leader Action')
        body3, timers = _pop_block(body2, r'Active Timer')

        # Strip the Theme and Objective lines from main body (already in header)
        body4 = re.sub(r'\*\*Theme:\*\*.*\n?', '', body3)
        body4 = re.sub(r'\*\*Objective:\*\*.*\n?', '', body4).strip()

        main_html   = convert_md(body4, group_badges=True)
        timer_html  = (f'<div class="timer-block">⏱ {convert_md(timers)}</div>' if timers.strip() else '')
        leader_html = (f'<div class="leader-note">👤 {convert_md(leader)}</div>' if leader.strip() else '')

        cards.append(
            f'<div class="month-card">'
            f'<div class="month-card-header"><span class="month-name">{month_name}</span><span class="month-weeks">{weeks_range}</span></div>'
            + (f'<div class="month-card-theme">{inline(theme)}</div>' if theme else '')
            + f'<div class="month-card-body">{main_html}</div>'
            + timer_html + leader_html +
            f'</div>'
        )

    return f'<div class="month-grid">{"".join(cards)}</div>'

def render_week_grid(section_content):
    blocks = split_h3_blocks(section_content)
    if not blocks:
        return f'<div class="section-content">{convert_md(section_content)}</div>'

    cards = []
    for title, body in blocks:
        # Parse "WEEK 1: April 14–20, 2026"
        m_wk = re.match(r'WEEK\s+(\d+)[:\-–]?\s*(.*)', title, re.I)
        week_num   = f'Week {m_wk.group(1)}' if m_wk else title
        week_dates = m_wk.group(2).strip() if m_wk else ''

        # Extract theme from **Theme:** or **Activity Type:**
        theme_m = re.search(r'\*\*(?:Theme|Activity Type):\*\*\s*(.+)', body)
        theme = theme_m.group(1).strip() if theme_m else ''

        # Extract focus line
        focus_m = re.search(r"\*\*This Week(?:'s)? Focus[:\*]*\*?\*?\s*(.+)", body)
        focus = focus_m.group(1).strip() if focus_m else ''

        # Strip heading lines from body
        body2 = re.sub(r'\*\*(?:Theme|Activity Type|Meeting Type|This Week[\'s]*\s+Focus):\*\*.*\n?', '', body).strip()

        cards.append(
            f'<div class="week-card">'
            f'<div class="week-card-header"><span class="week-num">{inline(week_num)}</span><span class="week-dates">{week_dates}</span></div>'
            + (f'<div class="week-card-theme">{inline(theme)}</div>' if theme else '')
            + f'<div class="week-card-body">{convert_md(body2, group_badges=True)}</div>'
            + (f'<div class="week-focus">{inline(focus)}</div>' if focus else '')
            + '</div>'
        )

    return f'<div class="week-grid">{"".join(cards)}</div>'

# ---------------------------------------------------------------------------
# Section renderer
# ---------------------------------------------------------------------------

def render_section(kind, title, content):
    heading = f'<div class="section-title">{inline(title)}</div>'

    if kind == 'countdown':
        body = render_gantt(content)
    elif kind == 'monthly':
        body = render_month_grid(content)
    elif kind == 'weekly':
        body = render_week_grid(content)
    elif kind == 'action_items':
        body = f'<div class="action-box">{convert_md(content)}</div>'
    elif kind in ('notes','family'):
        body = f'<div class="notes-box">{convert_md(content)}</div>'
    else:
        body = f'<div class="section-content">{convert_md(content)}</div>'

    return f'<div class="section">{heading}{body}</div>'

# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def extract_meta(md_text):
    title, meta = '', {}
    for line in md_text.split('\n')[:25]:
        m_h1 = re.match(r'^# (.+)', line)
        if m_h1 and not title:
            title = m_h1.group(1).strip(); continue
        m_kv = re.match(r'^\*\*([^*]+):\*\*\s*(.*)', line)
        if m_kv:
            meta[m_kv.group(1).strip()] = m_kv.group(2).strip()
    return title, meta

META_ORDER = ['Scout Name','Scout','Current Rank','Target Rank','Troop',
              'Intermediate Ranks','Plan Start Date','Projected Completion Date',
              'Projected First Class Completion','Eagle Scout Deadline','Time Remaining']

# ---------------------------------------------------------------------------
# Page builder
# ---------------------------------------------------------------------------

def build_page(title, meta, sections_html, source_file):
    seen = set()
    meta_items = []
    for k in META_ORDER:
        if k in meta:
            meta_items.append((k, meta[k])); seen.add(k)
    for k,v in meta.items():
        if k not in seen:
            meta_items.append((k,v))

    meta_html = ''.join(f'<div class="meta-item"><strong>{k}:</strong> {v}</div>' for k,v in meta_items)
    generated = datetime.now().strftime('%B %d, %Y')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>{CSS}</style>
</head>
<body>
<div class="page">
  <div class="banner">
    <h1>{title}</h1>
    <div class="meta-grid">{meta_html}</div>
  </div>
  <div class="content">
    {"".join(sections_html)}
  </div>
  <div class="footer">
    Generated {generated} from {source_file} &nbsp;·&nbsp; File → Print → Save as PDF
  </div>
</div>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 generate_report.py <input.md> [output.html]')
        sys.exit(1)

    md_path  = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else md_path.with_suffix('.html')

    if not md_path.exists():
        print(f'Error: {md_path} not found'); sys.exit(1)

    md_text = md_path.read_text(encoding='utf-8')
    title, meta = extract_meta(md_text)

    # Bucket H2 sections by type
    buckets = {}
    for sec_title, sec_content in split_h2_sections(md_text):
        kind = classify(sec_title)
        buckets.setdefault(kind, []).append((sec_title, sec_content))

    # Render in desired order
    rendered = []
    for kind in SECTION_ORDER:
        for sec_title, sec_content in buckets.get(kind, []):
            rendered.append(render_section(kind, sec_title, sec_content))

    page = build_page(title, meta, rendered, md_path.name)
    out_path.write_text(page, encoding='utf-8')
    print(f'✓  {out_path}')

if __name__ == '__main__':
    main()
