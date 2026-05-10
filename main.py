"""命令桥接插件 — 将 ! 前缀指令写入队列"""

__plugin_meta__ = {
    'name': '命令桥接',
    'author': 'MUJ1024',
    'description': '将带有 ! 前缀的消息写入队列，供 Claude Code 处理',
    'version': '1.0.0',
    'github': 'https://github.com/MUJ1024/Elainabot-command-bridge',
}

from core.plugin.decorators import on_load, on_unload
from core.base.logger import get_logger, PLUGIN

from plugins.command_bridge.app import commands  # noqa: F401

log = get_logger(PLUGIN, "命令桥接")


@on_load
def _on_load():
    log.info("✅ 命令桥接插件已加载")


@on_unload
def _on_unload():
    log.info("命令桥接插件已卸载")
