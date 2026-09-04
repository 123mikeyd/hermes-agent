# Same-character multi-import dance consolidation

Use this workflow when a marketplace or animation bridge imports the same skinned character once per dance, leaving several visible copies—often overlapping the hero—while the artist has deliberately placed one instance in the intended lineup or side-stage slot.

## Acceptance target

- One authoritative visible rig+mesh at the artist's chosen transform.
- Every distinct imported dance preserved as a protected canonical Action.
- An editable NLA presentation that covers the intended scene range and remains animated late in the shot.
- Redundant imports hidden as recoverable source carriers, not silently deleted.
- Source-pair, pose-equivalence, transition, and camera-framing evidence kept separate.

## 1. Protect and inventory the live scene

If the live Blender file is dirty, preserve the unsaved imports before background processing. Prefer a matching autosave or `Save Copy…`. When GUI Save Copy is unavailable but the live scene must be captured, a validated fallback is:

1. Copy the last saved `.blend` byte-for-byte to an explicit `BEFORE_IMPORTS` backup and verify the two hashes match.
2. Save the dirty live Blender scene to its current path.
3. Perform all consolidation in a new versioned derivative, never in the just-captured live file.

Diff the before/after inventories. Record every new armature, mesh, assigned Action, native frame range, parent/modifier target, object transform, materials, collections, and hide state. Do not classify duplicates from similar names alone.

## 2. Choose the canonical performer from art direction

The canonical instance is the one the artist deliberately positioned for the shot. Preserve its exact world location, rotation, and scale. Do not choose a different import merely because it has the first or cleanest datablock name.

Before consolidation, render a labeled representative still from every native rig+mesh pair in a neutral studio. Confirm:

- the same character identity and materials;
- normal hands, sleeves, shoulders, knees, and silhouette;
- visibly distinct candidate poses;
- no obvious source-side deformation.

A still proves binding and identity, not full-clip uniqueness. Also sample deterministic normalized pose signatures over each native range.

## 3. Gate direct Action reuse with exact compatibility

Equal bone counts or names are not enough. Compare, in order:

- bone names and hierarchy;
- complete local rest matrices (therefore directions and rolls);
- armature object scale and orientation;
- Action slot target type in Blender 5.2.

Only when the complete rest signature matches may the imported Actions be directly reused on the selected rig. Otherwise retarget and bake target-specific Actions.

Duplicate each accepted source Action rather than renaming or editing it. Give the copy a stable performer-scoped name, enable Fake User, and store source Action/rig identifiers as custom properties or in an embedded JSON catalog.

After saving and reopening, evaluate each canonical copy and its source at start/mid/end. Their local pose vectors should match exactly (or within a declared numerical tolerance). If the original canonical object was renamed, its old import name no longer exists; compare its source and copied Actions sequentially on the renamed rig rather than trying to look up the obsolete object name.

## 4. Preserve placement with a lineup root

Create a persistent Empty at the artist's chosen transform. Parent the retained rig with:

- root at the intended world location/rotation;
- `matrix_parent_inverse` set to identity;
- rig local location and rotation reset to identity;
- original rig local scale preserved.

Verify the evaluated world bounds before and after parenting. This isolates lineup placement from body motion and makes later staging changes reversible.

## 5. Build an editable multi-Action playlist

Clear direct-Action/NLA conflicts on the retained rig, then create single-pass NLA strips for the protected canonical Actions.

- Use the native interval `action_end - action_start`; do not treat inclusive frame count as repeat length.
- In Blender 5.2, `NlaStrips.new(..., start, action)` requires an integer `start`; cast or round explicitly.
- Set `use_auto_blend = False` before assigning explicit blend lengths.
- Put strips on ascending tracks with `extrapolation='NOTHING'` and intentional overlaps (for example, 12 frames at 30 FPS), then read the values back after saving.
- Do not directly loop a clip whose end→start pose delta exceeds ordinary within-clip motion. It may still appear once in a playlist and transition to a different clip through a reviewed crossfade.
- Continue the playlist through or beyond the hero's end frame when the side performer should dance for the full shot.

A separate track per strip is verbose but deterministic for short presentation playlists and makes transition order obvious during verification.

## 6. Hide, do not destroy, redundant imports

Move every noncanonical rig+mesh pair into a clearly named source-carrier collection. Hide both viewport and render visibility, preserve each native Action with Fake User, and record that the dance was consolidated. Do not leave duplicate performers at world origin, below the floor, or just outside the camera.

## 7. Fresh-reopen verification

Require all of the following from the exact saved derivative:

- one visible canonical rig+mesh and the expected lineup-root transform;
- all redundant rig+mesh pairs hidden in the source-carrier collection;
- expected protected Action set and native ranges;
- source/canonical pose RMS within tolerance at representative frames;
- complete NLA strip count, no timeline gaps, intentional overlap length, and coverage beyond scene end;
- nonzero late-scene pose delta;
- adjacent before/after renders at every first-cycle transition and playlist wrap;
- no bind-pose flash, teleport, severe snap, deformation, or hero overlap.

Render an action-coverage sheet from the actual shot camera. A side performer can pass structural consolidation while failing camera coverage. A glove or narrow body fragment at the frame edge is not readable presence. Preserve the artist's approved placement and treat camera widening/retargeting as a separate decision unless the artist explicitly asks to move the performer.

Finally, open exactly one authoritative preview in a 3D View at the intended review frame. If a live-save operation captured the Layout workspace in Python Console mode, restore only the affected Layout area; do not globally replace Console areas in unrelated workspaces.