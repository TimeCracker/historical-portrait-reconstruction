# Generation contract

## Capability and input

Use the host's supported image-generation/editing tool. Check its current
instructions rather than inventing provider endpoints or switches. This Skill
does not ship a generation API, credentials, model weights or a paid service.

Before editing a local reference, inspect it with the host's image viewer.
Pass the actual file/attachment using the tool's reference-image mechanism.
Record whether reference pixels were supplied, the crop and prompt, and the
model identifier only if the tool actually exposes it.

Do not confuse a text description of a painting with image conditioning.
Do not advertise an untested provider as supported. Retain output using the
host's documented procedure; do not expose private task paths or account IDs
in public provenance.

If a host auto-displays the generated right panel, treat that display as an
intermediate result and continue immediately to the mechanically composed
paired deliverable. Follow the host's display requirements without dropping
the final comparison.

## Prompt pattern

Replace the bracketed entries using inspected evidence; placeholders are not
claims about any particular historical person.

"Use the supplied authentic painting crop as the facial reference for
[person/source]. Create one photorealistic interpretation of the depicted
person. Keep [visible head outline], [brow and eyelid relations], [nose and
mouth relations], [beard origin and contour], [visible asymmetry], and the
source's [pose]. Translate paint into plausible skin, hair and soft natural
lighting without redesigning these visible proportions. Preserve the apparent
age and source costume unless a separately documented adjustment is requested.
Treat [unreadable/occluded details] as uncertain. Do not use a celebrity,
another person's face, a stock emperor face, beauty retouching, or invented
scars. Output only the right-hand portrait. The genuine source panel and
labels will be composed separately."

Use concrete person-specific features. A common studio style is acceptable;
a common facial template is not. Do not direct unsupported identity changes
merely to reduce pairwise similarity.

## History and reproducibility

Record the full prompt, actual input hash, generation date when known,
reference-input status and selected output hash. Model output can vary between
calls and versions; exact pixel reproduction is not promised.

Use documentary adjustments only when verified and explicit. Normal skin
texture or a plausible hidden surface is artistic completion, not a discovery
about the sitter.

If no usable generation backend is available, finish the evidence and prompt
artifacts and identify generation as blocked. Never substitute procedural
drawing, a relabelled previous image or another person's face.

