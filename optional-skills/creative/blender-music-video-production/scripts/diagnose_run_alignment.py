"""Run inside Blender: diagnose locomotion facing and deformed-mesh floor clearance.

Usage:
  blender --background scene.blend --python diagnose_run_alignment.py -- \
    ARMATURE MESH MOTION_ROOT FLOOR START END FORWARD_BONE output.json
"""
import bpy
import json
import pathlib
import sys

args = sys.argv[sys.argv.index("--") + 1 :]
arm_name, mesh_name, root_name, floor_name, start, end, forward_bone, output = args
start, end = int(start), int(end)
scene = bpy.context.scene
arm = bpy.data.objects[arm_name]
mesh = bpy.data.objects[mesh_name]
root = bpy.data.objects[root_name]
floor = bpy.data.objects[floor_name]
deps = bpy.context.evaluated_depsgraph_get()
rows = []

for frame in range(start, end + 1):
    scene.frame_set(frame)
    deps.update()
    evaluated_arm = arm.evaluated_get(deps)
    pb = evaluated_arm.pose.bones[forward_bone]
    forward = (evaluated_arm.matrix_world @ pb.tail) - (evaluated_arm.matrix_world @ pb.head)
    forward.z = 0
    if forward.length:
        forward.normalize()

    p0 = root.matrix_world.translation.copy()
    scene.frame_set(min(frame + 1, end))
    deps.update()
    velocity = root.matrix_world.translation.copy() - p0
    velocity.z = 0
    if velocity.length:
        velocity.normalize()

    scene.frame_set(frame)
    deps.update()
    evaluated_mesh = mesh.evaluated_get(deps)
    temp = evaluated_mesh.to_mesh()
    min_z = min((evaluated_mesh.matrix_world @ v.co).z for v in temp.vertices)
    evaluated_mesh.to_mesh_clear()
    floor_z = floor.matrix_world.translation.z
    rows.append(
        {
            "frame": frame,
            "forward_xy": [forward.x, forward.y],
            "travel_xy": [velocity.x, velocity.y],
            "forward_travel_dot": forward.dot(velocity) if velocity.length else None,
            "mesh_min_z": min_z,
            "floor_z": floor_z,
            "clearance": min_z - floor_z,
        }
    )

valid = [r for r in rows if r["forward_travel_dot"] is not None]
dots = sorted(r["forward_travel_dot"] for r in valid)
result = {
    "file": bpy.data.filepath,
    "interval": [start, end],
    "root_rotation_z": root.rotation_euler.z,
    "median_forward_travel_dot": dots[len(dots) // 2],
    "minimum_clearance": min(r["clearance"] for r in rows),
    "maximum_clearance": max(r["clearance"] for r in rows),
    "worst_clearance_frame": min(rows, key=lambda r: r["clearance"]),
}
pathlib.Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")
print("RUN_ALIGNMENT=" + output)
