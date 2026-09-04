# Background Mascot Flight Loops

Use this pattern for a small static mascot, drone, bee, fairy, or floating prop that should stay lively throughout a long Blender performance without competing with the hero.

## Validated construction

1. **Inspect before animating.** Record the mesh’s exact world transform, dimensions, parent, collections, existing Action/NLA state, and camera projection. Refuse to overwrite existing animation accidentally.
2. **Animate a root, not the mesh.** Create a dedicated Empty such as `Mascot_FlightRoot` at the artist’s anchor. Parent the mesh with identity parent inverse, zero local location, and preserved local rotation/scale. Keep the mesh and root in a named collection.
3. **Author one exact-endpoint loop.** A compact sideways figure-eight can use:
   - horizontal: `A * sin(theta)`;
   - vertical: `B * sin(2*theta)`;
   - bee/fly bob: a smaller higher-frequency sine;
   - depth flutter and bank: restrained additional sine channels.
   Key both the start and terminal frame to the same transform. The repeat interval is `action_end - action_start`, not the inclusive frame count. Dense linear samples are predictable and avoid automatic-handle surprises at the wrap.
4. **Repeat through NLA.** Protect the Action with Fake User, clear direct-Action conflicts, and use `ceil((scene_end-strip_start)/loop_interval)` repeats. Extend beyond the scene end rather than stopping one frame early.
5. **Fit without destructive rekeying.** If the path is correctly shaped but poorly framed, use a parent anchor or `delta_location` offset to move the whole flight envelope. Record that framing offset separately from the reusable Action.

## Camera validation

A motion that looks good in User Perspective can be absent from the actual render. Sample every camera beat and every repeated camera cycle.

- Project all eight corners of the evaluated render bounds with `world_to_camera_view`; an origin inside `0..1` does not prove the full mascot is visible.
- Require positive depth and a deliberate edge margin appropriate to the mascot’s projected size. A center at `x=0.99` is generally not a pass.
- Track NDC min/max, world-height range, and representative early/middle/late projections.
- Keep a full-frame coverage sheet to judge hierarchy and an enlarged mascot crop sheet to judge integrity, wall tangencies, and portrait/frame overlap.
- Treat overlap with important wall art as an art-direction choice. A tiny pass near a frame may add life; repeated coverage of a face or label needs restaging.

## Loop verification

- Compare the terminal pose with the start pose; require exact or negligible closure error.
- Inspect adjacent frames before, at, and after at least two NLA wraps.
- Compare wrap delta with ordinary within-loop frame deltas; a wrap should not be the motion spike.
- Prove nonzero motion at the final two scene frames.
- Render and encode one complete loop at the delivery frame rate. If music is already selected, mux the corresponding audio excerpt so motion energy can be judged in context. Verify the preview’s video frame count, FPS, duration, and audio stream with `ffprobe`.

## Proven failure and correction pattern

In one long music-video scene, a small floating mascot began at a reasonable world-space wall position and followed a valid six-second figure-eight, yet its projected center was inside the camera for only `9/301` sampled frames because the entire path sat above the shot. Applying a non-destructive framing offset, then resampling every repeated camera cycle, produced `301/301` in-frame centers. A second margin pass moved the maximum center projection from approximately `0.98` to `0.95`, leaving room for the wings and antenna. The Action itself remained unchanged and reusable.

## Delivery gate

Do not call the mascot complete from structural checks alone. Acceptance requires: protected reusable Action, exact loop closure, NLA coverage through scene end, late-scene motion, evaluated-bound camera margins, no hero-face obstruction, full-frame hierarchy review, enlarged crop review, and one rendered motion loop.
