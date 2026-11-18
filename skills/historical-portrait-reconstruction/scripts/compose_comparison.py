#!/usr/bin/env python3
"""Compose authentic source pixels and an existing AI portrait; never generate either.

Requires Python 3.11+ and Pillow 13. Batch paths are relative to the manifest.
Each PNG has a same-stem JSON provenance file. Crops use decoded, unrotated
image coordinates; EXIF orientation is deliberately not applied implicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
except ImportError:
    raise SystemExit("Pillow is required. Install this project's requirements.txt first.")

BG = (247, 245, 240)
INK = (38, 44, 48)
DEFAULTS = {
    "title": "Historical portrait comparison",
    "source_label": "Source painting",
    "portrait_label": "AI interpretation",
    "caption": "Painting-based interpretation; historical likeness is not verified.",
    "panel_width": 720,
    "panel_height": 960,
    "font": None,
    "font_bold": None,
    "crop": None,
    "portrait_crop": None,
}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else hashlib.sha256(stream.read()).hexdigest()


def path_at(value: Any, base: Path, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty path string")
    path = Path(value).expanduser()
    return (base / path if not path.is_absolute() else path).resolve()


def crop_box(value: Any, size: tuple[int, int], label: str) -> tuple[int, int, int, int]:
    if value is None:
        return (0, 0, *size)
    if not isinstance(value, (list, tuple)) or len(value) != 4 or any(type(v) is not int for v in value):
        raise ValueError(f"{label} must contain four integer pixel coordinates")
    x0, y0, x1, y1 = value
    if not (0 <= x0 < x1 <= size[0] and 0 <= y0 < y1 <= size[1]):
        raise ValueError(f"{label} is outside the decoded image or has no area")
    return tuple(value)


def inspect_input(path: Path, crop: Any, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"{label} file does not exist: {path.name}")
    try:
        with Image.open(path) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError(f"{label} must be a single-frame image")
            image.load()
            size = image.size
            orientation = image.getexif().get(274, 1)
    except (OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise ValueError(f"Cannot decode {label}: {path.name}") from error
    return {"file": path.name, "sha256": digest(path), "image_size": list(size),
            "crop_xyxy": list(crop_box(crop, size, label + ' crop')),
            "exif_orientation": orientation, "orientation_applied": False}


def supports(font: ImageFont.FreeTypeFont, text: str) -> bool:
    """Detect missing glyphs by comparing to the font's .notdef mask."""
    missing = font.getmask("\U0010ffff")
    signature = (missing.size, bytes(missing))
    return all((mask.size, bytes(mask)) != signature
               for char in set(text) if not char.isspace()
               for mask in [font.getmask(char)])


def font_candidates() -> list[Path]:
    return [Path(p) for p in (
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/msyh.ttc"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )]


def choose_font(value: Any, base: Path, text: str, size: int) -> tuple[ImageFont.FreeTypeFont, str]:
    candidates = [path_at(value, base, "font")] if value is not None else font_candidates()
    for candidate in candidates:
        try:
            font = ImageFont.truetype(str(candidate), size=size)
        except (OSError, ValueError):
            if value is not None:
                raise ValueError(f"Cannot load font: {candidate.name}; pass a readable TTF/OTF/TTC file")
            continue
        if supports(font, text):
            return font, candidate.name
        if value is not None:
            raise ValueError(f"Font {candidate.name} lacks required glyphs; supply a font covering the labels")
    if value is None and text.isascii():
        return ImageFont.load_default(size=size), "Pillow default"
    raise ValueError("No installed font covers the text. Use --font with a suitable font, such as Noto Sans CJK.")


def aliases(a: Path, b: Path) -> bool:
    if a == b:
        return True
    try:
        return a.exists() and b.exists() and a.samefile(b)
    except OSError:
        return False


def prepare(raw: dict[str, Any], base: Path, defaults: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Every manifest item must be an object")
    item = {**defaults, **raw}
    if not isinstance(item.get("id"), str) or not item["id"].strip():
        raise ValueError("Every item must have a nonempty string id")
    for key in ("source", "portrait", "output"):
        item[key] = path_at(item.get(key), base, key)
    if item["output"].suffix.lower() != ".png":
        raise ValueError("Output must have the .png extension")
    item["sidecar"] = item["output"].with_suffix(".json")
    for key in ("title", "source_label", "portrait_label", "caption"):
        if not isinstance(item[key], str):
            raise ValueError(f"{key} must be text")
        if any(not char.isprintable() and char not in "\n\t" for char in item[key]):
            raise ValueError(f"{key} contains unsupported control characters")
    for key in ("panel_width", "panel_height"):
        if type(item[key]) is not int or item[key] < 120:
            raise ValueError(f"{key} must be an integer of at least 120 pixels")
    item["source_info"] = inspect_input(item["source"], item["crop"], "source")
    item["portrait_info"] = inspect_input(item["portrait"], item["portrait_crop"], "portrait")
    size = max(14, min(30, item["panel_width"] // 24))
    text = "\n".join(item[key] for key in ("title", "source_label", "portrait_label", "caption"))
    item["font_object"], item["font_name"] = choose_font(item["font"], base, text, size)
    item["bold_object"], item["bold_name"] = choose_font(item["font_bold"] or item["font"], base, text, size + 3)
    return item


def preflight(items: list[dict[str, Any]], report: Path | None, manifest: Path | None) -> None:
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate item ids are not allowed")
    inputs = [item[key] for item in items for key in ("source", "portrait")]
    if manifest:
        inputs.append(manifest)
    outputs = [item[key] for item in items for key in ("output", "sidecar")]
    if report:
        outputs.append(report)
    for index, output in enumerate(outputs):
        if any(aliases(output, source) for source in inputs):
            raise ValueError(f"Output would overwrite an input: {output.name}")
        if any(aliases(output, previous) for previous in outputs[:index]):
            raise ValueError(f"Duplicate or overlapping output: {output.name}")
        if output.exists() and not output.is_file():
            raise ValueError(f"Output path is not a regular file: {output.name}")
        parent = output.parent
        while not parent.exists():
            parent = parent.parent
        if not parent.is_dir():
            raise ValueError(f"Output parent is not a directory: {output.name}")


def wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.expandtabs(4).split("\n"):
        current = ""
        for char in paragraph:
            if current and font.getlength(current + char) > width:
                lines.append(current.rstrip())
                current = char.lstrip()
            else:
                current += char
        lines.append(current.rstrip())
    return lines if text else []


def draw_lines(draw: ImageDraw.ImageDraw, lines: list[str], font: ImageFont.FreeTypeFont,
               x: int, y: int, line_height: int) -> None:
    for line in lines:
        draw.text((x, y), line, font=font, fill=INK, anchor="lt")
        y += line_height


def place_image(canvas: Image.Image, path: Path, info: dict[str, Any],
                panel: tuple[int, int, int, int]) -> dict[str, Any]:
    if digest(path) != info["sha256"]:
        raise ValueError(f"Input changed after validation: {path.name}")
    with Image.open(path) as opened:
        image = opened.crop(tuple(info["crop_xyxy"])).convert("RGBA")
    scale = min(panel[2] / image.width, panel[3] / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    image = image.resize(size, Image.Resampling.LANCZOS)
    # Only transparency is composited; opaque source pixels receive no color edits.
    flattened = Image.new("RGBA", size, (*BG, 255))
    flattened.alpha_composite(image)
    x, y = panel[0] + (panel[2] - size[0]) // 2, panel[1] + (panel[3] - size[1]) // 2
    canvas.paste(flattened.convert("RGB"), (x, y))
    return {**info, "display": {"box_xyxy": [x, y, x + size[0], y + size[1]],
            "scale": scale, "rendered_size": list(size), "resampling": "LANCZOS",
            "rounding": "nearest integer", "alpha_background_rgb": list(BG)}}


def json_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".hpr-", suffix=".json", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(json_bytes(data))
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def compose(item: dict[str, Any]) -> None:
    width, height = item["panel_width"], item["panel_height"]
    margin = max(16, width // 30)
    canvas_width = width * 2 + margin * 3
    normal, bold = item["font_object"], item["bold_object"]
    line_height = round(normal.size * 1.5)
    bold_height = round(bold.size * 1.5)
    title = wrap(item["title"], bold, canvas_width - 2 * margin)
    labels = [wrap(item[key], bold, width) for key in ("source_label", "portrait_label")]
    caption = wrap(item["caption"], normal, canvas_width - 2 * margin)
    label_y = margin + len(title) * bold_height + margin
    image_y = label_y + max(map(len, labels), default=0) * bold_height + margin
    footer_y = image_y + height + margin
    canvas = Image.new("RGB", (canvas_width, footer_y + len(caption) * line_height + margin), BG)
    draw = ImageDraw.Draw(canvas)
    draw_lines(draw, title, bold, margin, margin, bold_height)
    for x, label in zip((margin, width + 2 * margin), labels):
        draw_lines(draw, label, bold, x, label_y, bold_height)
    draw_lines(draw, caption, normal, margin, footer_y, line_height)
    source = place_image(canvas, item["source"], item["source_info"], (margin, image_y, width, height))
    portrait = place_image(canvas, item["portrait"], item["portrait_info"], (width + 2 * margin, image_y, width, height))
    record = {"schema_version": "1.0", "id": item["id"], "title": item["title"],
              "source": source, "portrait": portrait, "caption": item["caption"],
              "labels": {"source": item["source_label"], "portrait": item["portrait_label"]},
              "fonts": {"regular": item["font_name"], "bold": item["bold_name"]},
              "output": {"file": item["output"].name, "image_size": list(canvas.size)},
              "method": "Deterministic crop, proportional resize and side-by-side composition",
              "historical_likeness": "not-verifiable", "visual_review": "not-performed-by-script"}
    info = PngImagePlugin.PngInfo()
    info.add_text("hpr_provenance", json.dumps(record, ensure_ascii=False))
    output = item["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".hpr-", suffix=".png", dir=output.parent)
    os.close(fd)
    temp = Path(name)
    try:
        canvas.save(temp, format="PNG", pnginfo=info)
        record["output"]["sha256"] = digest(temp)
        temp.replace(output)
        atomic_json(item["sidecar"], record)
    finally:
        temp.unlink(missing_ok=True)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument("--source")
    result.add_argument("--portrait")
    result.add_argument("--output")
    result.add_argument("--manifest", help="JSON object containing an items array; paths relative to this file")
    result.add_argument("--report", help="Batch status JSON path; default: batch_report.json beside manifest")
    for key in ("title", "source_label", "portrait_label", "caption", "font", "font_bold"):
        result.add_argument("--" + key.replace("_", "-"), default=DEFAULTS[key])
    for key in ("panel_width", "panel_height"):
        result.add_argument("--" + key.replace("_", "-"), type=int, default=DEFAULTS[key])
    result.add_argument("--crop", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    result.add_argument("--portrait-crop", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    return result


def main(argv: list[str] | None = None) -> int:
    cli = parser()
    args = cli.parse_args(argv)
    if args.manifest and any((args.source, args.portrait, args.output)):
        cli.error("--manifest is an alternative to --source/--portrait/--output")
    if not args.manifest and not all((args.source, args.portrait, args.output)):
        cli.error("provide --source, --portrait and --output, or use --manifest")
    if args.report and not args.manifest:
        cli.error("--report is only available with --manifest")
    try:
        defaults = {key: getattr(args, key) for key in DEFAULTS}
        report = manifest = None
        base = Path.cwd()
        if args.manifest:
            manifest = path_at(args.manifest, base, "manifest")
            base = manifest.parent
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("items"), list) or not data["items"]:
                raise ValueError("Manifest must be an object with a nonempty items array")
            raw = data["items"]
            report = path_at(args.report or "batch_report.json", base, "report")
        else:
            raw = [{"id": Path(args.output).stem, "source": args.source,
                    "portrait": args.portrait, "output": args.output}]
        items = [prepare(item, base, defaults) for item in raw]
        preflight(items, report, manifest)
        statuses = []
        for item in items:
            status = {"id": item["id"], "output": item["output"].name, "status": "completed"}
            try:
                compose(item)
            except (OSError, ValueError) as error:
                message = str(error)
                for key in ("source", "portrait", "output", "sidecar"):
                    message = message.replace(str(item[key]), item[key].name)
                status.update(status="failed", error=message)
            statuses.append(status)
        summary = {"schema_version": "1.0", "requested": len(items),
                   "completed": sum(s["status"] == "completed" for s in statuses), "items": statuses}
        summary["status"] = "completed" if summary["completed"] == len(items) else "incomplete"
        if report:
            atomic_json(report, summary)
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if summary["status"] == "completed" else 1
    except (OSError, ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
