#!/usr/bin/env python
"""Convert the paper's generated per-task appendix tables (Sections/tab_task_*.tex, written by
IMU-SSL/analysis/paper_tables/make_task_tables.py) into HTML and inject them into website/index.html
between the <!-- task-tables:start --> and <!-- task-tables:end --> markers.

Usage: python website/tools/make_task_tables_html.py [--paper ~/paper_arxiv]
"""
import argparse, html, os, re, sys

TABLES = [  # (file stem, tab label, panel id)
    ("tab_task_arm_pose_nymeria", "Arm pose", "tt-arm"),
    ("tab_task_full_body_pose_nymeria", "Full-body pose", "tt-body"),
    ("tab_task_odometry_nymeria_local", "Odometry", "tt-odom"),
    ("tab_task_microgesture_openwatch", "Microgesture", "tt-gesture"),
    ("tab_task_language_humanml3d", "IMU\u2013text", "tt-text"),
    ("tab_task_pd_pads", "Parkinson's", "tt-pd"),
    ("tab_task_har", "Activity", "tt-har"),
]
REF_ROWS = ("Random frozen encoder", "Raw input", "Scratch")


def untex(s):
    s = s.strip()
    s = re.sub(r"~?\\citep?\{[^}]*\}", "", s)
    s = s.replace("(Appendix~\\ref{app:tasks})", "(see the paper appendix)")
    s = re.sub(r"\\ref\{[^}]*\}", "", s)
    s = s.replace("$\\rightarrow$", "\u2192").replace("$\\downarrow$", " \u2193").replace("$\\uparrow$", " \u2191")
    s = s.replace("($^\\circ$)", "(\u00b0)").replace("$^\\circ$", "\u00b0")
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = s.replace("\\%", "%").replace("\\&", "&").replace("\\,", "\u2009").replace("--", "\u2013").replace("~", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return html.escape(s, quote=False)


def parse(tex):
    cap = re.search(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", tex, re.S).group(1)
    body = tex[tex.index("\\toprule") + len("\\toprule"): tex.index("\\bottomrule")]
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    rows, groups, header, sep = [], None, None, False
    for l in lines:
        if l.startswith("\\cmidrule") or l == "\\midrule":
            if header is not None:
                sep = True
            continue
        if not l.endswith("\\\\"):
            continue
        cells = [c.strip() for c in l[:-2].split("&")]
        if header is None:
            mc = re.findall(r"\\multicolumn\{(\d+)\}\{c\}\{([^}]*)\}", l)
            if mc and len(mc) + 1 >= len(cells) - 1 and all("multicolumn" in c or c == "" for c in cells):
                groups = [(int(n), untex(t)) for n, t in mc]  # group header row
                continue
            header = [untex(c) for c in cells]
            continue
        m = re.match(r"\\multicolumn\{(\d+)\}\{@\{\}l\}\{(.*)\}$", cells[0])
        if m and len(cells) == 1:
            rows.append({"kind": "section", "text": untex(m.group(2)), "sep": sep}); sep = False
            continue
        rows.append({"kind": "data", "cells": [untex(c) for c in cells], "sep": sep}); sep = False
    return untex(cap), groups, header, rows


def render(stem, label, pid, paper):
    cap, groups, header, rows = parse(open(os.path.join(paper, "Sections", stem + ".tex")).read())
    n = len(header)
    out = ['<div class="lb-wrap" id="%s" role="tabpanel" aria-labelledby="%s-tab" hidden>' % (pid, pid), '<table class="lb">', "<thead>"]
    if groups:
        out.append("<tr><th></th>" + "".join('<th class="grp" colspan="%d">%s</th>' % (k, t) if t else '<th colspan="%d"></th>' % k for k, t in groups) + "</tr>")
    out.append("<tr>" + "".join("<th>%s</th>" % h for h in header) + "</tr>")
    out.append("</thead><tbody>")
    in_ref = False
    for r in rows:
        cls = []
        if r["sep"]:
            cls.append("sep")
        if r["kind"] == "section":
            in_ref = r["text"].startswith("Task-specific")
            out.append('<tr class="section%s"><td colspan="%d"><em>%s</em></td></tr>' % (" sep" if r["sep"] else "", n, r["text"]))
            continue
        name = r["cells"][0]
        if name.startswith("InrtlWrist (Ours)"):
            cls.append("ours")
        if in_ref or name.startswith(REF_ROWS):
            cls.append("ref")
        tds = ["<td>%s</td>" % name] + ["<td>%s</td>" % c for c in r["cells"][1:]]
        out.append('<tr class="%s">%s</tr>' % (" ".join(cls), "".join(tds)))
    out.append("</tbody></table></div>")
    out.append('<p class="lb-note tt-cap" data-for="%s" hidden>%s</p>' % (pid, cap))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--paper", default=os.path.expanduser("~/paper_arxiv"))
    ap.add_argument("--site", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html"))
    a = ap.parse_args()
    tabs = '<div class="tabs tabs-wrap" role="tablist" aria-label="Task">' + "".join(
        '<button class="tab" role="tab" id="%s-tab" aria-controls="%s" aria-selected="%s" type="button">%s</button>' % (pid, pid, "true" if i == 0 else "false", label)
        for i, (_, label, pid) in enumerate(TABLES)) + "</div>"
    panels = "\n".join(render(stem, label, pid, a.paper) for stem, label, pid in TABLES)
    frag = "<!-- task-tables:start (generated by website/tools/make_task_tables_html.py; do not edit by hand) -->\n" + tabs + "\n" + panels + "\n<!-- task-tables:end -->"
    frag = frag.replace('id="tt-arm" role="tabpanel" aria-labelledby="tt-arm-tab" hidden', 'id="tt-arm" role="tabpanel" aria-labelledby="tt-arm-tab"')
    frag = frag.replace('data-for="tt-arm" hidden', 'data-for="tt-arm"')
    s = open(a.site).read()
    new = re.sub(r"<!-- task-tables:start.*?<!-- task-tables:end -->", lambda m: frag, s, flags=re.S)
    assert new != s or frag in s, "markers not found in " + a.site
    open(a.site, "w").write(new)
    print("injected %d tables into %s" % (len(TABLES), a.site))


if __name__ == "__main__":
    main()
