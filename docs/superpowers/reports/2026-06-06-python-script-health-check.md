# Python 脚本可运行性体检报告

- 体检时间: 2026-06-06
- 体检范围: 4 个 Python 脚本
- 体检深度: 静态检查 + 导入可行性 (未执行 main，未执行模块代码)
- 体检环境: master_study_env (只含 packaging/pip/setuptools/wheel)
- 工具脚本: tools/script_health_check.py

## 汇总：环境 vs 脚本本身

| 维度 | 数量 |
|------|------|
| 脚本总数 | 4 |
| 语法 OK | 3 |
| 语法失败 | 1 |
| 脚本本身有问题 (语法/硬编码路径) | 3 |
| 只缺包、脚本本身健康 (env-only) | 0 |
| 完全 clean | 1 |


## 缺失最多的模块 (Top 10)

- (无缺失模块)


## 优先级建议（基于修复工作量）

1. **易修复（仅装包）**: 装上缺失的包就能跑，列在 "env-only" 分组
2. **中等（装包 + 改路径）**: 还要把 F:/... 改成 __file__ 相对路径
3. **难（脚本本身有语法/逻辑问题）**: 需要人工 review


## 按子项目分节详述（每个脚本一节）
### other/
#### ❌ _test_bad_syntax.py  (issue_type: script-issue)
- 语法: invalid syntax (line 1)
- 硬编码路径: 无
- 全注释: 否
- Imports: (空)
- 缺失: (无)
- 跳过 main: 否
- 建议: 打开文件修正语法错误

#### ✅ _test_basic.py  (issue_type: clean)
- 语法: OK
- 硬编码路径: 无
- 全注释: 否
- Imports: (空)
- 缺失: (无)
- 跳过 main: 否
- 建议: 无需修改

#### ❌ _test_path_ast.py  (issue_type: script-issue)
- 语法: OK
- 硬编码路径: F:/foo/bar
- 全注释: 否
- Imports: (空)
- 缺失: (无)
- 跳过 main: 否
- 建议: 把 F:/... 路径改为 `pathlib.Path(__file__).parent / ...` 相对路径

#### ⚠️ _test_path_comment.py  (issue_type: all-commented)
- 语法: OK
- 硬编码路径: # F:/foo/bar comment only
- 全注释: 是
- Imports: (空)
- 缺失: (无)
- 跳过 main: 否
- 建议: 该文件是文档伪装的 .py。如不需要可删除；如需保留请改成 `.md` 或启用代码
