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
            if any("\\multicolumn" in c for c in cells):
                # group header row: every cell is either \multicolumn{n}{c}{text} or a plain (span-1) label
                groups = []
                for c in cells:
                    m = re.match(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}$", c)
                    groups.append((int(m.group(1)), untex(m.group(2))) if m else (1, untex(c)))
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
        out.append("<tr>" + "".join('<th class="grp" colspan="%d">%s</th>' % (k, t) if t else '<th colspan="%d"></th>' % k for k, t in groups) + "</tr>")
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


HELD_OUT = [("har_hhar", "HHAR"), ("har_mhealth", "MHEALTH"), ("har_prism", "PRISM"), ("har_userwatch", "TransfHAR")]
POOL_HAR = [("har_wisdm", "WISDM"), ("har_pamap2", "PAMAP2"), ("har_recofit", "RecoFit"), ("har_utd_mhad", "UTD-MHAD"),
            ("har_samosa", "SAMoSA")]
MATCHED = ["mae_5src", "limubert_5src", "simmtm_5src", "focal_5src", "relcon_5src", "sslwear_5src"]
HAR_ROWS = [
    ("Frozen probe", "probe", [("mae_5src", "InrtlWrist (Ours)", "ours"), ("limubert_5src", "LIMU-BERT", ""), ("simmtm_5src", "SimMTM", ""),
        ("focal_5src", "FOCAL", ""), ("relcon_5src", "RelCon", ""), ("sslwear_5src", "SSL-Wearables", ""),
        ("mae_5src_noaltattn", "InrtlWrist, plain attention", ""), ("mae_5src_acconly", "InrtlWrist, accelerometer only", ""),
        ("control_random", "Random frozen encoder", "ref"), ("control_raw", "Raw input, 0 layers", "ref")]),
    ("Fine-tune", "finetune", [("mae_5src", "InrtlWrist (Ours)", "ours"), ("limubert_5src", "LIMU-BERT", ""), ("simmtm_5src", "SimMTM", ""),
        ("focal_5src", "FOCAL", ""), ("relcon_5src", "RelCon", ""), ("sslwear_5src", "SSL-Wearables", ""),
        ("mae_5src_noaltattn", "InrtlWrist, plain attention", ""), ("mae_5src_acconly", "InrtlWrist, accelerometer only", "")]),
    ("From scratch", "scratch", [("scratch", "Same backbone, scratch", "ref")]),
    ("Task-specific systems (not ranked)", "external", [("deepconvlstm", "DeepConvLSTM (Ord\u00f3\u00f1ez &amp; Roggen)", "ref")]),
]


def render_har(results_root, pid="tt-har"):
    """One activity table from bench/results: window macro-F1 on the four held-out sets of the paper and on the six
    datasets of the pretraining pool. Bold = best of the six matched objectives per column within a protocol."""
    import glob, json
    def cell(task, enc, proto):
        for f in sorted(glob.glob(os.path.join(results_root, task, "%s__%s__s*.json" % (enc, proto)))):
            try:
                d = json.load(open(f)); v = (d.get("metrics") or {}).get("macro_f1")
                if v is not None: return float(v) * 100.0
            except Exception: pass
        return None
    cols = HELD_OUT + POOL_HAR
    out = ['<div class="lb-wrap" id="%s" role="tabpanel" aria-labelledby="%s-tab" hidden>' % (pid, pid), '<table class="lb">', "<thead>",
           '<tr><th colspan="1"></th><th class="grp" colspan="%d">Held-out sets (paper)</th><th class="grp" colspan="1"></th><th class="grp" colspan="%d">Pretraining-pool sets</th><th class="grp" colspan="1"></th></tr>' % (len(HELD_OUT), len(POOL_HAR)),
           "<tr><th>Encoder</th>" + "".join("<th>%s<small>macro-F1 &uarr;</small></th>" % lab for _, lab in HELD_OUT) + "<th>Mean<small>4 held-out</small></th>"
           + "".join("<th>%s<small>macro-F1 &uarr;</small></th>" % lab for _, lab in POOL_HAR) + "<th>Mean<small>pool, available</small></th></tr>",
           "</thead><tbody>"]
    n = len(cols) + 3
    for sec, proto, rows in HAR_ROWS:
        out.append('<tr class="section sep"><td colspan="%d"><em>%s</em></td></tr>' % (n, sec))
        table = {enc: [cell(t, enc, proto) for t, _ in cols] for enc, _, _ in rows}
        best = []
        for j in range(len(cols)):
            vals = [table[e][j] for e in MATCHED if e in table and table[e][j] is not None]
            best.append(max(vals) if len(vals) >= 2 else None)
        for enc, label, cls in rows:
            vals = table[enc]
            if all(v is None for v in vals): continue
            held = [v for v in vals[:len(HELD_OUT)] if v is not None]; pool = [v for v in vals[len(HELD_OUT):] if v is not None]
            def td(v, j):
                if v is None: return "<td>&ndash;</td>"
                b = enc in MATCHED and best[j] is not None and abs(v - best[j]) < 0.05
                return '<td class="b">%.1f</td>' % v if b else "<td>%.1f</td>" % v
            held_td = "".join(td(v, j) for j, v in enumerate(vals[:len(HELD_OUT)]))
            pool_td = "".join(td(v, len(HELD_OUT) + j) for j, v in enumerate(vals[len(HELD_OUT):]))
            m_held = "%.1f" % (sum(held) / len(held)) if len(held) == len(HELD_OUT) else ("%.1f<small>%d sets</small>" % (sum(held) / len(held), len(held)) if held else "&ndash;")
            m_pool = "%.1f<small>%d sets</small>" % (sum(pool) / len(pool), len(pool)) if pool else "&ndash;"
            out.append('<tr class="%s"><td>%s</td>%s<td>%s</td>%s<td>%s</td></tr>' % (cls, label, held_td, m_held, pool_td, m_pool))
    out.append("</tbody></table></div>")
    cap = ("Activity recognition, window macro-F1 (%) on each set's subject-disjoint evaluation split (TransfHAR is split in time), "
           "one seed, the benchmark's activity recipe (2.56 s windows, linear probe or full fine-tune). The four held-out sets are the "
           "paper's activity tasks; bold marks the best of the six matched objectives per column within a protocol, ties included. "
           "The five pretraining-pool sets are not evaluation tasks in the paper: they belong to the activity pool InrtlWrist was "
           "pretrained on (unlabeled windows from all participants; UTD-MHAD is in the pool configuration but contributes no windows), "
           "so InrtlWrist's cells there are not leak-free and the five matched objectives were not run on them. Balanced accuracy and "
           "accuracy for every cell are in the released result files.")
    out.append('<p class="lb-note tt-cap" data-for="%s" hidden>%s</p>' % (pid, cap))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--paper", default=os.path.expanduser("~/paper_arxiv"))
    ap.add_argument("--site", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html"))
    a = ap.parse_args()
    ap_results = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "bench", "results")
    all_tabs = [(label, pid) for _, label, pid in TABLES] + [("Activity", "tt-har")]
    tabs = '<div class="tabs tabs-wrap" role="tablist" aria-label="Task">' + "".join(
        '<button class="tab" role="tab" id="%s-tab" aria-controls="%s" aria-selected="%s" type="button">%s</button>' % (pid, pid, "true" if i == 0 else "false", label)
        for i, (label, pid) in enumerate(all_tabs)) + "</div>"
    panels = "\n".join(render(stem, label, pid, a.paper) for stem, label, pid in TABLES) + "\n" + render_har(ap_results)
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
