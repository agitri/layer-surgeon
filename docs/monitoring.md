# Printer Monitoring and Incident Reconstruction

This document describes a planned feature. No printer monitoring is implemented yet.

## Objective

Layer Surgeon should act as a read-only flight recorder during a print. If a print stops or fails, it should preserve the available evidence and map that evidence back to the source G-code.

## Recorded evidence

Depending on printer capabilities, a monitoring session can record:

- job identifier, file identity, and source digest;
- printer model, firmware, and adapter version;
- timestamps and printer-state transitions;
- progress, current layer, Z height, and estimated time;
- nozzle and bed temperatures and targets;
- fan, flow, and speed values;
- active tool, filament system, or material slot;
- firmware warnings and error codes;
- reported file position or last acknowledged command;
- optional camera snapshots.

Events should be stored append-only so the incident history remains auditable.

## Initial adapters

- **Bambu MQTT:** consume available local status reports. Treat fields as firmware-dependent because the public integration surface is limited.
- **PrusaLink:** poll or subscribe to the local job, printer, error, and camera interfaces exposed by supported printers.
- **OctoPrint:** consume job events, current Z, temperatures, serial messages, and file position when known.
- **Moonraker:** consume Klipper object updates and job state through its event interface.

Adapters normalize observations into one telemetry model without pretending all printers expose the same evidence.

## Source correlation

Correlation proceeds from strongest to weakest evidence:

1. A host-reported file position or acknowledged command maps directly to a source range.
2. A printer-reported layer maps to the matching layer marker.
3. A Z height maps to candidate layers, accounting for variable layer height.
4. Percentage and elapsed-time estimates identify only a broad range.

The report must state the method and confidence. Firmware buffers commands ahead of physical motion, so even a last acknowledged command is not proof of the nozzle's exact position when failure occurred.

## Failure detection limits

Firmware-detected failures—such as thermal faults, filament runout, or explicit crashes—can produce a precise timestamp and error. Mechanical failures such as detachment, layer shifts, or spaghetti may not change printer state at all. Those require an operator marker, external sensor, or camera analysis.

Camera inference is advisory evidence. Deterministic telemetry and source correlation remain separate from AI or computer-vision conclusions.

## Incident report

A report should contain:

- monitoring-session and source identities;
- last healthy and first abnormal observations;
- reported errors and state transitions;
- likely layer, Z height, and source range;
- correlation method and confidence;
- missing or contradictory evidence;
- a recommended recovery boundary for operator review.

Monitoring is read-only by default. Pausing, stopping, or otherwise controlling a printer is a separate capability requiring explicit authorization and safety policy.
