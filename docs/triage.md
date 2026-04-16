# Issue Triage and Labels

## Label set

Use these labels for first-pass triage:

- `bug`: incorrect behavior or regression.
- `enhancement`: new capability or behavior improvement.
- `docs`: documentation-only work.
- `infra`: repository, CI, tooling, automation, or release-process work.
- `good first issue`: small, well-scoped tasks suitable for newcomers.
- `help wanted`: maintainers explicitly invite external help.
- `question`: clarification requests that are not actionable bugs/features.

Secondary labels such as `duplicate`, `invalid`, and `wontfix` can be applied during resolution.

## Triage flow

1. Confirm issue quality
   - Ensure the report follows the issue template and includes reproduction/context.
   - Request missing details if needed.

2. Apply a primary label
   - Choose one of: `bug`, `enhancement`, `docs`, `infra`, `question`.

3. Add collaboration labels when useful
   - Add `good first issue` for scoped onboarding tasks.
   - Add `help wanted` when maintainers want external contributors.

4. Route to next action
   - `bug`: reproduce and confirm impact.
   - `enhancement`: align with project scope and architecture.
   - `docs`: identify affected docs under `docs/` and contributor docs.
   - `infra`: identify workflow/tooling ownership and risk.

5. Resolve lifecycle
   - Close as `duplicate`, `invalid`, or `wontfix` when appropriate.
   - Link merged PRs and close completed issues.

## Expectations

- Keep triage lightweight and decisive.
- Use labels consistently; avoid label sprawl.
- Prefer clear, actionable issue states over long unresolved discussions.
