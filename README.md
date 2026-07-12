# codex-pets

A flat catalog of custom Codex-compatible pets. Each member is a root-level
sibling folder — `pet.json` plus `spritesheet.webp` — ready to copy as one unit.
All members share one atlas contract. `production/` is the evidence surface: the
runtime package runs; the production record makes it answerable.
自定义 Codex 兼容宠物的扁平目录。每个成员都是根级同级文件夹——`pet.json` 加
`spritesheet.webp`——可作为一个整体直接复制。全体共用一套图集契约。`production/`
是证据面：运行包负责运行；生产记录使它可被追问。

---

## Pets | 宠物

| Pet | Rendering style | Status |
|---|---|---|
| [`cyber-otter-2077`](cyber-otter-2077/) | fishing the endless sea of time · smooth · 无尽时间之海垂钓 · 平滑 | active · 已发布 |
| [`cyber-otter-2077-pixel-edition`](cyber-otter-2077-pixel-edition/) | fishing the endless sea of time · pixel · 无尽时间之海垂钓 · 像素 | active · 已发布 |

Members are added beside members, never under a generic `pets/` wrapper. Shared
character identity is optional; the catalog only requires the atlas contract.
新成员与既有成员同级新增，不放进通用 `pets/` 包装层。是否共用角色可选；目录只要求满足
图集契约。

---

## Contract | 契约

The claim is narrow: a release is valid only when its runtime package matches a
reviewed production run and can be rebuilt pixel for pixel from frozen release
cells. File presence alone proves less.
主张刻意收窄：只有当运行包与已审阅的生产记录一致，且能由冻结 release cells 逐像素
重建时，发布才成立。仅有文件，不构成证明。

| Surface | Contains | Consequence |
|---|---|---|
| `<pet-id>/` | `pet.json` + `spritesheet.webp` | root-level sibling; copy directly into Codex · 根级并列；可直接复制进 Codex |
| `production/<pet-id>/` | request, jobs, prompts, references, decoded, frames, assembly, final, QA, manifest | binds the runtime to its production chain · 把运行包绑定到生产链 |
| `scripts/` | rebuild, validation, install | turns the contract into checks · 把契约变成检查 |

---

## Layout | 目录

Every runtime member has the same shape; current members are listed under
[Pets](#pets--宠物).
每个运行成员同构；当前成员见 [宠物](#pets--宠物)。

```text
codex-pets/
├── README.md
├── LICENSE
├── requirements.txt
├── <pet-id>/                      # direct-copy pet · 可直接复制的宠物
│   ├── pet.json
│   └── spritesheet.webp
├── production/
│   └── <pet-id>/                  # matching evidence record · 对应证据记录
└── scripts/
    ├── config.py                  # one filesystem/atlas contract · 单一契约源
    ├── rebuild_atlas.py           # frozen cells → atlas · 冻结单元 → 图集
    └── pets.py                    # validate, audit, install · 验证、审计、安装
```

---

## Runtime | 运行时

Install any listed member with the repository script:
用仓库脚本安装表中任一成员：

```bash
pip install -r requirements.txt
python scripts/pets.py install <pet-id>
```

Or copy one root-level pet directory into `~/.codex/pets/`. Do not copy
`production/` or `scripts/`; Codex does not read them.
也可把根目录下任一宠物文件夹直接复制到 `~/.codex/pets/`。不要复制 `production/` 或
`scripts/`；Codex 不读取它们。

```bash
cp -r <pet-id> ~/.codex/pets/
```

Every atlas uses the Codex-compatible 11-row pet spritesheet format selected by
`spriteVersionNumber: 2`: lossless RGBA WebP, `1536 × 2288`, an `8 × 11` grid of
`192 × 208` cells, nine state rows, and sixteen clockwise look directions.
每张图集均遵循由 `spriteVersionNumber: 2` 选择的 Codex 兼容 11 行宠物图集格式：无损
RGBA WebP、`1536 × 2288`、`8 × 11` 个 `192 × 208` 单元、九行状态动画，以及十六向
顺时针观察。

---

## Production chain | 生产链

```text
reference + request
        ↓
prompts + imagegen job graph
        ↓
approved decoded strips
        ↓
extracted state frames
        ↓
final assembly + one despill pass
        ↓
frozen release cells
        ↓
runtime atlas + QA ledger
```

Generation is interpretive; assembly is deterministic. The repository therefore
preserves both layers but does not confuse them: rerunning a prompt need not return
the same drawing, while rebuilding from frozen cells must return the same RGBA
pixels.
生成属于解释层，组装属于确定层。仓库保留两层，却不混淆二者：重跑提示词不必得到同一
幅画；由冻结单元重建，则必须得到相同 RGBA 像素。

---

## Verify | 验证

```bash
python scripts/rebuild_atlas.py build all
python scripts/pets.py audit
```

After an intentional source change, a maintainer may refresh the production
ledger:

```bash
python scripts/pets.py manifest
```

`manifest` accepts a changed file into the ledger; it is not a repair command.
Review the change first. Then move the hash.
`manifest` 把变更纳入账本，并不修复变更。先审查文件，再移动哈希。

| Gate | Required result |
|---|---|
| Runtime shape | `pet.json` + `spritesheet.webp`; RGBA WebP; exact 11-row atlas geometry · 运行包形状、RGBA WebP、11 行图集几何精确 |
| State cells | every used slot populated; every unused slot transparent · 使用格非空、空闲格透明 |
| Production graph | all jobs complete; every input and output repository-relative · 作业完成、输入输出均为相对路径 |
| Rebuild | frozen cells reproduce runtime RGBA pixels · 冻结单元重建运行时像素 |
| Direction QA | four cardinals pass; sixteen semantic verdicts contain no failure · 四基准方向通过、十六方向无失败 |
| Privacy | no workstation path, account identifier, or temporary generation path · 无本机路径、账号标识或临时生成路径 |

---

## Authoring | 新增宠物

Add one root-level `<pet-id>/` with `pet.json` and `spritesheet.webp`; add the
matching `production/<pet-id>/` evidence record; register the id in
`scripts/config.py` (`PET_IDS`); then add one row to [Pets](#pets--宠物). Run
`audit` before treating the member as released.
新增根级 `<pet-id>/`（含 `pet.json` 与 `spritesheet.webp`）；补齐对应
`production/<pet-id>/` 证据记录；在 `scripts/config.py` 的 `PET_IDS` 注册该 id；再在
[宠物](#pets--宠物) 加一行。视为发布前先跑 `audit`。

---

## Limits | 边界

This repository does not redistribute Codex built-in pet atlases. It also does
not claim that AI image generation is reproducible, or that these custom pets are
endorsed by OpenAI. These are boundaries, not omissions.
本仓库不再分发 Codex 内置宠物图集。仓库也不声称 AI 图像生成可复现，更不声称这些自定义
宠物获 OpenAI 背书。这些是边界，不是遗漏。

A release is rejected when any accepted runtime differs from its reviewed
production spritesheet, when a rebuilt pixel differs, when a hard direction gate
fails, or when the public tree contains private workstation provenance.
当运行包与已审阅的生产图集不一致、重建像素不同、硬方向闸门失败，或公开树残留本机溯源
时，发布不成立。

---

## Encoding | 编码

UTF-8, no BOM. · UTF-8，无 BOM。

---

## License | 许可

Code under `scripts/` is MIT (see `LICENSE`). The character, sprites, prompts, and
animation assets remain property of Xinhao Zheng.
`scripts/` 下代码采用 MIT（见 `LICENSE`）；角色、精灵图、提示词与动画资产归
Xinhao Zheng 所有。

---

*What installs is the package. What holds is the record. · 可安装的是运行包；成立的是生产记录。*
