---
name: fm-repo
version: 1.0.0
description: fm is a file synchronous tools between difference host
trigger_conditions:
  - 需要理解、修改或排障 fm 的代码
  - 在 fm 里定位入口、数据表、对外契约或构建方式
---

# fm 仓库技能

> 由仓库实际内容生成的骨架（README/目录/模型定义/契约/构建脚本逐项取证）。新增判断与坑位请直接在下面对应小节补充。

## 定位

**fm is a file synchronous tools between difference host**

appPublic provide some bases functions for fm, [watchdog](https://pypi.org/project/watchdog/) is a files or folders changes monitor engine, [hachiko](https://github.com/biesnecker/hachiko) is the asynchronous API for watchdog [paramiko](https://github.com/paramiko/paramiko) is a python ssh2 api fm m

- 远端：`https://github.com/yumoqing/fm.git`
- 默认分支：`master`（共 23 个提交）
- 最近提交：2019-10-25 `33ec5f7` recovery
- 规模：10 个文件；Python 6，Shell 1，JSON 1

## 目录结构

- `conf/` — 配置（`config.json`；密码为 AES 密文）（1 个文件）
- 根文件：`README.md`、`build.sh`、`filemonitor.py`、`newfm1.2.py`、`newfm1.py`、`newfm2.py`、`requirements.txt`、`sftpapi.py`、`t.py`

## 代码入口（顶层 Python）

- `filemonitor.py`
- `newfm1.2.py`
- `newfm1.py`
- `newfm2.py`
- `sftpapi.py` — #logon without password
- `t.py`

## 构建与运行

- `build.sh`（一键部署）
- `requirements.txt`：5 项（asyncio、watchdog、hachiko、appPublic、paramiko）

## README 要点与注意（摘自 `README.md`）

- 章节：dependented packages、function、configuratin

## 建议阅读顺序

1. `README.md`
2. `build.sh`

