# 第三方材料声明

本文件登记随仓库分发、但不由 Trader Atlas 维护者原创的材料。除非条目明确说明，第三方材料不受
本项目 MIT 或 CC BY 4.0 许可证重新授权。

## 当前随仓库分发的材料

### Creative Commons Attribution 4.0 International legal code

- 文件：`LICENSE-CONTENT`
- 来源：https://creativecommons.org/licenses/by/4.0/legalcode.txt
- 权利说明：Creative Commons 公共许可证文本依其声明以 CC0 Public Domain Dedication
  贡献至公共领域。
- 修改：未修改许可条款；仅以仓库文件形式收录。

### Noto Sans SC

- 使用位置：`output/pdf/trader-atlas.pdf` 中嵌入的字形子集（发布 PDF 存在时）。
- 来源：https://github.com/google/fonts/tree/9710da1eacb3be272583c3224dcb70f9da6eadbb/ofl/notosanssc
- 许可证：SIL Open Font License 1.1。
- 修改：源字体文件不入库；构建过程仅抽取书中使用的字形并嵌入 PDF。

### Archify viewer

- 使用位置：`00-knowledge-map.html` 中由 Archify 生成并内嵌的 viewer 代码（发布地图存在时）。
- 工具版本：Archify 3.0.1，基于 Cocoon AI architecture diagram generator。
- 版权：Copyright (c) 2026 tt-a1i (Archify)；Copyright (c) 2025 Cocoon AI。
- 许可证：MIT；许可与免责声明条款见根目录 `LICENSE`，上述第三方版权声明同时保留。
- 修改：本项目只提供知识地图数据与展示产物，不修改或再发布 Archify 工具包。

### JetBrains Mono

- 使用位置：`00-knowledge-map.html` 中由 Archify viewer 内嵌的字体数据。
- 来源：https://github.com/JetBrains/JetBrainsMono
- 许可证：SIL Open Font License 1.1。
- 修改：由 Archify 打包进单文件交付物；本仓库不单独分发源字体文件。

## 工具与依赖

除上文说明的嵌入内容外，构建工具、Python 包和 GitHub Actions 仅作为依赖被调用，不因本仓库的
许可证而改变其各自许可。精确版本见 `uv.lock` 与 `.github/workflows/**`。

## 数据与外部内容

当前不计划随仓库分发交易所原始行情。后续若加入数据、字体、图片、截图、商标、较长摘录或其他
第三方资产，贡献者必须在合并前新增条目，至少记录：文件路径、标题、权利人、来源 URL、获取日期、
许可证/使用依据、是否修改。仅有引用链接且未复制第三方内容时，一般无需在此登记。
