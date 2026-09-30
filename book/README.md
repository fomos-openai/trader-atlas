# 《Trader Atlas》小书

本目录保存可审阅的 Markdown 书稿与构建清单。唯一发布 PDF 位于 [`output/pdf/trader-atlas.pdf`](../output/pdf/trader-atlas.pdf)，历史版本通过 Git tag 与 GitHub Release 保存。

构建前从 Google Fonts 的固定提交下载 Noto Sans SC，并核对仓库约定的 SHA-256。脚本不允许回退到
系统字体：

```bash
curl -L --fail \
  'https://raw.githubusercontent.com/google/fonts/9710da1eacb3be272583c3224dcb70f9da6eadbb/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf' \
  -o /tmp/trader-atlas-NotoSansSC.ttf
echo 'a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da  /tmp/trader-atlas-NotoSansSC.ttf' \
  | shasum -a 256 -c -
uv run python scripts/build_book.py --font /tmp/trader-atlas-NotoSansSC.ttf
```

字体来源、许可证和校验和也记录在 [`book/assets/README.md`](assets/README.md)。

书稿只提炼判断框架、操作顺序和案例；会变化的法规、工具、数据接口与长清单通过 `docs/references/link-registry.yml` 外链到知识库。
