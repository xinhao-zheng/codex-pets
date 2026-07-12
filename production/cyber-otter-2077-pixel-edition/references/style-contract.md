# style contract

Codex compatibility is a geometry-and-motion claim. Surface resemblance is not
enough: the pet must remain readable, bounded, and semantically stable inside the
native cell.
Codex 兼容是一项几何与动作主张。表面相似不够：宠物必须在原生单元内保持可读、受界、
语义稳定。

---

## Shared geometry | 共用几何

1. One connected silhouette binds head, torso, tail, and tool.
2. A large head carries identity; short limbs and broad feet hold the baseline.
3. Face, muzzle, eyes, harness, and reel remain separable before fine texture is read.
4. Every body part stays inside its `192 × 208` slot with transparent padding.

1. 一个连通轮廓绑定头、躯干、尾与工具。
2. 大头承载身份；短肢与宽足固定基线。
3. 在读取细纹理前，面部、口鼻、眼、胸挂与线轮已可分辨。
4. 所有身体部分均留在 `192 × 208` 格内，并保有透明边距。

Motion comes from pose, expression, and attached equipment. Detached marks,
speed lines, floor shadows, glow, smoke, UI, and scenery add pixels without adding
state information. They are excluded.
动作由姿态、表情与连接设备产生。游离符号、速度线、地面阴影、辉光、烟雾、UI 与场景
增加像素，却不增加状态信息。故排除。

---

## Polished edition | 普通版

The polished edition uses simplified fur planes, restrained highlights, a dark
outer contour, and broad value bands. It may be smooth; it may not become a
photograph, cinematic sticker, airbrushed illustration, or glow cutout.
普通版采用简化毛发面、克制高光、深色外轮廓与宽明度带。它可以平滑，却不能变成照片、
电影贴纸、喷绘插画或辉光剪影。

---

## Pixel edition | 像素版

The pixel edition is authored at native cell scale. Stepped contours, discrete
clusters, and bounded two-to-four-step ramps carry form. Blur, smooth painterly
gradients, enlarged mock pixels, and unstructured one-pixel noise do not.
像素版在原生单元尺度上制作。阶梯轮廓、离散色块与二至四阶明度坡承载形体；模糊、平滑
绘画渐变、放大的伪像素与无结构单像素噪声不能。

---

## State semantics | 状态语义

| Row | State | Required reading |
|---:|---|---|
| 0 | `idle` | breath and blink; no task action · 呼吸与眨眼；无任务动作 |
| 1 | `running-right` | alternating right-facing locomotion · 面右交替步态 |
| 2 | `running-left` | independently authored left-facing locomotion · 独立制作的面左步态 |
| 3 | `waving` | paw rises and returns · 爪抬起并回落 |
| 4 | `jumping` | anticipation, lift, peak, descent, settle · 预备、起跳、顶点、下降、落定 |
| 5 | `failed` | rig powers down; body deflates · 装备熄灭、身体泄力 |
| 6 | `waiting` | expectant request for input · 期待输入 |
| 7 | `running` | active Codex work; no locomotion · Codex 任务处理中；不位移 |
| 8 | `review` | focused inspection and completion beat · 聚焦检查与完成节拍 |
| 9–10 | `look` | one clockwise sixteen-pose family · 单一顺时针十六姿态族 |

---

## Direction and failure | 方向与失败

Rows 9–10 keep the feet and lower torso registered while gaze turns clockwise.
`000` reads up, `090` screen-right, `180` down, and `270` screen-left. A cardinal
that needs its label to be understood has failed.
第 9–10 行固定足部与下躯干，使视线顺时针转动。`000` 向上，`090` 向画面右，`180`
向下，`270` 向画面左。若基准方向必须依赖标签才能理解，它已经失败。

The style contract fails on identity drift, blank or clipped frames, opaque key
panels, detached effects, baseline jumps, wrong-facing travel, inert idle motion,
wrong-quadrant gaze, or a visible reversal in the direction loop.
若出现身份漂移、空帧或裁切、不透明色键面板、游离效果、基线跳变、移动朝向错误、静止
idle、错误象限视线，或方向循环可见反转，样式契约即告失败。
