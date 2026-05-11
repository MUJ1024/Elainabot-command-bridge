# 命令桥接插件

> 项目地址：https://github.com/MUJ1024/Elainabot-command-bridge

将 QQ 上带 `！` 前缀的消息写入信号文件，供 Claude Code 每 10 分钟检查处理。处理后通过 Web API 回复到 QQ。

## 运行环境

- 仅限 **Claude Code 终端** 中使用
- 需要以 `claude --dangerously-skip-permissions` 启动（否则无法自动执行 Bash 命令和 Web API 调用）
- Windows 用户可自行创建启动脚本 `claude --dangerously-skip-permissions`

## 工作流程

```
你发 ！<指令>
  → Bot 插件写入 data/p（信号文件）和 data/command_queue/tasks.json（任务列表）
  → Claude Code 每 10 分钟检查 data/p 是否存在
  → 存在则读取 tasks.json 中所有待处理任务
  → 处理后标记为 done，删除 data/p
  → 通过 Web API 回复结果到 QQ
```

## 安装

1. 将 `command_bridge/` 放到 `plugins/` 下
2. 框架自动热加载或手动重载
3. 发送 `！测试` 验证（回复"已投递"即成功）

## 配置

指令仅限 `config/bot.yaml` 中 `owner_ids` 内的用户使用：

```yaml
bots:
  - appid: "你的appid"
    owner_ids:
      - "<你的openid>"
```

## 轮询

```
/loop 10m "检p"
```

取消：`/cron_delete <job_id>` ｜ 查看：`/cron_list`

## 指令

| 指令 | 功能 |
|------|------|
| `！<内容>` | 投递新任务 |
| `tdck` / `投递查看` / `投递列表` | 查看待处理 |
| `我的投递` / `tdall` | 查看全部（含已处理） |
| `tdsc <n>` | 按序号删除 |

## 文件

| 文件 | 说明 |
|------|------|
| `data/p` | 信号文件（1字节） |
| `data/command_queue/tasks.json` | 任务列表 |

## 隐私

- 用户 ID 仅存于 `config/bot.yaml` 和 `tasks.json`
- 不收集任何统计信息

## 文件结构

```
plugins/command_bridge/
├── README.md
├── __init__.py
├── main.py
└── app/
    ├── __init__.py
    └── commands.py
```
