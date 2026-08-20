/-
# TokCommon — shared foundation for tôk-system publications

Reusable definitions and lemmas about the tôk system that more than one
publication builds on. Each publication is its own self-contained Lake project
that `require`s this package by relative path (see AGENTS.md, "Shared
foundation") and then `import TokCommon`.

Kept intentionally minimal until there is genuinely shared material to lift
here from a publication. Add shared content under the `Tok` namespace; prefer
narrow `import Mathlib.…` lines in the modules that need them over importing all
of mathlib here.
-/
import Mathlib.Tactic

namespace Tok

end Tok
