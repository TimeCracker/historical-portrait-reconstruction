# Sixteen Ming emperors: batch example

This folder contains 16 source records, 16 person-specific prompts, and a batch compositor manifest. It contains **no source or generated image binaries**.

Scope: Hongwu through Chongzhen. Southern Ming rulers are outside this example. Zhengtong and Tianshun are two reign titles of the same person and occupy one record. This example’s count does not impose a batch limit on the Skill or compositor.

## Contents

- [sources.json](sources.json): source links, accession records where available, original byte hashes, distinct generation and comparison crops, limitations, and rights-review status.
- [prompts/](prompts/): generation-stage prompts; the selected Chenghua beard revision is preserved.
- [batch.example.json](batch.example.json): 16 expected outputs with paths relative to the manifest.

The records were imported from a previous completed workflow. Source byte hashes were checked on 2026-11-18. The release does not claim that all catalogue statements or image licences were independently reviewed again.

## Reproduce

1. Review each source record and the exact file’s reuse conditions. Obtain suitable source files; use the `input_filenames.source` paths in `sources.json`. If a downloaded file differs from the recorded hash or dimensions, resolve that difference before applying the crop.
2. Prepare each person’s generation reference using `generation_crop_xyxy`. Hongwu’s reference was additionally resized proportionally to 900 × 1200. Do not transfer a different person’s face or reference between runs.
3. For each person, supply the real reference image to a suitable generator with the corresponding prompt. Save the reviewed result at `input_filenames.portrait`. These prompts create the right-hand portrait only; they do not satisfy the final side-by-side delivery requirement.
4. From the repository root, run:

```bash
python skills/historical-portrait-reconstruction/scripts/compose_comparison.py \
  --manifest examples/ming-portraits/batch.example.json \
  --font /path/to/a/CJK-font.ttf
```

Replace the font argument with an existing CJK-capable font on your machine. A known installed CJK font may be detected by the compositor; providing it explicitly makes the run easier to reproduce. The manifest intentionally contains Chinese names and captions.

5. Review each comparison. The source and generated portrait must be paired by person; record all 16 completed outputs and any failures. The manifest requires local input files and does not download or generate images.

## Evidence limitations

| Records | How to describe the source |
| --- | --- |
| 13 portraits with National Palace Museum collection records | Museum-held paintings; provenance does not itself verify lifetime sitting or exact resemblance |
| Jianwen and Jingtai | Later attributed depictions with unresolved original provenance; keep attribution uncertainty explicit |
| Chongzhen | A later printed illustration recorded as a 1907 edition, not a lifetime portrait |

The earlier Zhengtong comparison uses a tighter display crop than the generation reference; both coordinates are retained. This is an explicitly recorded layout choice, not retouching of the source face.

The repository does not apply MIT to external scans, newspaper illustrations, or generated image files. Verify each exact asset before redistribution; the linked museum page alone is not a licence for every copy found elsewhere.

## 中文说明

本例包含明朝十六帝的逐人来源、提示词和批量拼图清单，不附图像。建文、景泰及崇祯所用材料的时代和归属局限单列。正统、天顺合为同一人。每人独立取得原画、生成和检查后，再交付并排对照；16 人只是本例范围，不是工具上限。
