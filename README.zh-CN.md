# AI 字幕流水线（中文概览）

[English](README.md) · [许可](LICENSE)

一套本地优先、可审计的 AI 辅助字幕翻译流程。它把源字幕（`*.ass`）和视频变成
译文字幕，并用客观检查抓住朴素翻译会漏掉的三类问题：**术语漂移**、**时间轴漂移**、
**花体/顶部字幕漏译**。

## 为什么需要

翻译一两句台词很简单；翻译一整部系列不是：

- 同一个人名在不同集被译成好几种中文；
- 字幕文件和视频其实是同一作品的不同剪辑版，首句看着对，中段漂移几十秒；
- 顶部提示、地点招牌、中央大字因为不是对白样式，被主翻译直接跳过，保持原文。

本流程用「锁定词表 + 时间基准 + 保样式拼接 + 强制交付审计」来解决它们。

## 功能

- **词表优先**：锁定的术语表，每句翻译都要遵守，并有自动一致性核对。
- **时间轴校准**：用文本对齐 + 音频起音点量测漂移，把译文重定到权威轨道。
- **保样式拼接**：只替换可见文字，`\an8`/`\pos`/`\move`/`\fscx`/淡入淡出等标签原样保留。
- **强制审计**：一条命令检查文件完整性、提示横幅、语言覆盖率、术语一致性、音频同步、花体缺口。
- **本地离线**：纯 Python 脚本在本地文件上跑，不上传任何内容。

## 快速开始

```bash
python scripts/dump_targets.py input.ass targets.txt
# 把 targets.txt 翻成 translations.txt（key|text）
python scripts/splice.py input.ass translations.txt output.ass --margin 40
python scripts/audit_episode.py output.ass video.mkv input.ass
```

详细文档见 [docs/pipeline.md](docs/pipeline.md) 等；英文为主，中文为可选补充。

## 许可

MIT — 见 [LICENSE](LICENSE)。
