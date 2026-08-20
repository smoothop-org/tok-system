# Go-live — $t\^okEx defensive publication

Checklist before actually pushing the tag `stokex-defpub-2026-08` and making the
publication citable as prior art.

## Placeholders to remove

- [ ] Request peer review from the board

- [ ] `latex_document/stokex_defensive_publication.tex:643-648` — replace the
  `\placeholder{...}` block with the final sentence citing the URL once the tag is
  pushed
  (`https://github.com/smoothop-org/tok-system/tree/stokex-defpub-2026-08/publications/stokex/lean_proofs`).
- [ ] Check that the link to the same tag in the "AI contribution statement"
  (`latex_document/stokex_defensive_publication.tex:83`) resolves once the tag is in place.
- [ ] `grep -n "À COMPLÉTER\|placeholder" latex_document/stokex_defensive_publication.tex` must
  return nothing in the body of the text (only the entries of the notation table,
  which use "placeholder" as a mathematical term, are legitimate).

## Checks before the tag

- [ ] `python3 python_toy/verify_stokex.py` passes (numerical verification of the paper's claims).
- [ ] The Lean project (`lean_proofs/`) compiles: `cd lean_proofs && lake build`.
- [ ] `lean_proofs/README.md` is cleaned of its "GitHub configuration" section (scaffolding
  instructions, no longer relevant once the repo is in place).
- [ ] Recompile the PDF (`cd latex_document && latexmk -pdf stokex_defensive_publication.tex`) and check
  there is no new blocking warning.
- [ ] Reread the final PDF in full (not only the recently edited sections).

## Tag and push

- [ ] Commit the final changes (tex + pdf).
- [ ] `git tag stokex-defpub-2026-08`
- [ ] **Confirmation from Maxime before pushing** (tag + commits) — non-negotiable rule of the repo.
- [ ] `git push origin stokex-defpub-2026-08` and `git push origin main`.

## After the push

- [ ] Check that the tag URL (lean_proofs/ and the repo root) resolves on GitHub.
- [ ] Check that the PDF downloaded from GitHub matches the tagged version.

## Before TDCommons publication (irreversible step)

Once submitted and published on TDCommons, the document can no longer be withdrawn or
modified: that is precisely what makes it opposable prior art. Everything must be frozen
and validated before this point.

- [ ] The submitted PDF is **exactly** the one from the tag `stokex-defpub-2026-08` (not a
  fresher local version, not a draft) — compare the hash or re-download from GitHub.
- [ ] No placeholder, author note, or "to be completed" comment remains in the PDF.
- [ ] The PDF passes the CLAUDE.md test: nothing in it we would not be comfortable seeing
  public forever (a dedicated reread, not just the earlier technical review).
- [ ] Submission metadata ready: title, author(s), affiliation, abstract, keywords, date of
  first use/disclosure if applicable — consistent with the PDF.
- [ ] License confirmed (CC BY 4.0, already stated in the PDF) and compatible with the
  TDCommons submission terms.
- [ ] **Explicit confirmation from Maxime immediately before clicking "Publish/Submit"** on
  TDCommons — an irreversible action, so no automatic submission by Milu.
- [ ] Keep a timestamped copy of the submitted PDF and of the TDCommons confirmation page
  (publication number / DOI if provided) for future annexes and for LinkedIn/investors.

## After publication (LinkedIn + investor mailing list)

- [ ] Retrieve the permanent TDCommons link (and the publication number) once online.
- [ ] Write the LinkedIn post: TDCommons link + tok-system link (tag), tone consistent with the
  rest of Smoothop's public presence — reviewed by Maxime before publication (publicly
  visible, under his name).
- [ ] Write the email to the investor mailing list: same links, framing suited to that
  audience (prior art established, next product step) — reviewed and **explicitly confirmed
  by Maxime before sending** (external email, irreversible once gone).
- [ ] Check the consistency of dates: the LinkedIn post and the email go out only after
  confirmation that TDCommons has indeed published (no dead link).
- [ ] After sending, record the actual publication/announcement date in the project memory
  (useful for future references to "the stokex defensive publication").
