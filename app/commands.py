"""命令桥接 — 将 ! 前缀指令写入固定信号文件"""

import os
import json
import logging
from datetime import datetime

from core.plugin.decorators import handler

log = logging.getLogger("ElainaBot.plugins.command_bridge.commands")

_ROOT = os.path.dirname(os.path.abspath(__file__))
for _ in range(3):
    _ROOT = os.path.dirname(_ROOT)

_QUEUE_DIR = os.path.join(_ROOT, 'data', 'command_queue')
_SIGNAL_FILE = os.path.join(_QUEUE_DIR, 'pending.json')


@handler(r'^[！!](.+)$', name='桥接', desc='将指令写入信号文件', owner_only=True, priority=0)
async def bridge_to_claude(event, match):
    cmd = match.group(1).strip()
    if not cmd:
        return
    os.makedirs(_QUEUE_DIR, exist_ok=True)
    with open(_SIGNAL_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'user_id': event.user_id,
            'time': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'text': cmd,
        }, f, ensure_ascii=False)
    await event.reply(f'📨 已投递 → 等待处理: `{cmd}`')
    log.info(f'指令入队: {cmd}')
