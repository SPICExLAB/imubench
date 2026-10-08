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

## Deploy on GitHub Pages (free, like yang-ai-lab.github.io/Inertia-1/)

The site lives in its own public repository, `SPICExLAB/imubench`, and GitHub Pages serves it at
**https://spicexlab.github.io/imubench/** (Settings -> Pages -> Source: Deploy from a branch, `main`, `/ (root)`).
No custom domain: the `CNAME` file was removed, and `canonical` / `og:url` point at the github.io address.
All internal links are relative, so the site works at any path.

The repository name is the last path segment. `IMU-Bench` is taken by the (private) code repository; once that
repository is public, the site can move into its `docs/` folder (Pages source = `main` / `docs`) and the address becomes
`https://spicexlab.github.io/IMU-Bench/`, which is what the Inertia-1 page does with its code repository.

Workflow: edit this folder in IMU-SSL, then copy it to the site clone and push:

```
rsync -a --delete --exclude .git /gpfs/home/vbc1591/IMU-SSL/website/ ~/imubench-site/
cd ~/imubench-site && git add -A && git commit -m "Update site" && git push
```

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
