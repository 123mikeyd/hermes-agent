# Unsaved Blender scenes and source-pair Action auditions

## Safe inspection of an unsaved live scene on Windows

When Blender's title shows an unsaved scene, treat the open process as protected source. Do not press Save, replace the file, or build the cinematic in the live window.

1. Identify the Blender process ID from the live app/window.
2. Look for Blender's matching autosave in the configured temp directory, normally `<pid>_autosave.blend` (for example, `10420_autosave.blend`). Match the PID rather than choosing the newest unrelated `.blend`.
3. Open that autosave in a separate background Blender process and run a read-only inventory script. Record objects, armature bone lists, mesh-to-armature modifiers, packed textures, FPS, Action names/ranges, and hips/root displacement.
4. Build and save only a new versioned working `.blend`; leave the live unsaved process untouched.

Representative command shape:

```text
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b "C:/.../<pid>_autosave.blend" --python "C:/.../inspect_scene.py"
```

This is also a robust fallback when live-console automation is unnecessary: the autosave gives background Blender a deterministic file while preserving the user's foreground work.

## Source-pair-first audition gate

Marketplace and Meshy multi-clip imports commonly contain one armature+mesh pair per animation. Before selecting a canonical rig:

1. Preserve all imported pairs.
2. For each pair, hide every other imported rig and mesh.
3. Evaluate a representative frame from that pair's own assigned Action.
4. Render a labeled still using a consistent stage and camera language.
5. If the Action contains root travel, derive the camera target from the evaluated hips/root and apply the same relative camera offset so framing remains comparable.
6. Assemble a contact sheet and confirm the silhouettes are visibly distinct.

Only after this visual gate should Actions be assigned to a canonical rig and sequenced through NLA. Bone-name equality and numeric pose-signature differences verify compatibility/motion data, but they do not replace a rendered binding check. Compare the canonical-rig audition with the original-pair audition; if distinct source clips unexpectedly appear identical after transfer, stop and diagnose Action binding/evaluation instead of accepting the sheet or building the full video.

## Audition lighting

Use restrained emissive geometry and moderate area-light energy. Green stage lighting can clip pale hair and costume trim to mint-white, erase black clothing against a black world, and make background bars compete with the silhouette. Favor a tighter full-body camera, preserve head/hand clearance, and verify there is no accidental eye glow before asking for the artist's still approval.
