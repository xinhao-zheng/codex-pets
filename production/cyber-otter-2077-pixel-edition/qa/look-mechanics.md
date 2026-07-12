# Cyber Otter 2077 Pixel Edition look mechanics

Use the same physical motion family as the polished edition, redrawn in strict native-cell pixel clusters: **eyes lead, broad nose/muzzle and head follow, ears and upper torso lag subtly**. The feet, lower body, harness center, purple reel mount, and tail root stay registered. No whole-sprite rotation, affine tilt, rescale, recentering, or pixel-filter transformation.

The eyes remain the canonical block-built glossy eyes. Move/redraw the complete eye construction—rim, dark globe, compact highlights, and eyelids—rather than pasting new pupils. Head yaw changes muzzle width and near/far eye/ear occlusion with deliberate stepped contours. Pitch changes nose height, muzzle foreshortening, eyelids, crown exposure, and restrained upper-body compression.

## Fixed identity and anchors

- Viewer-left facial circuit is magenta; viewer-right facial circuit is cyan.
- Purple reel and visible thick tail remain viewer-left, matching the approved canonical base and standard rows.
- Feet/baseline, lower torso, harness center, head volume, cluster scale, and attached rod geometry remain stable.
- Each 22.5° step advances by comparable pixel-cluster amounts with no lighting, palette, outline, or registration jump.

## Cardinal pose families

- `000 up`: whole eyes aim upward, upper lids lift, nose/muzzle pitch up, chin shortens; clearly different from neutral.
- `090 screen-right`: eye and nose landmarks cross to screen-right; cyan near side broadens while magenta far side is partly occluded.
- `180 down`: eyes/nose lower, lids press down, chin tucks, crown grows; feet and lower body remain fixed.
- `270 screen-left`: eye and nose landmarks cross to screen-left; magenta near side and reel read clearly while cyan far side is partly occluded. Never mirror the identity.

Interpolate both axes for diagonals. Row 9 is `000 → 090 → 180`; row 10 is `180 → 270 → 000`, with equal boundary steps at `157.5 → 180` and `337.5 → 000`.

## Row 10 screen-coordinate hard gate

`screen-left` is the left edge of the output image, not the character's left. After `180`, the nose tip and complete eye axis in `202.5`, `225`, and `247.5` must move progressively left of the head/slot center. `270` must match the approved left cardinal with the muzzle projecting toward the image-left edge. `292.5`, `315`, and `337.5` remain left of center while pitching upward; `337.5` is only slightly left of center with both eyes and ears visible. Except for front/down `180`, no row-10 muzzle may project toward the image-right edge.

`180` must reproduce the approved down cardinal, not neutral/front: nose and complete eye construction visibly below neutral, chin tucked toward the harness, upper lids pressed down, and more crown visible. The compact silhouette must still clear the shared final-cell edge budget.
