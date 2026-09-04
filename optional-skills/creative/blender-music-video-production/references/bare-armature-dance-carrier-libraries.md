# Bare-armature dance carrier libraries

Use this pattern when an import session yields one skinned character clip and many animation-only armatures. The goal is a trustworthy motion library, not a scene full of duplicate meshes.

## Why carriers should remain unskinned initially

A mesh does not need to be duplicated for every Action. The raw armature+Action pair is a valid preservation carrier, provided the Action has a real user or Fake User and the `.blend` is saved. Directly reusing the one character mesh is unsafe until compatibility is proven: identical bone names and counts can coexist with different rest matrices, bone directions, or rolls, causing collapsed shoulders, lateral arm swings, or other deformation.

When rest transforms differ, preserve the raw carrier and later retarget and bake a target-specific Action onto the canonical skinned rig. This uses one authoritative mesh while keeping every source motion recoverable.

## Protected-source workflow

1. If the live Blender title is dirty, locate the autosave that matches the live Blender PID and inspect it in a separate background process. Never overwrite or change the filepath of the live scene.
2. Identify the only mesh, its parent armature, Armature-modifier target, material images, packed state, and assigned Action. Treat the artist’s statement about which move it contains as authoritative; do not infer dance names from duration or pose samples.
3. Inventory all armatures and Actions. Record FPS, native frame ranges, object transforms, ordered bone names, hierarchy, and full rest matrices.
4. Compare each carrier against the skinned canonical rig. Store bone-name compatibility and rest-transform compatibility as separate fields.
5. Keep the canonical mesh+rig visible. Move bare carriers into a hidden collection such as `RAW_DANCE_CARRIERS`; hide them from render but do not delete them.
6. Enable Fake User on every Action. For generic source names such as repeated `mixamo.com` variants, assign reversible catalog labels (`Dance_Raw_01`, `Dance_Raw_02`, …) and preserve original Action/rig names in custom properties.
7. Embed a Markdown catalog in a Blender Text datablock and write a CSV or JSON sidecar. Include catalog label, original names, carrier name, frame range, duration derived from scene FPS, skin presence, bone-name match, rest match, and workflow status.
8. Save only to a new versioned `.blend`.

## Audition limitation and next gate

The usual original-pair audition is impossible for a bare armature because there is no source mesh to render. Do not disguise this limitation by temporarily attaching the canonical mesh and calling the result source truth. Instead:

- preserve the raw Action on its native carrier;
- shortlist promising clips using motion data or an explicitly temporary diagnostic visualization;
- retarget and bake onto the canonical rig;
- render a labeled post-retarget audition with shoulder and arm-chain crops;
- approve the target-specific Action only after visual review.

## Fresh-reopen acceptance checks

Reopen the exact library output in a separate Blender process and assert programmatically:

- expected canonical mesh and rig exist;
- mesh parent and Armature-modifier target both point to the canonical rig;
- canonical Action is still assigned;
- raw carrier count and total Action count match the catalog;
- every Action has Fake User enabled;
- raw-carrier collection exists and is hidden from viewport/render as intended;
- packed character texture remains present;
- embedded catalog exists;
- sidecar row count equals the Action count.

Only then report the library as saved. This verifies preservation and organization, not motion quality; post-retarget renders remain the visual gate.

## Pitfalls

- Do not create one skinned mesh duplicate per dance merely for organization.
- Do not rename generic Actions with invented dance styles. Use numbered reversible labels until the artist identifies them.
- Do not treat a successful Action assignment as evidence that rest spaces are compatible.
- Do not delete bare source carriers after copying Actions; retain them until target-specific retargets have been baked and visually approved.
- Do not build the final dance video in the protected library master. Create a versioned cinematic derivative after selecting approved Actions.
