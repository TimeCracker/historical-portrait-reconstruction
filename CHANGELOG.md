# Changelog

## 0.1.0 — 2026-11-18

First public release structure, based on the earlier internal portrait workflow.

### Added

- A source-first historical portrait skill with person-specific facial observations.
- Mandatory authentic-source and photorealistic-interpretation comparisons.
- A portable Pillow compositor for individual images and manifest-driven batches.
- Input hashes, crop and scaling provenance, and batch status reporting.
- English and Chinese usage instructions.
- Metadata-only Qin Shi Huang and sixteen-person Ming examples.
- Deterministic compositor tests.

### Changed from the earlier internal workflow

- Preserve the reference pose by default instead of forcing a frontal view.
- Treat composition and final comparison review as part of completion.
- Record actual reference-image input and backend limitations.
- Keep third-party image rights separate from the license for original project code and documents.

### Scope

This release does not bundle image-model weights, a hosted generation service, third-party scans, fonts, or generated portrait binaries. It does not measure resemblance to a historical person.

