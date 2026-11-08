#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知识库体检：校验 Wiki 条目的机器契约与 Skill 的引用指针。

校验项：
  1. Wiki 条目的 8 个必填契约字段（TL;DR / ID / 状态 / 负责人 / 最后核验 / 有效期至 / 口径·版本 / 依赖本条的 Skill）
  2. ID 与文件路径是否一致
  3. 有效期：已过期 = error，30 天内到期 = warn
  4. 状态取值是否合法；被引用的条目状态为 deprecated = error
  5. Skill 里的 `wiki:` 指针：文件存在 + 锚点存在
  6. 双向依赖：Wiki 声明的「依赖本条的 Skill」↔ Skill 的实际引用，两边都要一致
  7. Skill frontmatter 的 name 与目录名是否一致

用法：
    python3 tools/check.py
    python3 tools/check.py --root ~/my-kb
    python3 tools/check.py --today 2026-10-12

退出码：0 = 无 error；1 = 有 error。
约定：路径中任何一段以 "_" 或 "." 开头（如 _TEMPLATE）都会被跳过，不参与校验。
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys

META_RE = re.compile(r"^\s*>\s*\*\*(?P<key>[^*]+?)\*\*\s*[：:]\s*(?P<val>.*?)\s*$")
HEAD_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")
ANCHOR_TAIL_RE = re.compile(r"\{#(?P<id>[A-Za-z0-9_\-]+)\}\s*$")
REF_RE = re.compile(
    r"wiki:(?P<path>[A-Za-z0-9_\-/\.]+?)(?:#(?P<anchor>[A-Za-z0-9_\-]+))?"
    r"(?=[`\s\)）,，。;；、]|$)"
)
NAME_RE = re.compile(r"^name:\s*(?P<val>.+?)\s*$", re.M)

REQUIRED_META = [
    "TL;DR",
    "ID",
    "状态",
    "负责人",
    "最后核验",
    "有效期至",
    "口径/版本",
    "依赖本条的 Skill",
]
VALID_STATUS = {"active", "draft", "deprecated"}
NO_DEP_WORDS = {"无", "none", "-", "—", ""}
SLUG_DROP = "`*_[]()（）【】「」《》，。、：:；;！!？?\"'“”‘’"

RED, YEL, GRN, DIM, RST = "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    RED = YEL = GRN = DIM = RST = ""


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warns: list[str] = []
        self.notes: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warns.append(f"{where}: {msg}")

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def is_skipped(path: str, root: str) -> bool:
    rel = os.path.relpath(path, root)
    return any(seg.startswith(("_", ".")) for seg in rel.split(os.sep))


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def slugify(title: str) -> str:
    text = title.strip().lower()
    text = "".join(ch for ch in text if ch not in SLUG_DROP)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def anchors_of(text: str) -> set:
    found = set()
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        if not m:
            continue
        title = m.group("title")
        tail = ANCHOR_TAIL_RE.search(title)
        if tail:
            found.add(tail.group("id"))
            title = ANCHOR_TAIL_RE.sub("", title).strip()
        slug = slugify(title)
        if slug:
            found.add(slug)
    return found


def walk_md(base: str, root: str) -> list:
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(("_", ".")))
        for name in sorted(filenames):
            if not name.endswith(".md") or name.startswith(("_", ".")):
                continue
            path = os.path.join(dirpath, name)
            if not is_skipped(path, root):
                out.append(path)
    return sorted(out)


def parse_meta(text: str) -> dict:
    meta = {}
    for line in text.splitlines():
        m = META_RE.match(line)
        if m:
            meta.setdefault(m.group("key").strip(), m.group("val").strip().strip("`").strip())
    return meta


def parse_date(value: str):
    value = value.strip().strip("`").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", value)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def dep_names(value: str) -> list:
    value = value.replace("`", "").strip()
    if value.lower() in NO_DEP_WORDS:
        return []
    parts = re.split(r"[,，、;；\s]+", value)
    return [p for p in (x.strip() for x in parts) if p and p.lower() not in NO_DEP_WORDS]


def skill_key_from_dep(dep: str) -> str:
    return dep[7:] if dep.startswith("skills/") else dep


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="知识库体检（Wiki 契约 + Skill 指针）")
    ap.add_argument("--root", default=os.path.dirname(here), help="知识库根目录（默认脚本的上一级）")
    ap.add_argument("--today", default=None, help="把今天当作某一天，用于复现有效期判定（YYYY-MM-DD）")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    rep = Report()

    if not os.path.isdir(os.path.join(root, "wiki")):
        print(f"{RED}找不到 wiki/ 目录：{root}{RST}")
        return 1

    # ---------- 收集 Wiki 文件与锚点 ----------
    wiki_root = os.path.join(root, "wiki")
    wiki_files = {}
    for path in walk_md(wiki_root, root):
        key = os.path.relpath(path, wiki_root)[: -len(".md")].replace(os.sep, "/")
        text = read_text(path)
        wiki_files[key] = {"path": path, "text": text, "anchors": anchors_of(text), "meta": {}, "status": None}

    # ---------- 检查 Wiki 条目契约 ----------
    topics_dir = os.path.join(wiki_root, "topics")
    topic_keys = []
    for key, info in sorted(wiki_files.items()):
        if not key.startswith("topics/"):
            continue
        topic_keys.append(key)
        text = info["text"]
        meta = parse_meta(text)
        info["meta"] = meta
        info["status"] = meta.get("状态")
        where = os.path.relpath(info["path"], root)

        if not meta:
            rep.err(where, "缺少引用块（> **TL;DR**：…）—— 机器契约不存在")
            continue

        for field in REQUIRED_META:
            if field not in meta or not meta[field]:
                rep.err(where, f"缺字段：{field}")

        expect_id = key
        got_id = meta.get("ID", "").strip().strip("`")
        if got_id and got_id != expect_id:
            rep.err(where, f"ID 与路径不一致：ID=`{got_id}`，应为 `{expect_id}`")

        status = (meta.get("状态") or "").strip().strip("`")
        if status and status not in VALID_STATUS:
            rep.err(where, f"状态取值非法：`{status}`（应为 {'/'.join(sorted(VALID_STATUS))}）")

        for field in ("最后核验", "有效期至"):
            raw = meta.get(field, "")
            if not raw:
                continue
            parsed = parse_date(raw)
            if parsed is None:
                rep.err(where, f"{field} 不是 YYYY-MM-DD：`{raw}`")
            elif field == "有效期至":
                days = (parsed - today).days
                if days < 0:
                    rep.err(where, f"已过期 {-days} 天（有效期至 {parsed}）—— 需重编译或续期")
                elif days <= 30:
                    rep.warn(where, f"{days} 天后到期（{parsed}）")
            else:
                if parsed > today:
                    rep.warn(where, f"最后核验日期在未来（{parsed}）")

        tldr = meta.get("TL;DR", "")
        if tldr:
            n = len(tldr)
            if n < 20:
                rep.warn(where, f"TL;DR 过短（{n} 字），可能给不出结论")
            elif n > 160:
                rep.warn(where, f"TL;DR 过长（{n} 字），超出「三行摘要」的用意")

        if not info["anchors"]:
            rep.warn(where, "没有任何锚点，Skill 无法按粒度引用它")

    # ---------- 检查 Skill ----------
    skills_root = os.path.join(root, "skills")
    skill_files = walk_md(skills_root, root) if os.path.isdir(skills_root) else []
    skill_files = [p for p in skill_files if os.path.basename(p) == "SKILL.md"]
    refs_by_skill = {}
    total_refs = 0

    for path in skill_files:
        text = read_text(path)
        where = os.path.relpath(path, root)
        dirname = os.path.basename(os.path.dirname(path))

        m = NAME_RE.search(text)
        name = m.group("val").strip().strip("`") if m else ""
        if not name:
            rep.warn(where, "frontmatter 缺少 name")
        elif name != dirname:
            rep.warn(where, f"frontmatter name=`{name}` 与目录名 `{dirname}` 不一致")

        used = set()
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rm in REF_RE.finditer(line):
                ref_path = rm.group("path").strip("/")
                anchor = rm.group("anchor")
                total_refs += 1
                used.add(ref_path)
                loc = f"{where}:{lineno}"
                if ref_path not in wiki_files:
                    rep.err(loc, f"指针失效：`wiki:{ref_path}` 文件不存在")
                    continue
                info = wiki_files[ref_path]
                if anchor and anchor not in info["anchors"]:
                    rep.err(loc, f"锚点不存在：`wiki:{ref_path}#{anchor}`")
                if info["status"] == "deprecated" and ref_path.startswith("topics/"):
                    rep.err(loc, f"引用了已废弃条目：`wiki:{ref_path}`")
                if not anchor:
                    rep.warn(loc, f"引用未带锚点：`wiki:{ref_path}` —— 会读进整条，浪费上下文")
        refs_by_skill[dirname] = {"path": path, "used": used, "where": where}

    # ---------- 双向依赖 ----------
    for key in topic_keys:
        info = wiki_files[key]
        where = os.path.relpath(info["path"], root)
        declared = {skill_key_from_dep(d) for d in dep_names(info["meta"].get("依赖本条的 Skill", ""))}
        referenced_by = {name for name, rec in refs_by_skill.items() if key in rec["used"]}

        for name in sorted(declared - referenced_by):
            rec = refs_by_skill.get(name)
            if rec is None:
                rep.err(where, f"声明的 Skill 不存在：`skills/{name}`")
            else:
                rep.err(where, f"声明依赖 `skills/{name}`，但该 Skill 并未引用本条（单向依赖）")

        for name in sorted(referenced_by - declared):
            rep.err(where, f"`skills/{name}` 引用了本条，但未登记在「依赖本条的 Skill」（单向依赖）")

    # ---------- 报告 ----------
    print(f"{DIM}根目录：{root}{RST}")
    print(
        f"Wiki 条目 {len(topic_keys)} 个 · Skill {len(skill_files)} 个 · 引用 {total_refs} 处 · "
        f"校验基准日 {today}{RST}"
    )
    print()

    for msg in rep.notes:
        print(f"  {msg}")
    for msg in rep.warns:
        print(f"{YEL}⚠{RST}  {msg}")
    for msg in rep.errors:
        print(f"{RED}✗{RST}  {msg}")

    if not rep.errors and not rep.warns:
        print(f"{GRN}✓ 全绿：契约完整、指针有效、依赖双向一致。{RST}")
    print()
    print(f"结果：{RED if rep.errors else GRN}{len(rep.errors)} error{RST} / {YEL}{len(rep.warns)} warn{RST}")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
