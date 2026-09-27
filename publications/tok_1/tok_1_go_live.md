# Go-live — tôk 1 publication

Checklist before publishing `publications/tok_1`. The tag name and exact scope
are to be decided with the Opératrice (below assumes a tag of the form
`tok-1-YYYY-MM`).

## Write the content (the folder is a scaffold today)

- [ ] Fill `\placeholdertitle` and `\placeholdermonth` in
  `latex_document/tok_1.tex`.
- [ ] Write the abstract, introduction, body and conclusion (replace every
  `\placeholder{...}` block).
- [ ] Replace `figures/tok_1_example.pdf` with the real figures; update
  `figures/gen_figures.py` accordingly, and the figure list in `README.md`.
- [ ] Set the `pdfkeywords` and the visible **Keywords** line to the real terms.
- [ ] Decide whether tôk 1 needs the extra pieces of the stokex environment
  (`python_toy/`, `lean_proofs/`, `reviews/`) and add them if so.

## Checks before the tag

- [ ] Regenerate the figures:
  `./.venv/bin/python publications/tok_1/figures/gen_figures.py`.
- [ ] Recompile the PDF
  (`cd latex_document && latexmk -pdf tok_1.tex`) with no new blocking warning.
- [ ] `grep -n "placeholder\|TO BE FILLED\|Month 2026" latex_document/tok_1.tex`
  returns nothing in the body.
- [ ] Reread the final PDF in full.
- [ ] Confirm the license (CC BY 4.0) and the credit line in `LICENSE`.

## Tag and push

- [ ] Commit the final changes (tex + pdf + figures).
- [ ] `git tag tok-1-YYYY-MM`
- [ ] **Confirmation from Maxime before pushing** (tag + commits) —
  non-negotiable rule of the repo.
- [ ] `git push origin tok-1-YYYY-MM` and `git push origin main`.

## After the push

- [ ] Check that the tag URL resolves on GitHub and the PDF matches the tagged
  version.
- [ ] Record the actual publication date in the project memory.
