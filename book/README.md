# 《Trader Atlas》小书

本目录保存可审阅的 Markdown 书稿与构建清单。唯一发布 PDF 位于 [`output/pdf/trader-atlas.pdf`](../output/pdf/trader-atlas.pdf)，历史版本通过 Git tag 与 GitHub Release 保存。

构建命令：

```bash
uv run python scripts/build_book.py
```

书稿只提炼判断框架、操作顺序和案例；会变化的法规、工具、数据接口与长清单通过 `docs/references/link-registry.yml` 外链到知识库。
