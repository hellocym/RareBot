import nonebot
from nonebot import on_command, CommandSession


@on_command('usage', aliases=['使用方法', '帮助', '使用说明'])
async def _(session: CommandSession):
    plugins = list(filter(lambda x: x.name, nonebot.get_loaded_plugins()))

    arg = session.current_arg_text.strip().lower()
    if not arg:
        await session.send(
            '喵现在可以完成这些任务哦：\n\n' + '\n'.join(x.name for x in plugins)
        )
        return

    for p in plugins:
        if p.name.lower() == arg:
            await session.send(p.usage)
