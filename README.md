# 命令桥接插件

> 项目地址：https://github.com/MUJ1024/Elainabot-command-bridge

将 QQ 上带 `！` 前缀的消息写入固定信号文件，供 Claude Code 定时读取和处理。处理完成后通过 Web API 将结果回复到 QQ。

## 工作流程

```
你发 ！<指令>
  → Bot 插件写入 data/command_queue/pending.json（固定文件名）
  → Claude Code 每分钟检查该文件是否存在
  → 存在则读取处理，不存在则静默跳过（0 成本）
  → 处理后删除文件，通过 Web API 回复结果到 QQ
```

## 安装

1. 将 `command_bridge/` 整个目录放到 `plugins/` 下
2. 框架自动热加载（~2秒）或手动在 Web 面板重载插件
3. 在 QQ 上发送 `！测试` 验证是否生效（bot 回复"已投递"即成功）

## 配置

### 授权用户

指令仅限 `config/bot.yaml` 中配置的 `owner_ids` 使用：

```yaml
bots:
  - appid: "你的机器人appid"
    owner_ids:
      - "<你的 openid>"
```

### Claude Code 轮询

在 Claude Code 对话中设置轮询（最小间隔 1 分钟，cron 限制）：

```
/loop 1m "如果 data/command_queue/pending.json 存在则处理指令"
```

取消轮询：

```
/cron_delete <job_id>
```

查看所有定时任务：

```
/cron_list
```

## 信号文件格式

写入 `data/command_queue/pending.json`：

```json
{"user_id": "用户openid", "time": "时间戳", "text": "指令内容"}
```

处理完成后 `pending.json` 会被删除。文件不存在 = 无待处理指令，轮询直接静默跳过。

## 使用示例

### 基础指令

| 你发 | 效果 |
|------|------|
| `！帮我看看 config/settings.yaml` | Claude Code 读取文件并回复 |
| `！修复 facility_manager.py 的报错` | 分析错误并修复 |
| `！git pull` | 拉取最新代码 |
| `！给我的状态加个等级显示` | 修改代码并上线 |

### 处理结果

Claude Code 处理完指令后，通过 Web API 将结果直接发送到你的 QQ，格式为 markdown。

## 隐私说明

- 用户 ID 仅存储在 `config/bot.yaml` 的 `owner_ids` 中
- 运行时会话 ID 仅暂存于 `pending.json`，处理完毕自动删除
- 不记录日志到外部服务
- 不收集任何统计信息
- 信号文件不存在时轮询直接跳过，不浪费 Token

## 文件结构

```
plugins/command_bridge/
├── README.md          # 本说明文件
├── __init__.py
├── main.py            # 插件入口
└── app/
    ├── __init__.py
    └── commands.py     # 队列写入逻辑（仅 20 行）
```
