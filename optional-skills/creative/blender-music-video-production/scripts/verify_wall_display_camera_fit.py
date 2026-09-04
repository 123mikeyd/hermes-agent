"""Verify wall-display objects through an animated Blender camera.

Usage:
  blender -b scene.blend --python verify_wall_display_camera_fit.py -- \
    report.json ArtworkObject FrameObject TopLabel BottomLabel

Frames are derived from scene start/end plus every timeline marker and the
midpoint before the next marker. The JSON `all_inside` field is the gate; use a
normal Python assertion after Blender exits because some Blender builds return
zero even when a Python script raises.
"""

import bpy
import json
import sys
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
if len(args) < 2:
    raise ValueError("Expected output JSON path and at least one object name")

out = Path(args[0])
object_names = args[1:]
scene = bpy.context.scene
camera = scene.camera
if camera is None:
    raise RuntimeError("Scene has no active camera")

marker_frames = sorted({m.frame for m in scene.timeline_markers})
frames = {scene.frame_start, scene.frame_end, *marker_frames}
for index, start in enumerate(marker_frames):
    end = marker_frames[index + 1] - 1 if index + 1 < len(marker_frames) else scene.frame_end
    if end >= start:
        frames.add((start + end) // 2)
frames = sorted(frame for frame in frames if scene.frame_start <= frame <= scene.frame_end)

report = {
    "blend": bpy.data.filepath,
    "camera": camera.name,
    "scene_range": [scene.frame_start, scene.frame_end],
    "frames": frames,
    "objects": {},
    "all_inside": True,
}

for name in object_names:
    source = bpy.data.objects.get(name)
    if source is None:
        report["objects"][name] = {"exists": False}
        report["all_inside"] = False
        continue

    entry = {
        "exists": True,
        "type": source.type,
        "text_body": source.data.body if source.type == "FONT" else None,
        "font_filepath": source.data.font.filepath if source.type == "FONT" and source.data.font else None,
        "samples": {},
        "inside_all_samples": True,
    }
    for frame in frames:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = source.evaluated_get(depsgraph)
        corners = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
        projected = [world_to_camera_view(scene, camera, point) for point in corners]
        bounds = {
            "x": [min(p.x for p in projected), max(p.x for p in projected)],
            "y": [min(p.y for p in projected), max(p.y for p in projected)],
            "min_depth": min(p.z for p in projected),
        }
        inside = (
            bounds["min_depth"] > 0
            and bounds["x"][0] >= 0 and bounds["x"][1] <= 1
            and bounds["y"][0] >= 0 and bounds["y"][1] <= 1
        )
        bounds["inside"] = inside
        entry["samples"][str(frame)] = bounds
        entry["inside_all_samples"] &= inside
    report["objects"][name] = entry
    report["all_inside"] &= entry["inside_all_samples"]

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
print("WALL_DISPLAY_CAMERA_FIT_OK" if report["all_inside"] else "WALL_DISPLAY_CAMERA_FIT_FAIL")
