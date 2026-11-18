"""Behavior checks using synthetic raster inputs; no network or generation required."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from PIL import Image, ImageChops


REPO = Path(__file__).resolve().parents[1]
SCRIPT = Path(os.environ.get("HPR_COMPOSITOR", REPO / "skills/historical-portrait-reconstruction/scripts/compose_comparison.py"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompositorTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory()
        self.root = Path(self.sandbox.name)
        self.source = self.root / "source.png"
        self.portrait = self.root / "portrait.png"
        source = Image.new("RGB", (240, 180))
        source.putdata([((x * 3) % 256, (y * 5) % 256, (x + y) % 256)
                        for y in range(180) for x in range(240)])
        source.save(self.source)
        Image.new("RGB", (100, 200), (20, 70, 160)).save(self.portrait)
        self.source_hash = sha(self.source)
        self.portrait_hash = sha(self.portrait)

    def tearDown(self):
        self.sandbox.cleanup()

    def invoke(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              cwd=cwd or self.root, capture_output=True, text=True)

    def single(self, *args):
        return self.invoke("--source", self.source, "--portrait", self.portrait,
                           "--output", self.root / "comparison.png", *args)

    def test_source_pixels_crop_and_proportional_resize(self):
        run = self.single("--crop", 20, 30, 180, 150, "--panel-width", 320, "--panel-height", 240)
        self.assertEqual(run.returncode, 0, run.stderr)
        meta = json.loads((self.root / "comparison.json").read_text())
        self.assertEqual(meta["source"]["sha256"], self.source_hash)
        self.assertEqual(sha(self.source), self.source_hash)
        self.assertEqual(sha(self.portrait), self.portrait_hash)
        self.assertEqual(meta["source"]["display"]["scale"], 2)
        with Image.open(self.source) as original:
            expected = original.crop((20, 30, 180, 150)).resize((320, 240), Image.Resampling.LANCZOS)
        with Image.open(self.root / "comparison.png") as result:
            actual = result.crop(meta["source"]["display"]["box_xyxy"])
            self.assertIsNone(ImageChops.difference(actual, expected).getbbox())
            embedded = json.loads(result.info["hpr_provenance"])
            self.assertEqual(embedded["source"]["sha256"], self.source_hash)
        self.assertEqual(meta["output"]["sha256"], sha(self.root / "comparison.png"))
        self.assertNotIn(str(self.root), json.dumps(meta))
        self.assertEqual(meta["visual_review"], "not-performed-by-script")

    def test_twelve_item_batch_from_another_cwd(self):
        manifest = self.root / "batch.json"
        manifest.write_text(json.dumps({"items": [
            {"id": f"person-{i}", "source": "source.png", "portrait": "portrait.png",
             "output": f"output/{i}.png", "panel_width": 120, "panel_height": 120}
            for i in range(12)]}))
        other = self.root / "unrelated"
        other.mkdir()
        run = self.invoke("--manifest", manifest, cwd=other)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads((self.root / "batch_report.json").read_text())
        self.assertEqual(report["requested"], 12)
        self.assertEqual(report["completed"], 12)
        self.assertEqual(len(list((self.root / "output").glob("*.png"))), 12)
        self.assertEqual(sha(self.source), self.source_hash)

    def test_bad_crop_prevents_the_entire_batch(self):
        manifest = self.root / "batch.json"
        manifest.write_text(json.dumps({"items": [
            {"id": "valid", "source": "source.png", "portrait": "portrait.png", "output": "first.png"},
            {"id": "bad", "source": "source.png", "portrait": "portrait.png", "output": "second.png",
             "crop": [-1, 0, 100, 100]}]}))
        run = self.invoke("--manifest", manifest)
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse((self.root / "first.png").exists())
        self.assertFalse((self.root / "second.png").exists())

    def test_float_and_boolean_crops_are_rejected(self):
        for value in ([0.0, 0, 100, 100], [False, 0, 100, 100]):
            with self.subTest(value=value):
                manifest = self.root / "bad.json"
                manifest.write_text(json.dumps({"items": [{"id": "x", "source": "source.png",
                    "portrait": "portrait.png", "output": "no.png", "crop": value}]}))
                self.assertNotEqual(self.invoke("--manifest", manifest).returncode, 0)
                self.assertFalse((self.root / "no.png").exists())

    def test_overwriting_input_is_rejected(self):
        run = self.invoke("--source", self.source, "--portrait", self.portrait, "--output", self.source)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(sha(self.source), self.source_hash)

    def test_sidecar_cannot_overwrite_manifest(self):
        manifest = self.root / "comparison.json"
        manifest.write_text(json.dumps({"items": [{"id": "x", "source": "source.png",
            "portrait": "portrait.png", "output": "comparison.png"}]}))
        before = sha(manifest)
        run = self.invoke("--manifest", manifest)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(sha(manifest), before)
        self.assertFalse((self.root / "comparison.png").exists())

    def test_report_cannot_overwrite_an_input(self):
        manifest = self.root / "batch.json"
        manifest.write_text(json.dumps({"items": [{"id": "x", "source": "source.png",
            "portrait": "portrait.png", "output": "comparison.png"}]}))
        run = self.invoke("--manifest", manifest, "--report", "source.png")
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(sha(self.source), self.source_hash)

    def test_duplicate_ids_and_outputs_rejected(self):
        for second_id, second_output in (("same", "two.png"), ("other", "one.png")):
            with self.subTest(second_id=second_id, second_output=second_output):
                manifest = self.root / "batch.json"
                manifest.write_text(json.dumps({"items": [
                    {"id": "same", "source": "source.png", "portrait": "portrait.png", "output": "one.png"},
                    {"id": second_id, "source": "source.png", "portrait": "portrait.png", "output": second_output}]}))
                self.assertNotEqual(self.invoke("--manifest", manifest).returncode, 0)
                self.assertFalse((self.root / "one.png").exists())

    def test_invalid_font_does_not_silently_fallback(self):
        run = self.single("--font", self.root / "missing.ttf")
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse((self.root / "comparison.png").exists())

    def test_explicit_font_missing_chinese_glyphs_rejected(self):
        font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        if not font.exists():
            self.skipTest("DejaVu Sans fixture is not installed")
        run = self.single("--font", font, "--title", "秦始皇")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("glyph", run.stderr)

    def test_transparency_is_composited_on_neutral_background(self):
        Image.new("RGBA", (120, 120), (255, 0, 0, 0)).save(self.source)
        run = self.single("--panel-width", 120, "--panel-height", 120)
        self.assertEqual(run.returncode, 0, run.stderr)
        meta = json.loads((self.root / "comparison.json").read_text())
        box = meta["source"]["display"]["box_xyxy"]
        with Image.open(self.root / "comparison.png") as image:
            self.assertEqual(image.getpixel((box[0], box[1])), (247, 245, 240))

    def test_unreadable_input_fails_before_writing(self):
        self.source.write_text("not an image")
        run = self.single()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("Cannot decode", run.stderr)
        self.assertFalse((self.root / "comparison.png").exists())

    def test_save_failure_returns_nonzero_and_records_partial_completion(self):
        manifest = self.root / "batch.json"
        manifest.write_text(json.dumps({"items": [
            {"id": "bad", "source": "source.png", "portrait": "portrait.png", "output": "bad/result.png"},
            {"id": "good", "source": "source.png", "portrait": "portrait.png", "output": "good/result.png"}]}))
        spec = importlib.util.spec_from_file_location("hpr_compositor_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        actual_save = Image.Image.save

        def save_with_failure(image, file, *args, **kwargs):
            if Path(file).parent == self.root / "bad":
                raise OSError("simulated disk full")
            return actual_save(image, file, *args, **kwargs)

        with patch.object(Image.Image, "save", save_with_failure), redirect_stdout(io.StringIO()):
            code = module.main(["--manifest", str(manifest), "--panel-width", "120", "--panel-height", "120"])
        self.assertEqual(code, 1)
        report = json.loads((self.root / "batch_report.json").read_text())
        self.assertEqual(report["requested"], 2)
        self.assertEqual(report["completed"], 1)
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["items"][0]["status"], "failed")
        self.assertEqual(report["items"][1]["status"], "completed")
        self.assertFalse((self.root / "bad/result.png").exists())
        self.assertTrue((self.root / "good/result.png").exists())


if __name__ == "__main__":
    unittest.main()
