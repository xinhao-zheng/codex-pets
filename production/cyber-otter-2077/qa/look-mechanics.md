# Cyber Otter 2077 look mechanics

The natural gaze is **eyes first, broad nose and muzzle second, head/ears third, upper torso and shoulder straps last**. The planted feet, lower torso, harness center, reel mount, and tail root remain registered. The compact rod stays connected to both paws/harness and may lag by only a few pixels; it never crosses the face, changes hand, or swaps screen side.

The eyes are physical glossy eyeballs: iris/pupil, eye rim, eyelids, and highlights rotate and reshape together. Do not slide isolated pupils over unchanged eyes. The broad muzzle compresses slightly on the far side and opens on the near side as the head yaws. Pitch uses eyelids, nose height, muzzle foreshortening, ear height, and a restrained neck/upper-body follow-through. Never rotate, skew, or tilt the whole sprite.

## Fixed identity and anchors

- Viewer-left facial circuit is magenta; viewer-right facial circuit is cyan.
- The purple reel and visible thick tail remain viewer-left, matching the approved canonical base and all standard rows.
- Feet/lower body baseline, torso scale, head volume, harness center, and rod attachment remain stable.
- Every 22.5° transition uses an even motion budget; adjacent cells may not snap, rescale, recenter, or change lighting.

## Cardinal pose families

- `000 up`: eyes rotate upward, upper eyelids lift, nose/muzzle pitch upward, chin shortens, and ears lower slightly in perspective; both facial circuits remain visible. This must not read as neutral/front.
- `090 screen-right`: pupils, nose tip, muzzle center, and head yaw clearly past center toward the viewer's right. The viewer-right cyan side is nearer and broader; the viewer-left magenta side, eye, and ear are modestly occluded. Harness and reel remain anchored.
- `180 down`: eyes and nose lower, upper eyelids press down, chin tucks, more crown is visible, and upper torso follows slightly while feet remain fixed.
- `270 screen-left`: pupils, nose tip, muzzle center, and head yaw clearly past center toward viewer-left. The magenta side and viewer-left reel are nearer; the cyan side, eye, and ear are modestly occluded. Do not mirror the markings, reel, or visible tail.

Diagonals combine both adjacent cardinal axes. Row 9 travels `000 → 090 → 180`; row 10 continues `180 → 270 → 000`. The `157.5 → 180` and `337.5 → 000` boundaries must be single equal steps.

## Row 10 screen-coordinate hard gate

`screen-left` means the **left edge of the output image**, never the character's left. After the front/down `180` cell, the nose tip and whole-eye axis in `202.5`, `225`, and `247.5` must move progressively to the left of the head/canvas-slot center. `270` must reproduce the approved left cardinal: nose tip unmistakably left of head center and muzzle projecting toward the image's left edge. `292.5`, `315`, and `337.5` remain on that same screen-left side while pitching upward and returning gradually toward center; `337.5` is only slightly left of center with both eyes and ears visible. No row-10 cell except `180` may project the muzzle toward the image's right edge.

`180` is also a hard cardinal gate, not a neutral transition frame. It must visibly reproduce the approved down anchor: nose tip and both complete eye axes below their neutral positions, chin tucked toward the harness, upper eyelids pressing downward, and clearly more crown visible than neutral. If it reads as upright/front, the entire row fails even when columns 1–7 point left.

Final return poses are hard continuity gates. `315` must still place the nose tip left of head center **and** above its level/neutral height, with the whole-eye axis aimed upper-left and chin visibly raised; it may not reverse right or bow down. `337.5` must keep a subtle but readable upper-left axis: nose slightly left and raised, both complete eyes/pupils upper-left, both ears visible, and body center/area matching row-9 `000` closely enough for a one-step wrap. A centered level face is not acceptable for `337.5`.
