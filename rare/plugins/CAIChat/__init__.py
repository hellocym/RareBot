from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
import nonebot

import asyncio
from playwright.async_api import Playwright, async_playwright, expect

from .data_source import CAIBot

__plugin_name__ = 'CAI聊天'
__plugin_usage__ = r"""
character.ai聊天

使用方式：
/chat set <id>
/chat list
/chat remake
"""

id_ = ""
bot = None


@on_command('chat')
async def chat(session: CommandSession):
    global id_
    global bot
    args = session.current_arg_text.strip()
    if not args:
        pass
    elif args.startswith('set'):
        # chat set <id>
        id_ = args.split(" ", maxsplit=1)[1:][0]
        nonebot.logger.info(id_)
        if not id_:
            id_ = (await session.aget(prompt='请输入角色id')).strip()
            while not id_:
                id_ = (await session.aget(prompt='角色id不能为空，请重新输入')).strip()
        async with async_playwright() as playwright:
            browser = await playwright.firefox.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            bot = CAIBot(page)
            name = await bot.set_id(id_)
            await session.send(f'设置成功,当前为{name}')
            await page.get_by_role("button", name="Accept").click()
            res = await bot.get_msg(sleep_time=1)
            while True:
                res = (await session.aget(prompt=res)).strip()
                await bot.send_msg(res)
                res = await bot.get_msg(sleep_time=10)
    else:
        if not id_:
            await session.send('请先设置角色id')
            return
        await bot.send_msg(args)
        res = await bot.get_msg()
        while True:
            res = (await session.aget(prompt=res)).strip()
        return
