# Book assets

The published PDF embeds a subset of **Noto Sans SC**, licensed under the SIL Open Font License 1.1.

- Source: `https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf`
- Expected SHA-256: `a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da`
- Upstream: Google Fonts / Noto Project

The 17 MB source font is not committed. Download it to a temporary location and pass it to the builder:

```bash
python scripts/build_book.py --font /path/to/NotoSansSC.ttf
```

The final PDF embeds only the glyph data used by the document through ReportLab's TrueType subsetting.
