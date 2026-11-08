# 术语表与命名空间

> **这一份是"两边共用"的契约。** Skill 里说的"高风险变更"，Wiki 里必须正好有一个 `高风险变更` 条目——否则 agent 会以为两边在说同一件事，而实际上不是。术语不对齐是 Skill 与 Wiki 结合失败最常见的原因。

## 规则

1. Skill 和 Wiki 里出现的**领域术语、判定词、状态词**，必须先在本文登记。
2. 一个术语只能有一个定义。有歧义就拆成两个（`高风险变更(发布)` / `高风险变更(数据)`）。
3. 术语的**判定标准**放在它的 Wiki 条目里，本文只放一句话定义和指针。
4. 新增术语时，同步检查已有哪些 Skill 会受影响。

## 术语

| 术语 | 一句话定义 | 判定标准（详见条目） | 首次登记 |
|---|---|---|---|
| 示例术语 | 示例定义 | [topics/example-refund-window](topics/example-refund-window.md#refund-window) | 2026-10-12 |

## 状态词（统一取值，不要自造）

| 状态 | 含义 | 使用场景 |
|---|---|---|
| `active` | 当前有效 | Wiki 条目、Skill |
| `draft` | 草稿，未经核验 | Wiki 条目 |
| `deprecated` | 已废弃，不得再被引用 | Wiki 条目 |
| `open` | 待核实 | traces 里的 open_questions |
| `conflict` | 与另一来源冲突，待裁决 | traces / Wiki 争议节 |

## ID 命名空间

| 前缀 | 用途 | 例 |
|---|---|---|
| `topics/` | 主题条目 | `topics/refund-window` |
| `terms/` | 术语条目（术语复杂到需要独立条目时） | `terms/high-risk-change` |
| `skills/` | Skill | `skills/refund-review` |
| `raw/` | 原文 | `raw/docs/policy-2026.md` |
