---
name: historical-portrait-reconstruction
description: >-
  Reinterpret historical portraits as source-grounded photorealistic people.
  Use for historical-person face reconstruction, painting-to-photo conversion,
  emperor portrait batches, original-versus-reconstruction comparisons, or
  reviewing same-face failures. Verify and inspect authentic source paintings,
  preserve person-specific visible features, and always deliver an authentic
  original image beside the generated interpretation with traceable provenance.
---

# Historical Portrait Reconstruction

Turn a verified reference painting into a photorealistic interpretation.
Treat resemblance to a painting and resemblance to the historical person as
separate questions. Never report an unverified real-person likeness score.

## Required final output

For each requested person, deliver **one selected comparison board: authentic
reference on the left, generated interpretation on the right**. Label both
panels and identify the source and its limitations.

- Build the board from two actual image files with the bundled compositor.
  Never ask the image model to recreate the left-hand "original".
- Keep the source file unchanged. Allow only recorded crops and proportional
  resizing in the display panel; keep labels outside image content.
- Preserve the source pose, visible facial proportions, and apparent age by
  default. Treat requested frontalization or age changes as extra inference.
- Generate each identity independently. Share presentation settings, not faces.
- Complete every requested identity. Chunk work to fit actual tool capacity
  and continue; do not invent a ten-image limit or stop at the first image.
- If the host automatically displays a generated image, continue to compose
  and deliver the final paired board. A standalone generation is intermediate.
- If source access or generation is blocked, report the exact unresolved item.
  Never fabricate a painting, substitute another person, or label partial work
  complete. Continue independently executable items.

## 1. Resolve scope and capability

Infer person names and task scope from the current request and prior corrections.
Ask only when identity or scope remains materially ambiguous.

For batches, record one stable ID per distinct person, expected names, chosen
source, generation state, comparison state, review state, and blocker.
Deduplicate one person who has multiple reign titles without silently dropping
separate requested people.

Confirm access to a source viewer, an image generator that accepts reference
images, and an image compositor. Do not imply that installing this Skill grants
an image-generation service or a particular API.

Read [the generation contract](references/generation-contract.md) before
generation. Read [source policy](references/source-policy.md) when selecting
evidence or publishing third-party material.

## 2. Select and inspect the actual source

Prefer a museum or research collection record, then a traceable reproduction.
Follow the source chain rather than counting copies as independent evidence.
Record the work's date separately from the subject's lifetime and distinguish
contemporary portraiture, later copies, narrative paintings, and later
imaginary depictions.

Open the actual image and inspect its face before using it. Record which
visible person or crop is the reference. Never infer facial details from a
catalogue description without viewing the image.

Store source page, institution, accession, attribution, date, provenance,
download provenance, file hash, image dimensions, crop coordinates, and
uncertainties. Use [the source record template](references/source-manifest.example.json).
Record image rights separately from evidential value.

If no usable original is available, do not fabricate one. Complete source
research and explain the gap; offer a clearly identified speculative portrait
only when that fits the user's requested scope.

## 3. Build a person-specific feature contract

Record the following before calling the generator:

- **LOCK:** observable face outline, cheek/jaw shape, relative eye spacing,
  lids, brow direction, nose shape, mouth position, beard growth and outline,
  pose, and visible asymmetries. Describe specific relations, not vague praise.
- **SOFT:** visibly ambiguous details or qualified documentary evidence.
- **UNKNOWN:** obscured or unreadable anatomy, skin microtexture and unpainted
  depth. Fill conservatively without presenting additions as historical facts.
- **FORBID:** another person's reference, prior AI faces used as primary
  evidence, celebrity templates, beautification, invented scars, or arbitrary
  changes made only to make the subjects look different.

Track clothing and facial evidence separately. Do not translate personality,
physiognomic rhetoric, ethnicity, or an honorific into invented anatomy.
Use reliable historical text for limited, explicit adjustments; cite the
specific passage and keep competing source interpretations visible.

Do not force differences that the sources do not support. Do not claim
quantitative measurements unless marked points and calculations exist.
Two-dimensional painting ratios are not three-dimensional anatomy.

## 4. Generate from the reference image

Supply the verified image or its recorded crop through the host's real
reference-image input. Follow the host's image-tool instructions for local
paths, attachments, output handling, and supported operations.

Convert the depicted person into plausible human skin, hair and lighting
while keeping the visible identity features and pose. Avoid generic
"handsome emperor", cinematic hero, or symmetrical model-face instructions.

Use one primary facial source for one person. If several sources disagree,
select and explain a primary source; do not silently average distinct faces.

If a generator cannot accept reference images, label any permitted text-only
result as text-conditioned speculation. Do not claim image-conditioned
conversion, pixel locking, or identity preservation that the call did not use.

Review the result before accepting it. Regenerate a failed person from the
authentic source and the feature contract, not from another generated face.
Keep one selected version for final delivery unless alternatives were requested.

## 5. Compose the comparison mechanically

Run the installed copy of `scripts/compose_comparison.py`; resolve its path
relative to this Skill's directory, not the caller's working directory.

The script uses Python 3.11+ and Pillow 13.x. Install dependencies only through
the host's approved workflow. Pass a suitable font for Chinese labels; do not
silently drop unreadable characters.

Single-person pattern (replace every placeholder with a real path):

```bash
python /path/to/this-skill/scripts/compose_comparison.py \
  --source /path/to/authentic-source.jpg \
  --portrait /path/to/generated-portrait.png \
  --output /path/to/person-comparison.png \
  --title "Person name" \
  --caption "Collection, accession; source date and limitation" \
  --crop 100 200 900 1300
```

Omit `--crop` to use the full source. Crop coordinates are integer
`left top right bottom` boundaries in the loaded image, with right/bottom
exclusive; check the script's actual metadata for the applied transform.
Never guess the example's coordinates for a different image.

For batches, use `--manifest /path/to/comparisons.json`. The manifest has
an `items` array; each item supplies `id`, `source`, `portrait`,
`output` and optional title/caption/crop. Relative file paths resolve from
the manifest's directory. See [the batch template](references/comparison-batch.example.json).

Retain the PNG and its JSON provenance. Image creation success does not replace
visual review or prove historical likeness.

## 6. Review, repair, and finish

Read [quality review](references/quality-review.md) and inspect the actual
finished board at a useful face size.

Confirm source identity, source-panel authenticity, visible facial fidelity,
pose, readable labels, and source limitations. Compare generated faces across
people for reused geometry; clothing differences alone do not establish
distinct identities.

Correct concrete failures and inspect the corrected board. If the available
evidence cannot distinguish the faces, say so rather than inventing features.

For a batch, compare the final IDs to the original expected IDs. Distinguish
generated, composed, reviewed, and blocked states. Deliver all reviewed
individual boards; an overview sheet is additional, not a substitute.

Briefly report the main source, visible retained features, and inference limits.
Describe these as **source-grounded photorealistic interpretations**. Keep
source uncertainty separate from generation fidelity.
