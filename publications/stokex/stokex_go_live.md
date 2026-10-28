# Go-live — $t\^okEx defensive publication

Checklist before actually pushing the tag `stokex-defpub-2026-10` and making the
publication citable as prior art.

## Placeholders to remove

- [X] Request peer review from the board

- [X] `latex_document/stokex_defensive_publication.tex:742-743` — replace the
  `\placeholder{...}` block with the final sentence citing the URL once the tag is
  pushed
  (`https://github.com/smoothop-org/tok-system/tree/stokex-defpub-2026-10/publications/stokex/lean_proofs`).
- [ ] Check that the link to the same tag in the "Defensive publication notice"
  (`latex_document/stokex_defensive_publication.tex:84`) resolves once the tag is in place.
- [X] `grep -n "À COMPLÉTER\|placeholder" latex_document/stokex_defensive_publication.tex` must
  return no `\placeholder{...}` call in the body (the two remaining hits are legitimate:
  the `\placeholder` macro definition at l.51, and the English word "placeholder" in prose at l.416).

## Checks before the tag

- [X] `python3 python_toy/verify_stokex.py` passes (numerical verification of the paper's claims).
- [X] The Lean project (`lean_proofs/`) compiles: `cd lean_proofs && lake build`.
- [X] `lean_proofs/README.md` is cleaned of its "GitHub configuration" section (scaffolding
  instructions, no longer relevant once the repo is in place).
- [X] Recompile the PDF (`cd latex_document && latexmk -pdf stokex_defensive_publication.tex`) and check
  there is no new blocking warning.
- [X] Reread the final PDF in full (not only the recently edited sections).

## Tag and push

- [X] Commit the final changes (tex + pdf).
- [X] `git tag stokex-defpub-2026-10`
- [X] **Confirmation from Maxime before pushing** (tag + commits) — non-negotiable rule of the repo.
- [X] `git push origin stokex-defpub-2026-10` and `git push origin main`.

## After the push

- [X] Check that the tag URL (lean_proofs/ and the repo root) resolves on GitHub. (tag ref `stokex-defpub-2026-10` confirmed on remote, dereferences to `beab2d4`)
- [X] Check that the PDF downloaded from GitHub matches the tagged version. (local `.pdf` verified byte-identical to the tagged commit; no draft drift)

## Before TDCommons publication (irreversible step)

Once submitted and published on TDCommons, the document can no longer be withdrawn or
modified: that is precisely what makes it opposable prior art. Everything must be frozen
and validated before this point.

- [X] The submitted PDF is **exactly** the one from the tag `stokex-defpub-2026-10` (not a
  fresher local version, not a draft) — compare the hash or re-download from GitHub.
- [X] No placeholder, author note, or "to be completed" comment remains in the PDF.
- [X] The PDF passes the CLAUDE.md test: nothing in it we would not be comfortable seeing
  public forever (a dedicated reread, not just the earlier technical review).
- [ ] Submission metadata ready: title, author(s), affiliation, abstract, keywords, date of
  first use/disclosure if applicable — consistent with the PDF.
- [X] License confirmed (CC BY 4.0, already stated in the PDF) and compatible with the
  TDCommons submission terms.
- [X] **Explicit confirmation from Maxime immediately before clicking "Publish/Submit"** on
  TDCommons — an irreversible action, so no automatic submission by Milu.
  *(Submitted 2026-10-27; pending TDCommons moderation — approval + posting typically within one business day, confirmation email to the inventor address.)*
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
