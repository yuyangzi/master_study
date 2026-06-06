# 环境修复计划 — Python 脚本可运行性修复 (Phase 1)

- **Date**: 2026-06-06
- **Spec**: `docs/superpowers/specs/2026-06-06-python-script-health-check-design.md`
- **Report**: `docs/superpowers/reports/2026-06-06-python-script-health-check.md`
- **Previous Plan**: `docs/superpowers/plans/2026-06-06-python-script-health-check-plan.md`
- **Status**: Plans

## 决策记录

| 议题 | 选项 | 决策 | 理由 |
|------|------|------|------|
| 修复范围 | ① env-only ② 全量修 ③ 全量+验证 | **① env-only** | 最低成本，不改源码（保持 spec 约束），只装包 |
| 环境策略 | ① 本地 ② 远程 ③ 两边 | **① 本地 master_study_env** | 配远程服务器需要额外工作；本地验证通过后再说 |
| 大包 (torch, mne) | ① 全装 ② 跳 mne ③ 跳过 | **① 全装** | 一次性到位，避免后续反复装 |
| 烟雾测试 | ① 做 ② 不做 | **② 不做** | 只验证 import 层面成功，不执行 `__main__` |
| feature_deal.py | ① 不处理 ② 启用注释 | **① 不处理** | 只有 1 个文件被标 all-commented，不影响大局 |

## 实现步骤

### Step 1 — 安装缺失包

**命令**:
```bash
master_study_env/bin/pip install \
    numpy pandas scikit-learn matplotlib tqdm \
    scipy mne seaborn joblib pyserial torchviz torch
```

**预期**: pip 下载并安装 12+ 个包（含依赖），总约 500MB。torch 为 macOS CPU-only 版。

**验证**: `master_study_env/bin/pip list --format=columns` 确认所有包出现在 `Installed` 列表。

### Step 2 — 运行体检工具确认状态变化

**命令**:
```bash
master_study_env/bin/python tools/script_health_check.py .
```

**预期变化**:
| 指标 | 装包前 | 装包后 |
|------|--------|--------|
| Env-only 脚本 | 18 个 MISSING | 18 个全部 OK |
| Mixed 脚本 | 31 个 MISSING | 31 个全部 OK（但路径问题仍在）|
| `import_missing_top` | 10 个模块缺失 | 空（全部安装成功）|

**关键验收**: 所有 `import_test` 值为 `OK`，不再有 `MISSING`。

### Step 3 — 提交环境状态（可选）

`master_study_env/` 在 `.gitignore` 里，不会被 git 跟踪。要记录变化有两种方式：

1. **不做任何 git 操作** — 环境是本地工具，不 commit
2. **Lock 文件** — `pip freeze > docs/superpowers/environment.lock` 记录精确版本

### Step 4 — 后续

- 用户自行试跑 env-only 脚本
- 修复 mixed 脚本（Phase 2 — 路径修复 + 装包）
- 远程服务器部署

## 验收标准

| # | 验收点 | 通过条件 |
|---|--------|---------|
| 1 | 包安装完成 | `pip list` 显示所有 12 个包 |
| 2 | 脚本 import 全部 OK | 体检报告 `import_test` 无 `MISSING` |
| 3 | 环境不污染 git | `git status` 在 `master_study_env` 无新文件 |

## 回滚

- `master_study_env/bin/pip uninstall -y <pkg>` 逐个卸载
- 或直接删环境重建：`conda remove -n master_study_env --all`
- 包安装在 conda env 内，不会影响系统 Python

## 产出物

- `docs/superpowers/reports/2026-06-06-python-script-health-check.md` — 更新后报告（MISSING → OK）
- `docs/superpowers/plans/2026-06-06-env-only-fix-plan.md` — 本计划
