# Bambu and Orca notes

The MVP recognizes the layer marker commonly found in Bambu Studio and OrcaSlicer output:

```gcode
; layer num/total_layer_count: 112/120
```

Recognition of this comment is not equivalent to complete Bambu printer support.

## Current 3MF support

Layer Surgeon discovers Bambu/Orca-style members named `Metadata/plate_<number>.gcode` inside sliced `.3mf` or `.gcode.3mf` packages. This matches [Bambu Studio's upstream archive filename definition](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Format/bbs_3mf.hpp). A single plate is selected automatically; multi-plate packages require `--plate`.

This is filename-based discovery, not complete interpretation of Bambu package relationships or metadata.

## Current limits

Layer Surgeon does not yet model Bambu-specific start sequences, AMS/tool state, build-plate metadata, calibration routines, timelapse motion, firmware metadata, or all vendor-specific 3MF relationships. The `--profile` value is currently a report label; it does not activate a safety policy or adapter.

## Adapter requirements

A production Bambu adapter should:

- identify slicer and firmware assumptions from metadata;
- interpret plate G-code relationships and metadata inside 3MF containers;
- reconstruct machine, tool, temperature, fan, and extrusion state;
- classify commands that are unsafe when an existing part remains on the bed;
- account for printer-specific homing and motion behavior;
- retain vendor commands it does not transform;
- validate output using fixtures from documented slicer versions.

Until those requirements are implemented, Bambu recovery output requires expert review and supervised execution.
