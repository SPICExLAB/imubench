# IMU-Bench project website

Static site for the paper *IMU-Bench: Benchmarking Wrist IMU Representations Across Kinematic, Semantic and Clinical Tasks*, laid out after the Inertia-1 project page (landing page + paper page).

```
website/
  index.html            landing page: hero, task families, findings, how it works, tasks, leaderboard
  paper/index.html      paper page: title block, abstract, benchmark design, findings with figures/tables, BibTeX
  static/css/site.css   shared stylesheet (light + dark via prefers-color-scheme)
  static/js/site.js     nav, reveal, finding toggles, task cards, leaderboard tabs, hero IMU trace, copy BibTeX
  static/images/        figures rasterised from paper_iclr/Pictures (teaser, radar, transfer heatmaps, decoder capacity, coverage)
```

No build step; open `index.html` in a browser.

## Deploy on GitHub Pages at https://imubench.io/

GitHub Pages serves either the repository root or a `docs/` folder, so either

* copy this folder to a repository of its own (`SPICExLAB/imubench.github.io`, Pages source = root of `main`; a project site, so it serves at `https://spicexlab.github.io/imubench.github.io/` until the custom domain is active), or
* rename it to `docs/` in this repository and set Pages source = `main` / `docs`.

The `CNAME` file in this folder (contents: `imubench.io`) tells GitHub Pages which custom domain to serve. The domain
does not resolve yet (checked 2026-10-08), so after the Pages site exists:

1. At the registrar, add the GitHub Pages apex records for `imubench.io`:
   A `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   (and AAAA `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`),
   plus a CNAME `www` -> `spicexlab.github.io` so `www.imubench.io` redirects to the apex.
2. In the repository settings, Pages -> Custom domain: `imubench.io`, wait for the DNS check, then tick "Enforce HTTPS"
   (the certificate is issued automatically once DNS has propagated).
3. Pages rewrites the `CNAME` file if the domain is set from the UI; keep the one in this folder in sync.

Both pages carry `<link rel="canonical">` and `og:url` pointing at `https://imubench.io/` and `https://imubench.io/paper/`.
All internal links are relative, so the site also works at a `*.github.io` address or from the file system.

## Before the site goes public

* `paper/index.html`: replace the "Authors withheld" lines with the author list and affiliations (template in the HTML comment), fill the BibTeX author field and the acknowledgments.
* Both pages: turn the "arXiv soon" / "PDF soon" spans into links once the preprint is public (search for `class="soon"`).
* Both pages: the Code buttons point at `https://github.com/SPICExLAB/IMU-Bench`; change if the public repository differs.
* Numbers in the leaderboard and findings are copied from the paper tables (`tab_main_results.tex`, `results2.tex`, `transferability.tex`, `ablations.tex`); regenerate from `bench/results` if the tables change.

## Regenerating figures

```
module load ghostscript/9.19
gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r220 -dTextAlphaBits=4 -dGraphicsAlphaBits=4 \
   -sOutputFile=static/images/main_radar.png ../../paper_iclr/Pictures/main_radar.pdf
```
(`teaser.png`, `hero_sunburst.png` and the three `panel_*.png` crops come from `Pictures/ICLR_MAIN-7.pdf`.)
