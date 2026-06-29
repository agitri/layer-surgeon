# Bambu and Orca notes

The MVP recognizes the layer marker commonly found in Bambu Studio and OrcaSlicer output:

```gcode
; layer num/total_layer_count: 112/120
```

Recognition of this comment is not equivalent to complete Bambu printer support.

## Current limits

Layer Surgeon does not yet model Bambu-specific start sequences, AMS/tool state, build-plate detection, calibration routines, timelapse motion, firmware metadata, or 3MF archive structure. The `--profile` value is currently a report label; it does not activate a safety policy or adapter.

## Adapter requirements

A production Bambu adapter should:

- identify slicer and firmware assumptions from metadata;
- locate plate G-code safely inside 3MF containers;
- reconstruct machine, tool, temperature, fan, and extrusion state;
- classify commands that are unsafe when an existing part remains on the bed;
- account for printer-specific homing and motion behavior;
- retain vendor commands it does not transform;
- validate output using fixtures from documented slicer versions.

Until those requirements are implemented, Bambu recovery output requires expert review and supervised execution.
