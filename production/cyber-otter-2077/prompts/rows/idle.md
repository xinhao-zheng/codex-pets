Create one horizontal animation strip for Codex pet `cyber-otter-2077`, state `idle`.

Use the attached canonical base for identity. Use the attached layout guide only for slot count, spacing, centering, and padding; do not draw the guide.

Output exactly 6 full-body frames in one left-to-right row on flat pure user-selected #00FF00. Treat the row as 6 invisible equal-width slots: one centered complete pose per slot, evenly spaced, with no overlap, clipping, empty slots, labels, or borders.

Identity: same pet in every frame: Plump cyberpunk sea otter inspired by the provided reference: broad rounded head, small round ears, huge matte-black nose, glossy dark eyes, cream muzzle and belly, dense dark-brown fur simplified for pet scale, magenta circuitry on viewer-left face and cyan circuitry on viewer-right face, compact black tactical chest harness with restrained cyan-magenta light blocks, short black fishing rod and compact reel physically attached to the paws. Preserve the same side-specific markings, facial geometry, body proportions, harness, rod and tail in every pose. Cyberpunk 2077 mood through materials and color only; no readable text, logo, HUD, city, detached holograms or scenery.. Preserve silhouette, face, proportions, markings, palette, material, style, and props.
Style: Pet-safe sprite: compact full-body mascot, readable in a 192x208 cell, clear silhouette, simple face, stable palette/materials, and crisp edges for chroma-key extraction. Style `3d-toy`: Stylized 3D toy mascot with smooth rounded forms, simple materials, clear silhouette, and no photoreal complexity. User style notes: Official Codex Desktop pet language translated into a polished non-pixel mascot: compact chibi silhouette, large head and stubby limbs, crisp dark contour, simplified soft fur planes rather than photoreal strands, controlled two-to-four tone materials, restrained glossy eyes and cyber hardware, strong readability at 192x208, no painterly haze or cinematic background..
Animation continuity: keep apparent pet scale and baseline stable within the row unless the state itself intentionally changes vertical position, such as `jumping`. Move the pose within the slot instead of redrawing the pet larger or smaller frame to frame.

State action: Calm low-distraction resting loop: subtle breathing, tiny blink, slight head/body bob, and only quiet persona-preserving motion.

State requirements:
- CRITICAL: idle is the low-distraction baseline state and the first frame is also used as the reduced-motion static pet.
- Use only subtle idle motion: gentle breathing, a tiny blink, a slight head or body bob, a very small material sway, or another quiet motion that fits the pet persona.
- Keep the pet essentially in the same pose, facing direction, silhouette, markings, palette, and prop state across all 6 frames.
- Idle variation must stay calm but still read as animation; do not repeat effectively identical copies across the loop.
- Do not show waving, walking, running, jumping, talking, working, reviewing, emotional reactions, large gestures, item interactions, or new props.
- Feet, base, body, or object anchor should remain planted or nearly planted.
- The first and last frames should be very close visually so the loop feels calm and does not pop.

Clean extraction: crisp opaque edges, safe padding, no scenery, text, guide marks, checkerboard, shadows, glows, motion blur, speed lines, dust, detached effects, stray pixels, or chroma-key colors inside the pet.
