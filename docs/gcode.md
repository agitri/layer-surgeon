# G-code handling

G-code is a family of dialects rather than one complete, universal language. Firmware and slicers attach different semantics to commands, comments, metadata, and defaults.

## Preservation rule

Layer Surgeon preserves original text from the selected recovery boundary onward. Unknown commands and comments must remain intact unless the user selects a named transformation that explicitly changes them.

## Currently recognized markers

The parser accepts these layer comment shapes case-insensitively:

```gcode
; layer num/total_layer_count: 112/120
;LAYER:112
; layer 112
```

The broad final pattern requires careful regression coverage because free-form comments can resemble layer markers.

## Current state extraction

The MVP extracts:

- the first `M140`/`M190` bed temperature;
- the first `M104`/`M109` nozzle temperature;
- the first `Z` word found after each recognized layer marker.

This is lexical extraction, not complete machine-state interpretation. It does not yet account for units, relative positioning, command ordering, tool changes, offsets, or firmware-specific semantics.

## 3MF input

[The 3MF Core Specification](https://github.com/3MFConsortium/spec_core/blob/master/3MF%20Core%20Specification.md) defines 3MF documents as ZIP-based OPC packages, but embedded G-code is a slicer/vendor extension rather than a guarantee of the core model format. Layer Surgeon validates basic package structure and searches for `.gcode` members without extracting archive contents to disk.

When one candidate exists, it is selected automatically. For multiple candidates, `--plate` selects a member whose name ends in `plate_<number>.gcode`. Ambiguous archives are rejected instead of choosing by archive order.

Archive member path, plate number, and container filename are retained as provenance in the recovery diff and report. Encrypted members, unsafe paths, unsupported compression, excessive uncompressed size, and suspicious compression ratios are rejected.

## Parsing direction

Future parsing should produce a lossless intermediate representation with:

- original source text and line provenance;
- command, parameters, comments, and dialect metadata;
- reconstructed machine state before and after each command;
- layer and feature boundaries;
- diagnostics for ambiguous or unsupported syntax.

Rendering an unchanged representation must reproduce the original bytes wherever encoding permits.
