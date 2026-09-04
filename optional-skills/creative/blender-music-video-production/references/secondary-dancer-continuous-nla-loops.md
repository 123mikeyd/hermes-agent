# Continuous NLA loops for secondary dancers

Use this when an artist adds a fully rigged backup performer to a live dance scene and wants that performer’s current native dance to repeat until the hero finishes.

## Protect the artist’s live placement

1. If the Blender title is dirty, save the live scene before inspecting it in a background process. The newly imported rig, mesh, Action, and hand-adjusted placement may exist only in that window.
2. Inventory the actual armature, skinned mesh, Armature-modifier target, assigned Action, Action range, object transforms, NLA tracks, visibility, and scene end. Do not identify the performer from generic importer names; store the artist-provided display name in custom properties.
3. Keep the performer on its own native rig and Action when that pair already evaluates correctly. Do not retarget a working backup dance onto the hero merely to simplify sequencing.

## Prove the Action can repeat

1. Evaluate every native Action frame on the performer’s own rig and compute ordinary adjacent-frame pose deltas.
2. Compare the last pose to the first. A viable unmodified loop has an endpoint delta inside the ordinary motion envelope; a boundary larger than normal requires a protected loop-fixed derivative, a safer trim, or artist review.
3. Inspect hips/root displacement in world units. Armature object scale matters: a numerically large pose-space translation can represent only a small world-space shift.
4. Preserve exact Action endpoints. The cycle length is `action_end - action_start` frame intervals, not the inclusive frame count.

## Build the continuous NLA strip

1. Duplicate the imported Action to a semantically named protected source such as `<Performer>_<Dance>_LoopSource`; enable Fake User and retain the original Action unchanged.
2. Clear the armature’s direct Action assignment so it does not compete with NLA. Remove or deliberately mute stale imported tracks rather than stacking another strip blindly.
3. Create one unmuted NLA track and one strip starting at the scene start. Set exact `action_frame_start` and `action_frame_end`, zero blend-in/out, and `extrapolation='NOTHING'`.
4. Compute coverage as:

   `repeat = ceil((scene_end - scene_start) / (action_end - action_start))`

   It is acceptable for the strip to end after the scene; it must not end before the hero.
5. Keep the user’s armature location, rotation, scale, mesh binding, and materials unchanged unless the artist separately approves staging changes.

## Fresh-reopen verification

After saving a versioned successor, evaluate the real NLA result—not only strip metadata:

- direct Action is `None` and exactly the intended track is unmuted;
- strip Action, native range, repeat count, and end cover the scene;
- every predicted repeat boundary has a pose delta no larger than the ordinary adjacent-motion maximum;
- a late pair such as `scene_end-64 → scene_end-63` has nonzero pose motion;
- performer mesh and rig remain visible/renderable and the deformed mesh does not penetrate the stage;
- camera-space bounds intersect the frame at early, middle, late, and repeat-boundary samples;
- the artist’s saved placement transforms are unchanged.

A performer can technically loop while being clipped by a hero-tracking camera. Report small edge grazing honestly and do not silently move a user-placed actor; offer a lineup-root or camera adjustment as a separate staging decision.

## Validated example

A native Action spanning frames `1–124` has `123` frame intervals. In a scene ending at frame `4064`, `34` repeats extend the NLA strip to frame `4183`, covering the full hero performance. In the validated scene, all 33 in-scene wrap deltas stayed below the maximum ordinary adjacent-frame delta, and motion remained nonzero after frame 4000.
