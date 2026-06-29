# Recovery model

Recovery means producing a new instruction stream that resumes an interrupted print from a known boundary. It does not repair physical displacement or prove that the remaining motion is collision-free.

## Current workflow

The `recover` command selects an exact layer marker, detects the first Z move associated with that layer and the first configured bed/nozzle temperatures, builds a preamble, then appends the original file from the marker onward.

Explicit temperature options override detected temperatures. Homing is excluded unless `--risk-allow-homing` is supplied.

Three artifacts are mandatory:

- Recovery G-code for inspection and, after operator review, execution.
- A unified diff exposing all removed and inserted lines.
- A Markdown report recording the target, detected state, and warnings.

## Assumptions in the MVP

- A recognized layer comment identifies a valid recovery boundary.
- The first Z word after that marker represents its layer height.
- The operator understands whether the printer still has valid position.
- The retained source suffix establishes any other state it requires.

These assumptions are not universally valid. State reconstruction and printer-specific policy are required before recovery can be considered robust.

## Minimum evidence for future recovery

A mature recovery pass should establish or explicitly mark unknown:

- active coordinate and extrusion modes;
- XYZ position and physical alignment;
- active tool and extrusion origin;
- bed, nozzle, chamber, and fan state;
- mesh/leveling and coordinate offsets;
- safe approach path and clearance from the existing part;
- slicer and firmware dialect;
- integrity and provenance of the source file.

Unknown safety-critical state should result in a refusal or a clearly classified high-risk output, according to documented policy.
