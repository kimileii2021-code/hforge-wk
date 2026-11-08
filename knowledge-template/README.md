# 知识库模板：Skill（判断层）+ Wiki（事实层）

一套可直接复制的目录骨架，用来落地"**Wiki 做底、Skill 做面**"的知识工程。

核心规则只有一条：**Skill 里不许出现具体事实**（数字、日期、金额、条款原文）。事实进 Wiki，判断留在 Skill。违反这条，迟早会有两套互相冲突的真相。

---

## 快速开始

```bash
cp -r knowledge-template ~/my-kb && cd ~/my-kb
python3 tools/check.py          # 先跑一遍，看示例是绿的
```

然后按这个顺序填：

1. **轻蒸馏（只蒸提问框架）**
   填 `wiki/terms.md` 的术语；把 `skills/<你的skill>/SKILL.md` 的第 1、2 节写成"该问什么 / 什么算好 / 边界在哪"。
   ⚠️ 这一步**不要写答案**，也不要先蒸到"思维框架层"——那等于用未经验证的压缩去决定 Wiki 的分类法，分类法错了要重建全库。

2. **Wiki 编译**
   `wiki/topics/` 下逐条复制 `_TEMPLATE.md`，用第 1 步的骨架当**编译规格**：决定粒度、分层、必留的反例、必填字段。这一步 Wiki 是主角。

3. **重蒸馏**
   Wiki 成型后回头填 SKILL.md 第 6 节的**下钻契约**，把稳定 ID 和锚点写进去。

4. **自检**
   ```bash
   python3 tools/check.py
   ```

---

## 四层结构

```
raw/        不可变原文 ────────────────┐ 永久保留，只增不改
  │ AOT 编译                            │
wiki/       编译层：条目 + 术语 + 有效期 + 反向依赖
  │ 蒸馏                                │
skills/     判断层：触发 / 步骤 / 标准 / 边界 / 下钻契约
  │ 运行                                │
traces/     证据层：每次调用的引用与结论
  └──────────── 回灌 ──────────────────┘ 改 Skill / 补 Wiki
```

- **raw 永不删**：Wiki 是**可再生**的编译产物。发现编错了就重编译，别手改烂条目。
- **Wiki 是编译产物，不是仓库**：真源永远在 `raw/`。
- **traces 是最常被漏掉的第三个环**：没有回灌，两个库都会在三个月内腐化。

---

## 两条顺序，别搞反

| 阶段 | 顺序 |
|---|---|
| **构建** | 轻蒸馏（提问框架）→ Wiki 编译 → 重蒸馏（加指针与锚点） |
| **运行** | Skill 出「方案 + open_questions + falsifiers」→ 按需查 Wiki 取证 → 定论 |
| **回灌** | traces 里的「漏查 / 缺口」→ 改 Skill 或补 Wiki |

运行期还有一条铁律：**Skill 先给方案、再去 Wiki 找支持，是确认偏误**。所以 Skill 必须输出 `open_questions`（待核实清单）和 `falsifiers`（什么会推翻它），让 Wiki 步骤去回答**具体问题**，而不是"再读点资料"。

---

## 单一真相表

| 内容 | 放哪 | 变更成本 |
|---|---|---|
| 数字、日期、金额、条款原文、出处 | `wiki/topics/<id>.md` | 改条目 + 重编译 |
| 怎么判断、怎么权衡、步骤、边界 | `skills/<name>/SKILL.md` | 改一个文件 |
| 中等粒度摘要（比 Wiki 浅、比 Skill 具体） | `skills/<name>/references/` | 改一个文件 |
| 原始材料 | `raw/` | 只增不改 |

---

## 命名与引用约定

- **Wiki 条目 ID**：`topics/<kebab-case>`，必须与文件名一致（`check.py` 会校验）。
- **引用格式**（必须带稳定 ID + 锚点粒度，不要用标题）：
  ```
  依据：`wiki:topics/example-refund-window#refund-window`
  ```
- **锚点**：标题后写 `{#anchor}`；不写则由标题自动生成。
- **模板文件**：路径中含以 `_` 开头的段（如 `_TEMPLATE`）不参与校验。
- **文件名会改、ID 不会改**：所以引用一律用 ID，不要写"《XX 政策》那一节"。

---

## 冲突规则（写进每个 Skill）

- **事实**（数字 / 条款 / 日期）以 **Wiki** 为准。
- **判断**（怎么权衡、怎么选）以 **Skill** 为准。
- **两者冲突时：停下来报告**，贴出两边原文与出处，不要自行裁决。

---

## 自检脚本 `tools/check.py` 查什么

| # | 检查项 | 级别 |
|---|---|---|
| 1 | Wiki 条目必备的 8 个机器契约字段 | error |
| 2 | `ID` 与文件路径是否一致 | error |
| 3 | `有效期至` 已过期 / 30 天内到期 | error / warn |
| 4 | `状态` 是否为合法值 | error |
| 5 | Skill 里的 `wiki:` 指针：文件存在 + 锚点存在 | error |
| 6 | 双向依赖：Wiki 声明「依赖本条的 Skill」↔ Skill 实际引用 | error |
| 7 | 被引用的条目状态为 `deprecated` | error |
| 8 | Skill 的 frontmatter `name` 与目录名一致 | warn |

```bash
python3 tools/check.py                       # 校验当前目录
python3 tools/check.py --root ~/my-kb        # 指定根目录
python3 tools/check.py --today 2026-10-12    # 复现某天的有效期判定
```

退出码 `0` = 无 error；`1` = 有 error。**建议把它挂进 CI 或 git pre-commit**，这是防"指针腐烂"最省事的办法。

---

## 目录一览

```
knowledge-template/
├── README.md                      ← 你正在看的这份
├── raw/README.md                  ← 原文层规则
├── wiki/
│   ├── index.md                   ← 入口：分区 + 高频条目
│   ├── terms.md                   ← 术语表与 ID 命名空间（两边共用）
│   └── topics/
│       ├── _TEMPLATE.md           ← 条目模板（TL;DR 机器契约）
│       └── example-refund-window.md  ← 填好的示例（可用 check.py 验证）
├── skills/
│   ├── _TEMPLATE/
│   │   ├── SKILL.md               ← 判断层模板
│   │   └── references/_TEMPLATE.md
│   └── example-refund-review/SKILL.md  ← 填好的示例
├── traces/_TEMPLATE.md            ← 调用记录 + 回灌动作
├── evals/cases.md                 ← 三组对照回归测试集
└── tools/check.py                 ← 体检脚本
```

---

## 什么时候**不要**用这套模板

如果 Wiki 只有二三十条、问题空间封闭、也不常变，**直接把内容放进 Skill 的 `references/` 就好**，不要引入第二套系统。Wiki 层的收益是长尾覆盖，成本是维护 + 检索开销——只有长尾问题真实存在时才划算。
