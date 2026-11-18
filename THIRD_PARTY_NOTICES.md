# Third-party notices

## Scope of the repository license

The root [MIT License](LICENSE) covers original skill instructions, scripts, and repository documentation to the extent the contributors can license them. It does not relicense third-party source images, fonts, dependencies, or externally generated material.

## Historical image references

The initial release includes source records and links for the Qin Shi Huang and Ming examples. It does **not** bundle historical scans, cropped references, generated portraits, or comparison-image binaries.

Image metadata describes the source and its recorded rights information; it is not a blanket permission to redistribute every copy of an artwork. The rights of a particular acquired image must be checked against its actual file page and institutional terms. When notices conflict or the applicable image version is unclear, the example records that uncertainty.

- [Qin Shi Huang source record](examples/qin-shi-huang/source.json)
- [Ming source records](examples/ming-portraits/sources.json)

Any future bundled image must have a per-file provenance and rights record, including applicable attribution, license link, and changes such as cropping or resizing. It must not imply institutional endorsement of an AI interpretation.

## README banner

The left panel of each pair shows a detail of a painting in the National Palace Museum, Taipei. The right panels reuse previously generated interpretations.

| Subject | Painting | Accession | Full image |
| --- | --- | --- | --- |
| Li Shimin | [唐太宗立像（一）](https://digitalarchive.npm.gov.tw/Collection/Detail/1825?dep=P) | 中畫000263N000000000 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:TangTaizong.jpg) |
| Zhao Kuangyin | [宋太祖坐像](https://digitalarchive.npm.gov.tw/Collection/Detail/1864?dep=P) | 中畫000302N000000000 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Song_Taizu.jpg) |
| Zhu Yuanzhang | [明太祖坐像（七）](https://digitalarchive.npm.gov.tw/Collection/Detail/1873?dep=P) | 中畫000311N000000000 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Portrait_assis_de_l%27empereur_Ming_Taizu.jpg) |

Wikimedia Commons marks the source scans as faithful public-domain reproductions. The banner crops and proportionally resizes the scans, including the source panel from the earlier Zhu Yuanzhang comparison. The artwork, scan rights, crop coordinates, and image hashes are documented in [banner-sources.json](assets/banner-sources.json). The banner is a project illustration. The MIT license applies to the repository material described above.

## Pillow

The compositor depends on [Pillow](https://python-pillow.org/), installed separately through the dependency specification. Pillow is licensed under **MIT-CMU**, as stated in its [official documentation](https://pillow.readthedocs.io/en/stable/about.html#license). The Pillow package retains its own license and notices. Its source code and binary distributions are not vendored here.

## Fonts

No fonts are bundled. The compositor can use an installed font or a path supplied by the user. A font's own license remains applicable if someone redistributes it with a derived package.

## Image-generation services and outputs

The skill invokes capabilities provided by its host environment; no service credentials or model weights are included. An image-generation service and its outputs may have terms separate from this repository's MIT license. This repository makes no general claim that AI outputs are either copyrighted or public domain in every jurisdiction.

