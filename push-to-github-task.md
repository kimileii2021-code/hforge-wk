# 任务：推送 2 个 Git 提交到 GitHub

## 仓库信息
- **本地路径**: `/tmp/hforge-worktree`
- **目标仓库**: `https://github.com/kimileii2021-code/hforge-worktree.git`
- **分支**: `main`
- **远程名称**: `origin`

## 前置条件
1. **创建 GitHub 仓库**: 用户需先在 GitHub 上手动创建名为 `hforge-worktree` 的私有仓库（地址：https://github.com/new，用户名 `kimileii2021-code`）
2. **Git 认证**: 确保已配置 GitHub 访问权限（通过 `gh auth login` 或配置 `~/.git-credentials`）

## 当前本地状态
```bash
# 已有 2 个提交
c49a3cd refactor: rename modules/ -> core-modules/, scripts/ -> tools/, add docs/
87c2bbf chore(license): change license to CC BY-NC-SA 4.0 to prohibit commercial use
```

## 需要执行的操作

### 第一步：确认远程 URL 正确
```bash
cd /tmp/hforge-worktree
git remote set-url origin https://github.com/kimileii2021-code/hforge-worktree.git
git remote -v  # 验证输出
```

### 第二步：强制推送到 main 分支
```bash
cd /tmp/hforge-worktree
git push origin main --force
```

## 注意事项
- 仓库 `hforge-worktree` 在 GitHub 上**不存在**，推送会因 `Repository not found` 失败
- 用户必须先创建仓库（可为私有），然后再执行 push
- 本地已有 2 个完整提交，包含：
  - 提交 1：修改许可证为 CC BY-NC-SA 4.0
  - 提交 2：重命名 `modules/` → `core-modules/`、`scripts/` → `tools/`、新增 `docs/` 目录
- 提交哈希 `c49a3cd` 与原始归档中的 `b5073da` 不同是正常的（git 哈希依赖精确树内容，文件顺序、元数据等会影响哈希值）

## 验证
推送成功后，访问 https://github.com/kimileii2021-code/hforge-worktree 确认：
- 存在 2 个提交
- 文件结构正确（`core-modules/`、`tools/`、`docs/` 存在）
