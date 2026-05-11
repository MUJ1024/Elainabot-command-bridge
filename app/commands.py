"""命令桥接 — 统一任务管理，所有投递放在一个文件中"""

import os
import json
import logging
from datetime import datetime

from core.plugin.decorators import handler

log = logging.getLogger("ElainaBot.plugins.command_bridge.commands")

_ROOT = os.path.dirname(os.path.abspath(__file__))
for _ in range(3):
    _ROOT = os.path.dirname(_ROOT)

_DATA_DIR = os.path.join(_ROOT, 'data', 'command_queue')
_TASKS_FILE = os.path.join(_DATA_DIR, 'tasks.json')
_SIGNAL_FILE = os.path.join(_DATA_DIR, 'pending.json')


def _load_tasks():
    """读取所有任务"""
    if not os.path.exists(_TASKS_FILE):
        return []
    try:
        with open(_TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def _save_tasks(tasks):
    """保存任务列表"""
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def _signal():
    """写信号文件通知 Claude Code"""
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_SIGNAL_FILE, 'w') as f:
        f.write('1')


def _add_task(user_id, text):
    """添加任务"""
    tasks = _load_tasks()
    tid = (tasks[-1]['id'] + 1) if tasks else 1
    tasks.append({
        'id': tid,
        'user_id': user_id,
        'text': text,
        'time': datetime.now().strftime('%m-%d %H:%M'),
        'status': 'pending',
    })
    _save_tasks(tasks)
    _signal()
    return tid


# ==================== 投递指令 ====================

@handler(r'^[！!](.+)$', name='桥接', desc='投递任务给Claude Code',
         owner_only=True, priority=0)
async def bridge_task(event, match):
    """所有带 ! 的消息都作为任务投递"""
    cmd = match.group(1).strip()
    if not cmd:
        return
    tid = _add_task(event.user_id, cmd)
    await event.reply(f'📨 #{tid} 已投递 → 等待处理: `{cmd}`')
    log.info(f'任务 #{tid} 入队: {cmd}')


@handler(r'^[！!]?(tdck|投递查看|投递列表)$', name='投递查看', desc='查看所有已投递的任务',
         owner_only=True, priority=1)
async def list_tasks(event, match):
    tasks = _load_tasks()
    if not tasks:
        await event.reply('📭 暂无投递任务')
        return

    lines = ['', '## 📋 投递列表', '', '---', '']
    for t in tasks:
        sid = str(t['id']).rjust(3)
        status_icon = '⏳' if t['status'] == 'pending' else '✅' if t['status'] == 'done' else '❌'
        text = t['text'][:50] + ('...' if len(t['text']) > 50 else '')
        lines.append(f'> `#{sid}` {status_icon} {t["time"]} {text}')
    lines.extend(['', '---', '', '> 投递删除 <序号> 或 tdsc <序号>'])
    await event.reply('\n'.join(lines), use_markdown=True)


@handler(r'^[！!]?(tdsc|投递删除)\s*(\d+)$', name='投递删除', desc='删除某个投递任务',
         owner_only=True, priority=1)
async def delete_task(event, match):
    tid = int(match.group(2))
    tasks = _load_tasks()
    before = len(tasks)
    tasks = [t for t in tasks if t['id'] != tid]
    if len(tasks) == before:
        await event.reply(f'❌ 未找到 #{tid}')
        return
    _save_tasks(tasks)
    _signal()
    await event.reply(f'🗑️ #{tid} 已删除')


@handler(r'^[！!]?(tdbj|投递编辑)\s*(\d+)\s+(.+)$', name='投递编辑', desc='编辑某个投递任务',
         owner_only=True, priority=1)
async def edit_task(event, match):
    tid = int(match.group(2))
    new_text = match.group(3).strip()
    tasks = _load_tasks()
    for t in tasks:
        if t['id'] == tid:
            t['text'] = new_text
            t['status'] = 'pending'
            _save_tasks(tasks)
            _signal()
            await event.reply(f'✏️ #{tid} 已更新: `{new_text}`')
            return
    await event.reply(f'❌ 未找到 #{tid}')
