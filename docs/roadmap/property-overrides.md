# CSS Property Override Roadmap

This document tracks the future work required to support adding/removing arbitrary CSS properties (beyond colour overrides) when patching Unity StyleSheets.

## Goals

- Allow skin authors to add new declarations (e.g. `height`, `width`, layout properties) to existing selectors.
- Support removal or replacement of existing declarations (such as the built-in `color` values on attribute classes).
- Maintain compatibility with current colour-only overrides and mapping behaviour.

## Implementation Plan

1. **Parsing layer**
   - Extend the CSS ingestion helpers to capture arbitrary declaration blocks, not just colour hex values.
   - Record the raw property names, values, and any metadata needed to recognise remove/replace directives.
   - Persist these extra declarations alongside the existing colour overrides in `CssFileOverrides`.

2. **Value normalisation**
   - Introduce converters that translate CSS tokens into Unity StyleSheet value types (floats, enums/keywords, resource paths, etc.).
   - Handle unit parsing (px, %, em) and boolean keywords.
   - Define syntax for removals (e.g. `!remove`) and explicit overrides to disambiguate from additive declarations.

3. **Data model updates**
   - Expand `CollectedCss` to carry per-selector/per-property add/replace/remove payloads in addition to colour data.
   - Preserve backward compatibility: legacy skins that only supply colours should continue to work with no changes.

4. **CssPatcher enhancements**
   - Teach `_apply_patches_to_stylesheet` to create or update entries in the Unity arrays (`strings`, `floats`, `m_Properties`, etc.) for non-colour values.
   - Implement property removal by pruning the relevant `m_Properties` entries and cleaning up unused array slots when safe.
   - Ensure new values allocate indices correctly and update all references to avoid corrupting the asset.

5. **Scan cache & targeting**
   - Update scan cache generation to track the wider property set so filtering, dry-run summaries, and targeting hints stay accurate.
   - Adjust cache versioning to invalidate old entries when the schema changes.

6. **User experience & docs**
   - Document the new syntax, including examples for add/replace/remove behaviour.
   - Provide validation warnings for unsupported or ambiguous values to keep patch runs predictable.
   - Consider feature flags or config toggles if we want a staged rollout.

7. **Testing strategy**
   - Add focused unit tests covering add/replace/remove paths for multiple property types (colours, lengths, resource references).
   - Include integration tests that round-trip actual bundles to confirm Unity can load the patched assets.
   - Add regression tests to guarantee colour-only skins behave exactly as before.

## Status

- Colour overrides (hex/rgb/rgba) are already supported and normalised.
- Arbitrary property manipulation remains future work; this document captures the agreed roadmap for when we tackle it.
