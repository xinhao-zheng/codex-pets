# production/

Each child is a complete Codex pet production record. Its order is causal: request
before generation, generated strips before frames, frames before final, final before
QA. Moving a later artifact cannot repair an earlier failure.
每个子目录都是完整的 Codex 宠物生产记录。其顺序是因果顺序：先请求，再生成；先条带，
再帧；先终稿，再 QA。移动下游工件，不能修复上游失败。

```text
<pet-id>/
├── pet_request.json
├── imagegen-jobs.json
├── references/
├── prompts/
├── decoded/
├── frames/
├── assembly/
│   ├── cells/
│   └── release-cells.json
├── final/
├── qa/
└── production-manifest.json
```

`decoded/` preserves approved generated sources. `frames/` preserves the standard
state extraction. `assembly/cells/` freezes the cleaned release cells so
`scripts/rebuild_atlas.py` can reproduce the accepted RGBA atlas without invoking
an image model.
`decoded/` 保存获准生成源，`frames/` 保存标准状态抽帧，`assembly/cells/` 冻结清理后的
发布单元，使 `scripts/rebuild_atlas.py` 无需调用图像模型即可重建获准 RGBA 图集。
