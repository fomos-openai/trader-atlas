#!/usr/bin/env python3
"""Build the Trader Atlas Chinese field guide as a linked, inspectable PDF."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm as unit_mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
PAGE_SIZE = (160 * mm, 230 * mm)
NAVY = colors.HexColor("#0B132B")
BLUE = colors.HexColor("#2563EB")
CYAN = colors.HexColor("#22D3EE")
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#5E6B85")
PALE = colors.HexColor("#EAF1FF")
AMBER = colors.HexColor("#F59E0B")
EXPECTED_NOTO_SHA256 = "a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da"


@dataclass(frozen=True)
class BookConfig:
    title: str
    subtitle: str
    version: str
    author: str
    repository: str
    release_ref: str
    license: str
    output: Path
    chapters: tuple[Path, ...]
    chapter_links: dict[str, tuple[str, ...]]


def load_config(path: Path) -> BookConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return BookConfig(
        title=raw["title"],
        subtitle=raw["subtitle"],
        version=str(raw["version"]),
        author=raw["author"],
        repository=raw["repository"].rstrip("/"),
        release_ref=raw["release_ref"],
        license=raw["license"],
        output=ROOT / raw["output"],
        chapters=tuple(ROOT / item for item in raw["chapters"]),
        chapter_links={key: tuple(value) for key, value in raw.get("chapter_links", {}).items()},
    )


def register_font(font_path: Path) -> tuple[str, str]:
    candidates = [
        font_path,
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            prepared = candidate
            if candidate.name.startswith("NotoSansSC"):
                if digest != EXPECTED_NOTO_SHA256:
                    raise RuntimeError(
                        "Noto Sans SC checksum mismatch: "
                        f"expected {EXPECTED_NOTO_SHA256}, got {digest}"
                    )
                try:
                    from fontTools.ttLib import TTFont as FontToolsTTFont
                    from fontTools.varLib.instancer import instantiateVariableFont

                    variable = FontToolsTTFont(candidate)
                    if "fvar" in variable:
                        prepared = ROOT / "tmp/pdfs/NotoSansSC-Regular.ttf"
                        prepared.parent.mkdir(parents=True, exist_ok=True)
                        regular = instantiateVariableFont(variable, {"wght": 400}, inplace=False)
                        regular.save(prepared)
                except ImportError as error:
                    raise RuntimeError(
                        "fonttools is required to freeze Noto Sans SC at weight 400"
                    ) from error
            pdfmetrics.registerFont(TTFont("TraderAtlasSans", str(prepared)))
            return "TraderAtlasSans", f"{candidate.name} sha256:{digest}"
    raise FileNotFoundError("No CJK font found. Place NotoSansSC-Regular.ttf in book/assets/.")


def inline_markup(text: str) -> str:
    placeholders: list[str] = []

    def hold(value: str) -> str:
        placeholders.append(value)
        return f"@@H{len(placeholders) - 1}@@"

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda m: hold(
            f'<link href="{escape(m.group(2), quote=True)}" color="#2563EB">'
            f"{escape(m.group(1))}</link>"
        ),
        text,
    )
    text = re.sub(
        r"`([^`]+)`",
        lambda m: hold(f'<font name="Courier" color="#394967">{escape(m.group(1))}</font>'),
        text,
    )
    text = escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    for index, value in enumerate(placeholders):
        text = text.replace(f"@@H{index}@@", value)
    return text


class TraderAtlasDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, config: BookConfig, font_name: str):
        super().__init__(
            filename,
            pagesize=PAGE_SIZE,
            rightMargin=18 * unit_mm,
            leftMargin=18 * unit_mm,
            topMargin=20 * unit_mm,
            bottomMargin=18 * unit_mm,
            title=config.title,
            author=config.author,
            subject="OPC professional independent trader knowledge tree",
            creator="Trader Atlas / ReportLab",
        )
        self.config = config
        self.font_name = font_name
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="body",
        )
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self._draw_page)])
        self._heading_seq = 0

    def _draw_page(self, canvas, doc) -> None:
        canvas.saveState()
        canvas.setTitle(self.config.title)
        if doc.page > 2:
            canvas.setStrokeColor(colors.HexColor("#D8E0EF"))
            canvas.setLineWidth(0.5)
            canvas.line(18 * mm, 17 * mm, PAGE_SIZE[0] - 18 * mm, 17 * mm)
            canvas.setFont(self.font_name, 7.5)
            canvas.setFillColor(MUTED)
            canvas.drawString(18 * mm, 11 * mm, "TRADER ATLAS · 研究优先，风险先行")
            canvas.drawRightString(PAGE_SIZE[0] - 18 * mm, 11 * mm, f"{doc.page:02d}")
        canvas.restoreState()

    def afterFlowable(self, flowable) -> None:
        if not isinstance(flowable, Paragraph):
            return
        level = getattr(flowable, "toc_level", None)
        if level is None:
            return
        key = getattr(flowable, "bookmark_key", None)
        if key is None:
            self._heading_seq += 1
            key = f"heading-{self._heading_seq}"
            flowable.bookmark_key = key
        text = flowable.getPlainText()
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
        self.notify("TOCEntry", (level, text, self.page, key))


def styles(font_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "BodyCN",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=11.2,
            leading=18.8,
            textColor=INK,
            spaceAfter=7,
            wordWrap="CJK",
            allowWidows=0,
            allowOrphans=0,
        ),
        "h1": ParagraphStyle(
            "ChapterCN",
            parent=base["Heading1"],
            fontName=font_name,
            fontSize=23,
            leading=31,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=16,
            wordWrap="CJK",
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "SectionCN",
            parent=base["Heading2"],
            fontName=font_name,
            fontSize=15,
            leading=22,
            textColor=BLUE,
            spaceBefore=14,
            spaceAfter=8,
            wordWrap="CJK",
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "SubsectionCN",
            parent=base["Heading3"],
            fontName=font_name,
            fontSize=12.5,
            leading=18,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=5,
            wordWrap="CJK",
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "BulletCN",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=10.8,
            leading=17.8,
            leftIndent=14,
            firstLineIndent=-8,
            bulletIndent=2,
            textColor=INK,
            spaceAfter=4,
            wordWrap="CJK",
        ),
        "quote": ParagraphStyle(
            "QuoteCN",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=11.4,
            leading=19,
            leftIndent=14,
            rightIndent=8,
            borderColor=CYAN,
            borderWidth=2,
            borderPadding=(7, 10, 7, 10),
            backColor=PALE,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=10,
            wordWrap="CJK",
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=7.8,
            leading=11.5,
            leftIndent=8,
            rightIndent=8,
            borderColor=colors.HexColor("#CBD5E1"),
            borderWidth=0.7,
            borderPadding=8,
            backColor=colors.HexColor("#F8FAFC"),
            textColor=colors.HexColor("#24324A"),
            spaceBefore=6,
            spaceAfter=10,
        ),
        "small": ParagraphStyle(
            "SmallCN",
            parent=base["BodyText"],
            fontName=font_name,
            fontSize=8.2,
            leading=12.5,
            textColor=MUTED,
            wordWrap="CJK",
        ),
        "toc": ParagraphStyle(
            "TocCN",
            fontName=font_name,
            fontSize=10,
            leading=16,
            textColor=INK,
        ),
    }


def cover_story(config: BookConfig, font_name: str, font_note: str):
    title_style = ParagraphStyle(
        "CoverTitle",
        fontName=font_name,
        fontSize=32,
        leading=40,
        textColor=colors.white,
        alignment=TA_LEFT,
        wordWrap="CJK",
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        fontName=font_name,
        fontSize=15,
        leading=24,
        textColor=colors.HexColor("#CDEBFF"),
        wordWrap="CJK",
    )
    small_white = ParagraphStyle(
        "CoverSmall",
        fontName=font_name,
        fontSize=9,
        leading=15,
        textColor=colors.HexColor("#D8E6FF"),
        wordWrap="CJK",
    )
    band = Table(
        [[Paragraph("OPC · QUANT RESEARCH · RISK-FIRST", small_white)]],
        colWidths=[118 * mm],
        rowHeights=[12 * mm],
    )
    band.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BLUE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    cover = Table(
        [
            [band],
            [Spacer(1, 21 * mm)],
            [Paragraph(escape(config.title), title_style)],
            [Spacer(1, 5 * mm)],
            [Paragraph(escape(config.subtitle), subtitle_style)],
            [Spacer(1, 48 * mm)],
            [
                Paragraph(
                    "从研究纪律到本地 paper 的第一年路线<br/>"
                    "香港法域 · BTC/ETH 现货趋势轮动 · 无实盘连接",
                    small_white,
                )
            ],
            [Spacer(1, 10 * mm)],
            [Paragraph(f"v{config.version} · {date.today().isoformat()}", small_white)],
        ],
        colWidths=[124 * mm],
        rowHeights=[None] * 9,
    )
    cover.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("BOX", (0, 0), (-1, -1), 0, NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), 8 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    legal = Paragraph(
        f"作者：{escape(config.author)}<br/>许可：{escape(config.license)}<br/>"
        f"字体：{escape(font_note)}<br/>"
        "本书仅供教育和研究，不构成投资、法律或税务建议。",
        ParagraphStyle(
            "Legal",
            fontName=font_name,
            fontSize=7.8,
            leading=12,
            textColor=MUTED,
            wordWrap="CJK",
        ),
    )
    return [cover, PageBreak(), legal, Spacer(1, 8 * mm)]


def toc_story(style_map: dict[str, ParagraphStyle]):
    title = Paragraph("目录", style_map["h1"])
    title.toc_level = None
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "TOCChapter",
            fontName=style_map["body"].fontName,
            fontSize=10.5,
            leading=18,
            textColor=NAVY,
            leftIndent=0,
            firstLineIndent=0,
            spaceBefore=4,
        ),
        ParagraphStyle(
            "TOCSection",
            fontName=style_map["body"].fontName,
            fontSize=8.7,
            leading=14,
            textColor=MUTED,
            leftIndent=12,
            firstLineIndent=0,
        ),
    ]
    return [title, toc, PageBreak()]


def reader_guide_story(config: BookConfig, style_map: dict[str, ParagraphStyle]):
    guide_title = Paragraph("阅读导航", style_map["h1"])
    guide_title.toc_level = None
    evidence_title = Paragraph("风险与证据约定", style_map["h1"])
    evidence_title.toc_level = None
    repository = escape(config.repository, quote=True)
    return [
        guide_title,
        Paragraph(
            "这本小书提供第一年路线与决策框架，完整知识条目、模板、代码和审计证据保留在开源仓库。"
            "建议先选一种阅读方式，再按章末链接下钻，避免把阅读量误当成研究进度。",
            style_map["body"],
        ),
        Paragraph(
            "• 快速路线：阅读第二章，完成个人交易政策与风险预算，再运行第六章案例。",
            style_map["bullet"],
        ),
        Paragraph(
            "• 系统路线：按第一至第七章顺序推进，每章只在产物通过阶段门后继续。",
            style_map["bullet"],
        ),
        Paragraph(
            "• 审查路线：从免责声明、第五章风险预算和第七章停止规则开始，反向检查研究。",
            style_map["bullet"],
        ),
        Spacer(1, 6 * mm),
        Paragraph(
            f'<link href="{repository}" color="#2563EB">开源仓库与更新记录：{repository}</link>',
            style_map["body"],
        ),
        Paragraph(
            "书内版本固定在发布标签；法规、平台状态、工具版本与外部链接具有时效性，实际使用时应回到仓库的"
            "官方来源登记，并查看页面中的 last_reviewed、as_of 与 review_due。",
            style_map["body"],
        ),
        PageBreak(),
        evidence_title,
        Paragraph(
            "Trader Atlas 不把回测或 paper Sharpe 当成盈利证明。这里的“稳定”只表示研究可复现、"
            "成本后样本外有正向证据、风险边界明确、仿真过程可审计；未来收益仍然不确定。",
            style_map["quote"],
        ),
        Paragraph(
            "证据分为实现证据、历史证据、样本外证据与运行证据。合成数据只能证明实现满足不变量；"
            "历史回测只能描述已发生样本；本地 paper 只能验证决策与记账流程。"
            "任何层级失败，都应公开标记 rejected、重做或退役，不能回看 holdout 后包装成成功。",
            style_map["body"],
        ),
        Paragraph(
            "v0.1 的工程边界止于本地订单意向与审计账本：不连接交易 API、不保存密钥、不自动下单，"
            "不包含杠杆、做空或衍生品执行。个人本金、生活现金跑道、账户和税务资料也不进入公开仓库。",
            style_map["body"],
        ),
        Paragraph(
            "每个结论都应能回答四个问题：使用了什么数据与时间语义；承担了哪些交易成本；"
            "在哪个样本上形成与检验；什么条件会暂停、重做或退役。回答不了时，默认结论尚未成立。",
            style_map["body"],
        ),
        PageBreak(),
    ]


def load_link_registry() -> dict[str, dict[str, str]]:
    path = ROOT / "docs/references/link-registry.yml"
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    links = raw.get("links", {})
    if not isinstance(links, dict):
        raise ValueError("link-registry.yml must contain a top-level links mapping")
    return links


def repository_link(
    config: BookConfig,
    chapter: Path,
    style_map,
    registry: dict[str, dict[str, str]],
):
    chapter_name = chapter.name
    repo_path = chapter.relative_to(ROOT).as_posix()
    url = f"{config.repository}/blob/{config.release_ref}/{repo_path}"
    rows = [
        Spacer(1, 5 * mm),
        HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#CBD5E1")),
        Spacer(1, 3 * mm),
        Paragraph(
            f'<b>开源源稿：</b> <link href="{url}" color="#2563EB">{escape(chapter_name)}</link>',
            style_map["small"],
        ),
    ]
    for link_id in config.chapter_links.get(chapter_name, ()):
        entry = registry.get(link_id)
        if not entry:
            raise ValueError(f"Book link id is missing from link registry: {link_id}")
        path = entry["path"]
        title = entry["title"]
        target = f"{config.repository}/blob/{config.release_ref}/{path}"
        rows.append(
            Paragraph(
                f'<b>延伸：</b> <link href="{target}" color="#2563EB">{escape(title)}</link>',
                style_map["small"],
            )
        )
    return KeepTogether(rows)


def parse_markdown(
    text: str,
    style_map,
    config: BookConfig,
    chapter: Path,
    registry: dict[str, dict[str, str]],
):
    story = []
    paragraph: list[str] = []
    code: list[str] = []
    in_code = False
    chapter_seen = False

    def flush_paragraph() -> None:
        if paragraph:
            joined = " ".join(item.strip() for item in paragraph).strip()
            if joined:
                story.append(Paragraph(inline_markup(joined), style_map["body"]))
            paragraph.clear()

    def flush_code() -> None:
        if code:
            story.append(Preformatted("\n".join(code), style_map["code"]))
            code.clear()

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            flush_paragraph()
            if in_code:
                flush_code()
            in_code = not in_code
            continue
        if in_code:
            code.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            if level == 1:
                if chapter_seen:
                    story.append(PageBreak())
                chapter_seen = True
            style = style_map[f"h{level}"]
            item = Paragraph(inline_markup(heading.group(2)), style)
            item.toc_level = level - 1
            story.append(item)
            if level == 1:
                story.append(HRFlowable(width="42%", thickness=2.2, color=CYAN, hAlign="LEFT"))
                story.extend(
                    [
                        Spacer(1, 92 * mm),
                        Paragraph(
                            "TRADER ATLAS · OPEN SOURCE FIELD GUIDE · v0.1",
                            style_map["small"],
                        ),
                        Spacer(1, 4 * mm),
                        Paragraph(
                            "本章把决策框架压缩在书内，并在章末链接完整知识页、模板与可运行证据。",
                            style_map["small"],
                        ),
                        PageBreak(),
                    ]
                )
            continue
        if line.startswith("> "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[2:]), style_map["quote"]))
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        number = re.match(r"^(\d+)\.\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            story.append(
                Paragraph(inline_markup(bullet.group(1)), style_map["bullet"], bulletText="•")
            )
            continue
        if number:
            flush_paragraph()
            story.append(
                Paragraph(
                    inline_markup(number.group(2)),
                    style_map["bullet"],
                    bulletText=f"{number.group(1)}.",
                )
            )
            continue
        paragraph.append(line)
    flush_paragraph()
    flush_code()
    story.append(repository_link(config, chapter, style_map, registry))
    return story


def git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def build(config_path: Path, font_path: Path) -> Path:
    config = load_config(config_path)
    config.output.parent.mkdir(parents=True, exist_ok=True)
    font_name, font_note = register_font(font_path)
    style_map = styles(font_name)
    registry = load_link_registry()
    doc = TraderAtlasDocTemplate(str(config.output), config, font_name)
    story = cover_story(config, font_name, font_note)
    story.extend(
        [
            Paragraph(
                f"构建版本：v{config.version} · 源提交：{git_revision()} · "
                f"构建日期：{date.today().isoformat()}",
                style_map["small"],
            ),
            Spacer(1, 6 * mm),
            Paragraph(
                f'<link href="{config.repository}" color="#2563EB">{config.repository}</link>',
                style_map["small"],
            ),
            PageBreak(),
        ]
    )
    story.extend(reader_guide_story(config, style_map))
    story.extend(toc_story(style_map))
    for index, chapter in enumerate(config.chapters):
        if index:
            story.append(PageBreak())
        story.extend(
            parse_markdown(
                chapter.read_text(encoding="utf-8"),
                style_map,
                config,
                chapter,
                registry,
            )
        )
    doc.multiBuild(story)
    return config.output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "book/book.yml")
    parser.add_argument(
        "--font",
        type=Path,
        default=ROOT / "book/assets/NotoSansSC-Regular.ttf",
    )
    args = parser.parse_args()
    output = build(args.config, args.font)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
