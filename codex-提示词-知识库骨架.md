# 提示词：用 Codex 搭建「Wiki 事实层 + Skill 判断层」知识库骨架

## 使用说明（这一节给你自己看，不用贴给 Codex）

1. 把 `=== 提示词开始 ===` 与 `=== 提示词结束 ===` 之间的内容整段贴给 Codex。
2. 先把提示词顶部的 **3 个变量**填好：`TEMPLATE_SRC` / `KB_ROOT` / `TOPIC`。
3. 建议分两次执行：
   - **第一次**：Phase 0–2（建骨架 + 跑通校验）——快，几分钟。
   - **第二次**：Phase 3–5（填真实内容）——等你把材料放进 `raw/` 之后，把 `TOPIC` 写上再跑。
4. `TOPIC` 留空时，提示词要求 Codex 先停下来问你，不会自己瞎编领域。

---

=== 提示词开始 ===

# 任务：搭建「Wiki 事实层 + Skill 判断层」的双层知识库骨架，并跑通自检

你是一名严谨的工程执行者。请严格按下面的规格建目录、建文件、跑验收，不要自由发挥结构，不要引入额外依赖。

## 变量（先读这里）

```
TEMPLATE_SRC = /Users/kk/学习/test/knowledge-template     # 权威模板源（若不可读，见「附录 A：无源重建规格」）
KB_ROOT      = <填写：你要把知识库建在哪，例如 /Users/kk/学习/test/my-kb>
TOPIC        = <填写：这个知识库的主题，例如「某公司售后政策」>
```

**开工前先做两件事：**

1. 确认 `TEMPLATE_SRC` 是否可读、`tools/check.py` 是否存在。可读 → 以它为准复制；不可读 → 改用「附录 A」从零生成，并在最终报告里明确说明你走了哪条路。
2. 如果 `KB_ROOT` 或 `TOPIC` 仍是空的占位符，**停下来问我**，不要自行猜测目录或领域。

---

## 一、最终要得到什么

一个四层结构的知识库：

```
raw/        不可变原文（只增不改、只增不删）
  │ AOT 编译
wiki/       编译层：结构化条目 + 术语表 + 有效期 + 反向依赖
  │ 蒸馏
skills/     判断层：触发 / 判断框架 / 下钻契约 / 冲突规则
  │ 运行
traces/     证据层：每次调用的引用与结论
  └──────────── 回灌：改 Skill / 补 Wiki ────────────┘
```

**核心铁律：Skill 文件里不得出现任何具体事实**（数字、金额、日期、条款原文）。事实只能放在 `wiki/topics/`。违反这条就等于两套真相，会在后续冲突。

---

## 二、文件清单：目标位置 ← 源位置

全部 12 个文件。**逐个复制到 `KB_ROOT` 下的对应路径**，路径必须完全一致。

| # | 目标路径（相对 `KB_ROOT`） | 源路径（相对 `TEMPLATE_SRC`） | 作用 |
|---|---|---|---|
| 1 | `README.md` | `README.md` | 总说明：四层结构、构建/运行顺序、单一真相表、命名与校验约定 |
| 2 | `raw/README.md` | `raw/README.md` | 原文层规则：只增不改、必须带来源元信息 |
| 3 | `wiki/index.md` | `wiki/index.md` | 编译层入口：分区、高频条目、待办、使用约定 |
| 4 | `wiki/terms.md` | `wiki/terms.md` | 术语表 + 状态词 + ID 命名空间（Skill 与 Wiki 共用） |
| 5 | `wiki/topics/_TEMPLATE.md` | `wiki/topics/_TEMPLATE.md` | **条目模板**：8 字段机器契约 + 锚点 + 证据/例外/争议结构 |
| 6 | `wiki/topics/example-refund-window.md` | `wiki/topics/example-refund-window.md` | 填好的示例条目（见第三节的处置要求） |
| 7 | `skills/_TEMPLATE/SKILL.md` | `skills/_TEMPLATE/SKILL.md` | **判断层模板**：9 节，含下钻契约与冲突规则 |
| 8 | `skills/_TEMPLATE/references/_TEMPLATE.md` | `skills/_TEMPLATE/references/_TEMPLATE.md` | 温知识摘要层模板（比 Wiki 浅、比 Skill 具体） |
| 9 | `skills/example-refund-review/SKILL.md` | `skills/example-refund-review/SKILL.md` | 填好的示例 Skill |
| 10 | `traces/_TEMPLATE.md` | `traces/_TEMPLATE.md` | 调用记录 + **回灌动作**（第三个环） |
| 11 | `evals/cases.md` | `evals/cases.md` | 三组对照评测集（只有 Skill / 只有 Wiki / 结合） |
| 12 | `tools/check.py` | `tools/check.py` | 体检脚本，零依赖，仅用 Python 标准库 |

另外建议创建这些空目录（放一个 `.gitkeep` 占位）：

```
raw/docs/  raw/chats/  raw/media/  raw/code/  raw/external/
```

### 关于示例文件（#6、#9）的处置

它们共用一对稳定的引用关系，**必须成对处理，否则校验会报「单向依赖」**：

- 若你**保留**：原样复制，不要只改其中一个。
- 若你**删除**：两个一起删，并同步清理 `wiki/index.md` 里指向示例条目的那一行表格。
- 若你**改造成真实内容**：先按第三节的三步法准备好真实领域，再成对改名 + 同步更新三处：`wiki/topics/<新id>.md` 的 `ID`、`skills/<新名>/SKILL.md` 的 frontmatter `name` 和引用锚点、以及条目里的「依赖本条的 Skill」。

---

## 三、必须遵守的 6 条硬约束

1. **`raw/` 只增不改**。发现问题不要改原文件，新增修订版。
2. **Skill 里不许有事实**。看到数字/日期/条款原文就移到 `wiki/topics/`，Skill 里只留指针。
3. **引用格式固定**：`` wiki:<相对wiki的路径>#<anchor> ``，例如 `wiki:topics/refund-window#refund-window`。**禁止用标题引用**（标题会改，ID 不会）。
4. **Wiki 条目的 8 字段机器契约，字段名一个字都不能改**，写在文件开头的引用块里：

   ```
   > **TL;DR**：<30–80 字，直接给结论，带关键数字与条件>
   > **ID**：`topics/<id>`
   > **状态**：`active`
   > **负责人**：`@<owner>`
   > **最后核验**：`YYYY-MM-DD`
   > **有效期至**：`YYYY-MM-DD`
   > **口径/版本**：`<适用版本 / 地区 / 政策批次>`
   > **依赖本条的 Skill**：`skills/<name>`
   ```

   `ID` 必须与文件路径一致（`topics/foo.md` ↔ `topics/foo`）；`状态` 只能是 `active` / `draft` / `deprecated`。
5. **锚点规则**：标题后写 `{#kebab-case-id}`；不写则由标题自动生成。
6. **双向依赖必须一致**：Skill 引用了 `topics/X`，那么 `topics/X` 的「依赖本条的 Skill」里必须列出这个 Skill；反之亦然。脚本会双向检查。

---

## 四、执行步骤

**Phase 0 · 预检**
- 读 `TEMPLATE_SRC/README.md` 和 `TEMPLATE_SRC/tools/check.py`，确认理解结构。
- 校验本机 `python3` 可用（`python3 -V`）。
- 确认 `KB_ROOT`、`TOPIC` 已填写；未填 → 停下来问。

**Phase 1 · 建骨架**
- 创建 `KB_ROOT` 及第三节列出的空目录。
- 按第二节表格**逐个复制** 12 个文件，保持相对路径一致。
- 复制完成后，用 `find "$KB_ROOT" -type f | sort` 把结果贴给我，确认路径无误。

**Phase 2 · 跑验收（必做）**
- 执行：`cd "$KB_ROOT" && python3 tools/check.py; echo "EXIT=$?"`
- **必须 `EXIT=0`**，且输出类似：

  ```
  ✓ 全绿：契约完整、指针有效、依赖双向一致。
  结果：0 error / 0 warn
  ```

- 然后做**破坏性自测**，证明脚本真的能抓错（在临时目录里做，不要污染 `KB_ROOT`）：

  ```bash
  TMP="$(mktemp -d)" && cp -r "$KB_ROOT/." "$TMP/" && cd "$TMP"
  python3 - <<'PY'
  import pathlib
  s = pathlib.Path("skills/example-refund-review/SKILL.md")
  s.write_text(s.read_text(encoding="utf-8").replace("#exceptions`", "#nope`"), encoding="utf-8")
  w = pathlib.Path("wiki/topics/example-refund-window.md")
  t = w.read_text(encoding="utf-8")
  t = "\n".join(l for l in t.splitlines() if "**负责人**" not in l)      # 删必填字段
  t = t.replace("`2027-06-30`", "`2026-01-01`")                          # 改成已过期
  t = t.replace("`skills/example-refund-review`", "`无`")                # 断开双向依赖
  w.write_text(t, encoding="utf-8")
  PY
  python3 tools/check.py; echo "EXIT=$?"
  ```

  期望输出 4 个 error（缺字段 / 已过期 / 锚点不存在 / 单向依赖），`EXIT=1`。
  **若这 4 类错误没有全部命中，说明脚本被改坏了或复制不完整，必须修好再继续。** 测完删除临时目录。

**Phase 3 · 轻蒸馏（只出提问框架，不出答案）**
- 等我提供材料或领域说明后再做。
- 填 `wiki/terms.md` 的术语表。
- 把 `skills/<name>/SKILL.md` 的第 1、2 节写成"该问什么 / 什么算好 / 边界在哪"。
- ⚠️ **这一步不要写任何事实，也不要蒸到"思维框架层"**——那等于用未经验证的压缩去决定 Wiki 的分类法，分类法错了要重建全库。

**Phase 4 · Wiki 编译**
- 把 Phase 3 的骨架当作**编译规格**：决定条目粒度、分层、必留的反例、必填字段。
- 在 `wiki/topics/` 下逐条复制 `_TEMPLATE.md` 填写，每条必须带真实的 `raw/` 出处。

**Phase 5 · 重蒸馏 + 收尾**
- 回填 `SKILL.md` 第 6 节的下钻契约：把稳定 ID 和锚点写进去，并写好查询预算。
- 补齐双向依赖登记。
- 再跑一次 `python3 tools/check.py`，必须回到全绿。

---

## 五、禁止事项

- ❌ 不要引入任何第三方 Python 包；`check.py` 只用标准库（目标环境是 Python 3.9）。
- ❌ 不要改 `check.py` 的检查规则来"让报告变绿"。绿必须是因为内容对。
- ❌ 不要把示例的业务内容（退款窗口那套）当成真实知识留下来——要么删，要么按第二节成对改造。
- ❌ 不要在 Phase 3 之前就开始写真实事实条目。
- ❌ 不要跳过 `traces/` 和 `evals/`——它们是回灌环，不是装饰。

## 六、最终请给我

1. `find "$KB_ROOT" -type f | sort` 的完整输出。
2. `python3 tools/check.py` 的完整输出与退出码。
3. 破坏性自测的完整输出（应含 4 个 error）。
4. 一句话说明：你走的是「复制模板」还是「附录 A 从零生成」，以及有没有任何文件与模板不一致。

---

## 附录 A：无源重建规格（仅当 `TEMPLATE_SRC` 不可读时使用）

按第二节的路径创建 12 个文件，内容按下述契约自行撰写（保持 Markdown、中文、简体）：

- **`tools/check.py`**：必须实现 8 项检查——① Wiki 条目 8 个契约字段完整性；② `ID` 与文件路径一致；③ `有效期至` 过期=error、30 天内到期=warn；④ `状态` 取值合法；⑤ Skill 里 `wiki:` 指针的文件与锚点都存在；⑥ 双向依赖一致；⑦ 被引用条目状态为 `deprecated`=error；⑧ frontmatter `name` 与目录名一致=warn。命令行支持 `--root` 与 `--today`，无 error 退出码 0、有 error 退出码 1，路径中含 `_` 或 `.` 开头的段全部跳过。
- **`wiki/topics/_TEMPLATE.md`**：以第二节第 4 条的 8 字段引用块开头，后接 `结论`/`证据与出处`/`适用范围与例外`/`争议与不确定性`/`变更记录` 五节，标题带 `{#anchor}`。
- **`skills/_TEMPLATE/SKILL.md`**：YAML frontmatter 含 `name` 与 `description`（description 要写清何时触发、何时不用）；正文 9 节：① 一句话 ② 何时使用/何时不要使用 ③ 判断框架（表格）④ 执行步骤 ⑤ 好坏标准 ⑥ 边界与例外 ⑦ 下钻契约 ⑧ 冲突规则 ⑨ 输出格式（方案 + open_questions + falsifiers）+ 自检清单。第 6、7、8 节必须原样保留语义，不得省略。
- **`traces/_TEMPLATE.md`**：含任务、使用的 Skill、方案、open_questions、取证表（条目/锚点/读到哪一层）、冲突、结论、**回灌动作（必填，没有写「无」）**、一句话复盘。
- **`evals/cases.md`**：定义三组对照（只有 Skill / 只有 Wiki / 结合）与四个指标（准确率、引用正确率、token 成本、**漏查率**），带一张 6 条的用例表。
- **其余文件**：按第二节「作用」一列自行撰写，保持与上述契约一致。

=== 提示词结束 ===
