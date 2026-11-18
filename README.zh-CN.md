# historical-portrait-reconstruction

**历史原画 → 画像约束的写实人像 → 真实原画并排对照。**

[English](README.md) · [Skill](skills/historical-portrait-reconstruction/SKILL.md) · [案例](examples/) · [参与贡献](CONTRIBUTING.md)

## 使用示例

在已加载本 Skill、且能输入参考图生成图像的 Agent 中提出请求：

> 按可追溯的画像还原秦始皇。核实作品年代和人物身份，保留原画可见的五官与视角，交付左侧真实原画、右侧写实转写的对照图，并说明后世画像的局限。

批量处理：

> 按给定清单处理明朝皇帝。每人独立选原画、记录面部特征、生成写实人像，逐人交付一张最终对照图，并列出完整处理状态。

**最终并排对照是强制交付。** 左栏由脚本放入实际取得的图档，不能让生成模型重画一幅“原画像”。

## 项目做什么

本 Skill 引导 Agent 完成选源、观察、参考图生成、拼接和检查。目标是保留每张原画中可观察到的人物区别。

| 阶段 | 必须得到的内容 |
| --- | --- |
| 选源 | 可追溯作品、可用时的馆藏编号、作品年代、身份依据、图像链接和许可记录 |
| 观察 | 逐人记录可见特征，将模糊与不可见部分单独列出 |
| 生成 | 将真实参考图传入支持参考图输入的生图后端 |
| 拼接 | 左真实原画、右写实转写，记录裁切和等比缩放 |
| 检查 | 对照该人物原画、检查跨人物同脸问题、核对批量完成度 |

**与画作相似，不等于证实历史真人的长相。** 输出属于图像证据约束的艺术性转写，不能作为法医复原或可量化的真人相似度。

## 安装 Skill

可复用目录为 `skills/historical-portrait-reconstruction/`，采用 [Agent Skills 格式](https://agentskills.io/specification)。

### Claude Code 本地终端会话

以下采用 Claude Code 官方记录的个人 Skill 目录，核查日期为 **2026-11-18**。客户端版本变化时，以[官方文档](https://code.claude.com/docs/en/skills)为准。

```bash
git clone https://github.com/TimeCracker/historical-portrait-reconstruction.git
cd historical-portrait-reconstruction
mkdir -p "$HOME/.claude/skills"
cp -R skills/historical-portrait-reconstruction "$HOME/.claude/skills/"
```

首次安装时复制整个目录。已有同名 Skill 时，先比较内容再替换。随后可以在 Claude Code 中调用：

```text
/historical-portrait-reconstruction 根据这幅画像生成写实人像，并交付原画与写实图并排对照。
```

项目级安装可放入项目内的 `.claude/skills/historical-portrait-reconstruction/`。其他 Agent Skills 客户端应使用各自支持的导入或发现方式。

**安装指令不会自动提供生图服务。** 宿主还需能看图、将参考图输入生图后端，并执行拼图脚本。本仓库不包含模型权重、API 凭据或自动接入后端的适配器。安装路径说明不代表已经验证该客户端的完整生图流程。

## 运行拼图脚本

拼图脚本处理**两张已有图片**，不负责生成人像或下载原画。

依赖：**Python 3.11+、Pillow 13.x**。当前开发环境为 Python **3.12.14**、Pillow **13.0.0**；不将其他环境标为已经测试。

在仓库根目录执行：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python skills/historical-portrait-reconstruction/scripts/compose_comparison.py --help
```

上述虚拟环境激活命令适用于 macOS/Linux shell；其他平台使用对应的 Python 虚拟环境激活方式。

### 单人

准备实际取得的原画和生成的人像，再执行：

```bash
python skills/historical-portrait-reconstruction/scripts/compose_comparison.py \
  --source input/source.jpg \
  --portrait input/portrait.png \
  --output output/comparison.png \
  --title "Qin Shi Huang" \
  --caption "Later painted depiction; historical likeness is not verified."
```

可选参数包括 `--crop X0 Y0 X1 Y1`、`--portrait-crop X0 Y0 X1 Y1`、`--panel-width`、`--panel-height`、`--source-label`、`--portrait-label` 和 `--font`。裁切坐标是解码后输入图像上的整数像素坐标，右边界和下边界不包含在裁切区域内。原画允许时，两侧保持相同视角。

中文标题需要支持中文的字体；自动查找未找到时，用 `--font /path/to/font.ttf` 指定。仓库不附带字体。

输出包括：

- `output/comparison.png`：并排对照图。
- `output/comparison.json`：输入哈希与拼接记录。

哈希用于识别输入文件，不能证明作品归属或人物长相真实。

### 批量

将以下内容保存为 `jobs.json`，并准备其中指定的文件：

```json
{
  "items": [
    {
      "id": "person-one",
      "source": "input/person-one-source.jpg",
      "portrait": "input/person-one-portrait.png",
      "output": "output/person-one.png",
      "title": "Person one",
      "caption": "Source-grounded interpretation; historical likeness is not verified."
    }
  ]
}
```

```bash
python skills/historical-portrait-reconstruction/scripts/compose_comparison.py \
  --manifest jobs.json
```

清单内路径相对于清单所在目录解析。每项必须有唯一 `id`、`source`、`portrait` 和 `output`；文字、裁切和字体设置可以逐项补充。默认批量报告是清单旁的 `batch_report.json`，也可用 `--report` 指定路径。核对报告及退出状态后，才能将批次标为完成。

流程不设“最多十人”的固定限制。后端限制或失败必须按实际运行情况记录，未完成的人物仍保留在清单中。

## 证据与检查原则

- 实际查看原画和面部，不能只读馆藏介绍。
- 区分人物在世年代与作品创作年代。
- 同一母本派生的复制品按共同来源链处理。
- 默认保留原画视角；用户要求其他视角时，注明推测部分。
- 每人独立锁定面部特征，共用服装或光照不能导致共用一张脸。
- 文学修辞和性格评价不能转化为虚构的解剖特征。
- 检查最终对照图，不能只检查生成的人像。
- 分别说明原画的史料局限与生成结果对原画的忠实程度。

完整执行规则见 [SKILL.md](skills/historical-portrait-reconstruction/SKILL.md)。

## 案例与图片

- [秦始皇](examples/qin-shi-huang/)：来源记录、观察约束提示词和拼接清单。
- [明朝皇帝](examples/ming-portraits/)：十六人的来源记录和批量清单。

首版案例**仅包含记录与文本**，不附带下载的历史扫描图或生成的人像文件。示例清单说明需要准备哪些文件，并非已经配齐图片的数据集。

第三方图片保留各自的权利说明。详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 开发验证

在仓库根目录运行：

```bash
python -m unittest discover -s tests -v
```

这些测试检查确定性图像处理和批量行为，不测量历史真实性，也不证明生图模型保持了人物身份。

2026-11-18：在上述环境中通过 13 项测试，包括原画区域逐像素核对、输入哈希不变、跨工作目录的 12 人批处理，以及部分保存失败时的状态报告。

## 许可

贡献者有权许可的原创 Skill 指令、脚本和仓库文档采用 [MIT License](LICENSE)。第三方图片、字体、依赖和服务输出分别适用其条款。

版本变更见 [CHANGELOG.md](CHANGELOG.md)，贡献要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。

