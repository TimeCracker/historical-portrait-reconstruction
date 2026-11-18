# Contributing

Contributions can improve source records, portrait review, client instructions, or deterministic tooling.

## Source and portrait contributions

For a new case, include:

1. A public source page, object identifier when available, artwork date, identity basis, and source lineage.
2. The exact acquired file's rights statement, retrieval date, and hash when the file was actually acquired.
3. Visible facial features and uncertain details recorded separately.
4. The prompt and whether the reference image was actually supplied to the generation tool.
5. One final comparison per person, with the authentic source panel placed mechanically.
6. A concise review of fidelity to the painting and the limits of historical likeness.

Submit source metadata first when image redistribution has not been checked. Do not attach images merely because the artwork is old or a copy appears online. Preserve third-party attribution, applicable notices, and modification records.

A visual improvement must not rely on invented anatomy, a celebrity face, or another person's generated portrait. Differences across people should follow the source evidence.

## Code changes

Keep the compositor independent of any image-generation vendor. Preserve source bytes, validate inputs before rendering, use proportional scaling, and report partial batches honestly.

Run:

```bash
python -m unittest discover -s tests -v
```

Add or change a test when a code change affects a concrete invariant such as cropping, input preservation, provenance, or batch accounting. Use synthetic images for deterministic tests so the test suite does not depend on external image rights or a paid service.

Do not commit credentials, signed download links, private absolute paths, client file identifiers, generated temporary outputs, or unrelated working files.

## Documentation changes

State the client and date for installation instructions. Distinguish a documented import path from an environment actually tested end to end. Do not add unsupported likeness scores or universal compatibility claims.

## Pull request description

Explain the problem, the changed behavior, and the checks performed. For source corrections, link the primary catalog or other evidence. For image examples, state the applicable rights and transformations.

Original code and documentation contributions are submitted under this repository's MIT license, to the extent the contributor can grant those rights. Third-party material retains its own terms.

