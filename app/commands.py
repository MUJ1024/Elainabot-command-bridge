"""命令桥接 — 统一任务管理"""

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
_SIGNAL_FILE = os.path.join(_DATA_DIR, 'p')


def _load():
    if not os.path.exists(_TASKS_FILE):
        return []
    try:
        with open(_TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def _save(tasks):
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def _signal():
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_SIGNAL_FILE, 'w') as f:
        f.write('1')


def _add(user_id, text):
    tasks = _load()
    tid = (tasks[-1]['id'] + 1) if tasks else 1
    tasks.append({'id': tid, 'user_id': user_id, 'text': text,
                  'time': datetime.now().strftime('%m-%d %H:%M'), 'status': 'pending'})
    _save(tasks)
    _signal()
    return tid


def _table(tasks):
    """生成 markdown 表格，序号从1递增"""
    if not tasks:
        return '（无）'
    rows = ['| # | 时间 | 内容 |', '|---|------|------|']
    reverse = list(reversed(tasks))
    for i, t in enumerate(reverse, 1):
        icon = '⏳' if t['status'] == 'pending' else '✅'
        text = t['text'][:45] + ('...' if len(t['text']) > 45 else '')
        rows.append(f'| {i} {icon} | {t["time"]} | {text} |')
    return '\n'.join(rows)


# ==================== 投递 ====================

@handler(r'^[！!](.+)$', name='桥接', desc='投递任务', owner_only=True, priority=0)
async def bridge_task(event, match):
    cmd = match.group(1).strip()
    if not cmd:
        return
    tid = _add(event.user_id, cmd)
    await event.reply(f'📨 #{tid} 已投递 → `{cmd}`')


@handler(r'^[！!]?(tdck|投递查看|投递列表)$', name='投递查看', desc='查看待处理的任务',
         owner_only=True, priority=1)
async def list_pending(event, match):
    """只显示待处理的任务"""
    tasks = _load()
    pending = [t for t in tasks if t['status'] == 'pending']
    if not pending:
        await event.reply('📭 没有待处理的任务')
        return
    lines = ['', '## ⏳ 待处理投递', '', '---', '', _table(pending), '',
             '> 点击下方按钮后输入序号', '']
    btns = [
        [{'text': '🗑️ 删除', 'data': 'tdsc ', 'enter': False},
         {'text': '📋 全部', 'data': '我的投递', 'enter': True}],
    ]
    await event.reply('\n'.join(lines), buttons=btns, use_markdown=True)


@handler(r'^[！!]?(我的投递|tdall)$', name='我的投递', desc='查看所有投递记录（含已处理）',
         owner_only=True, priority=1)
async def list_all(event, match):
    tasks = _load()
    if not tasks:
        await event.reply('📭 暂无投递记录')
        return
    lines = ['', '## 📋 全部投递', '', '---', '', _table(tasks), '']
    btns = [{'text': '⏳ 待处理', 'data': 'tdck', 'enter': True}]
    await event.reply('\n'.join(lines), buttons=[btns], use_markdown=True)


@handler(r'^[！!]?(tdsc|投递删除)\s*(\d+)$', name='投递删除', desc='删除任务',
         owner_only=True, priority=1)
async def delete_task(event, match):
    tid = int(match.group(2))
    tasks = _load()
    before = len(tasks)
    tasks = [t for t in tasks if t['id'] != tid]
    if len(tasks) == before:
        await event.reply(f'❌ 未找到 #{tid}')
        return
    _save(tasks)
    _signal()
    await event.reply(f'🗑️ #{tid} 已删除')


@handler(r'^[！!]?(tdbj|投递编辑)\s*(\d+)\s*(.+)$', name='投递编辑', desc='编辑任务内容',
         owner_only=True, priority=1)
async def edit_task(event, match):
    tid = int(match.group(2))
    new_text = match.group(3).strip()
    if not new_text:
        await event.reply(f'❌ 内容不能为空')
        return
    tasks = _load()
    for t in tasks:
        if t['id'] == tid:
            t['text'] = new_text
            t['status'] = 'pending'
            _save(tasks)
            _signal()
            await event.reply(f'✏️ #{tid} 已更新')
            return
    await event.reply(f'❌ 未找到 #{tid}')
