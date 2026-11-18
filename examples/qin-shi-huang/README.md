# Qin Shi Huang example

This folder contains a source record, the generation-stage prompt, and a compositor manifest. Image binaries are **not bundled** in this release.

The British Library catalogue dates *Kosindo 高臣圖*, Or 11515, to **1800–1900**. The downloaded image metadata identifies **f.11v**. This is a later depiction, not a surviving Qin-period portrait. See [source.json](source.json) for URLs, hashes, crop coordinates, and qualified rights information.

## Reproduce the workflow

1. Open the [specific source-file page](https://commons.wikimedia.org/wiki/File:Qin_Shi_Huang.jpg), review its rights information, and obtain the original file if its use is suitable for your context. Save it as `inputs/qin_source.jpg` in this example folder. The recorded file is 1279 × 2000 pixels with SHA-256 `e959c3cc5d04d8eea387392d34a2d527c54dd2f66e16c88ef525d8d10a7b3ae7`. If the bytes or dimensions differ, check the file version before reusing the coordinates.
2. Crop the generation reference to `[160, 490, 1080, 1717]` in the original pixel coordinate system. Preserve the original file. Attach that crop to a reference-image-capable image generator and use [prompt.md](prompt.md).
3. Save the selected generated portrait as `inputs/qin_portrait.png`. Inspect it against the source before accepting it. New generations may differ from the original run.
4. From the repository root, run the compositor:

```bash
python skills/historical-portrait-reconstruction/scripts/compose_comparison.py \
  --manifest examples/qin-shi-huang/comparison.example.json
```

Paths inside the manifest are relative to the manifest file. The compositor applies the documented crop directly to the full source and emits `outputs/qin_comparison.png` plus provenance JSON. The manifest requires the two local input images; it is not a downloader or image generator.

5. Inspect the actual finished comparison. Confirm that the left panel is the acquired source crop and that the pose and visible features remain comparable. Do not label the result as a verified historical face.

## Rights and attribution

The Commons page displays a PD-Art / PD-old-100-expired declaration and a Public Domain Mark, while qualifying photographic reuse in other jurisdictions. Its embedded file metadata also contains a British Library Board copyright notice. This release records those statements without asserting worldwide clearance. MIT applies to the project’s own eligible material, not to this external scan.

Source attribution: British Library, *Kosindo 高臣圖*, Or 11515, f.11v; image obtained through the linked Commons file. Changes for comparison: rectangular crop and proportional resizing. The AI interpretation is separate and is not represented as a British Library work or endorsement.

## Sources

- [British Library catalogue](https://searcharchives.bl.uk/catalog/032-003315401)
- [Specific Commons file and rights statement](https://commons.wikimedia.org/wiki/File:Qin_Shi_Huang.jpg)
- [British Library terms](https://www.bl.uk/terms)

## 中文说明

本例公开来源、裁切坐标、提示词和拼图清单，不附图像。先核实并取得具体原图，再将真实裁切图传入生图工具；生成人像后继续拼接，最终交付“左原画、右写实转写”。这幅画像所属画册为 19 世纪资料，不能作为秦代真人写真。
