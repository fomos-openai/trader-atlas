# 贡献指南

感谢你帮助完善 Trader Atlas。项目同时包含知识内容、轻量 Python 研究代码、仿真报告和发布产物；
每个变更都应保持可追溯、可复现，并避免把教育材料表述成收益承诺。

## 开发流程

1. 从最新 `main` 创建功能分支。Codex 生成的变更使用 `codex/<topic>`；其他贡献可使用
   `docs/<topic>`、`feat/<topic>` 或 `fix/<topic>`。
2. 一个分支只处理一个主题，不直接向 `main` 推送。
3. 使用锁定依赖安装环境：

   ```bash
   uv sync --frozen --all-extras --all-groups
   ```

4. 在本地运行与改动相关的检查：

   ```bash
   uv run ruff format --check .
   uv run ruff check .
   uv run pytest -q
   uv run python scripts/validate_repo.py docs
   uv run mkdocs build --strict
   uv run python scripts/validate_repo.py simulation
   uv run python scripts/validate_repo.py artifacts
   ```

5. 提交拉取请求（PR），等待 `quality`、`docs`、`simulation`、`artifacts` 四个检查通过，解决全部
   review 对话后使用 squash merge；合并后删除功能分支。

本项目按独立维护者模式运行：`main` 要求 PR 和状态检查，但所需人工审批数为 **0**，避免作者无法
批准自己的 PR 而造成自锁。出现第二位长期维护者后，才把所需审批数提高为 1。禁止 force-push
或删除 `main`。

### 仓库管理员首次设置

这些设置不由仓库文件自动完成：

- 在 GitHub 的 `main` ruleset 中要求 PR、解决全部 review 对话，并把 `quality`、`docs`、
  `simulation`、`artifacts` 设为 required status checks；人工审批数保持 0。
- 禁止删除或 force-push `main`，并仅允许通过检查后的 squash merge。
- 在 **Settings → Pages → Build and deployment** 中选择 **GitHub Actions** 作为发布源。
- 保持默认 `GITHUB_TOKEN` 只读；只有 Pages 部署 job 获得 `pages: write` 与 `id-token: write`。

## 内容要求

- 中文正文优先，首次出现专业术语时给出常用英文名称或缩写。
- 区分事实、假设、经验判断与示例；量化结论写明口径、时间区间、样本和限制。
- 引用优先使用监管机构、交易所规则、标准、论文或其他一手资料。
- 香港监管、税务或其他时效性内容必须注明 `last_reviewed` 日期，并链接最新官方来源。
- 不写“保证盈利”“稳定收益”等无法验证的表述；风险与失败条件应与方法一同呈现。
- 保持站内相对链接有效；扩展内容链接到仓库或 Pages 的稳定路径。

## 代码、数据与仿真

- Python 代码应有类型提示、清晰边界和确定性测试；测试不得依赖实时网络或当前时间。
- CI 只使用 `tests/fixtures/**` 中的合成离线数据验证工程不变量，不以其证明策略盈利。
- 不提交交易所原始行情、下载缓存、API 密钥、账户标识或本地 `.env`。
- 真实历史仿真应记录数据提供方、交易对映射、UTC 时区、K 线周期、起止时间与 checksum；只提交
  经许可的派生摘要和 `reports/baseline/**` 中的配置、manifest、指标与说明。
- BTC/ETH 现货轮动实现应显式防止前视，使用前一根已收盘 K 线生成信号，并在下一可交易 bar
  执行；手续费、滑点、仓位和无杠杆/无做空约束必须可审计。

## 发布产物

- `diagrams/trader-atlas-knowledge-map.archify.json` 是知识地图真源，根目录
  `00-knowledge-map.html` 是经 Archify finalize 验证的发布物。
- `.archify/**` 中与该发布物对应的 candidate、finalize summary 与浏览器验证 evidence 作为审计包
  提交；重复试验、临时截图与已废弃候选应在合并前清理。
- `book/manuscript/**` 与 `book/book.yml` 是小书真源；最终 PDF 为
  `output/pdf/trader-atlas.pdf`。
- 更新 PDF 后必须渲染全部页面并人工检查截断、重叠、乱码、图表清晰度、页码与链接。自动检查
  不能替代视觉检查。
- `site/`、PDF 临时渲染图及其他可重建缓存不进入版本库。

## 许可与第三方材料

提交即表示你有权贡献相关内容，并同意按 [`LICENSING.md`](LICENSING.md) 的路径规则发布：代码
使用 MIT，原创知识内容使用 CC BY 4.0。第三方材料不会被重新授权；引用、图片、字体或数据必须
写明来源、许可及必要归属，并同步更新 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

PR 描述应说明变更目的、验证命令、内容来源、许可证影响，以及地图/PDF/baseline 是否需要同步。
