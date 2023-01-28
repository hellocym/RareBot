from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from jieba import posseg

import numpy as np
import datetime

from .data_source import HardstyleRelease

__plugin_name__ = '新歌'
__plugin_usage__ = r"""
Release Hardstyle

使用方式：
    获取下周新歌：
        新歌/hardstyle
    指定时间歌曲：
        新歌 [下周/今天/明天]
    更新数据库：
        更新

示例：
新歌
今天有啥新歌
"""

release = HardstyleRelease()

@on_command('refresh', aliases='更新')
async def refresh(session: CommandSession):
    print("Getting releases...")
    await session.send("拉取专辑信息喵...")
    await release.get_releases()
    print("Done")
    await session.send("拉取完成了喵")

@on_command('hardstyle', aliases=('新歌'))
async def hardstyle(session: CommandSession):
    date = session.current_arg_text.strip() or '下周'
    if date == '今天':
        res = release.get_releases_today()
    elif date == '明天':
        res = release.get_releases_tomorrow()
    elif date == '下周':
        res = release.get_releases_next_week()
    nparray = np.array(res)
    pylist = nparray.tolist()


    if pylist:
        msg = 'Release Hardstyle Upcoming:\n'
        for i in pylist:
            msg += f"""
            Title: {i[0]}
            Label: {i[1]}
            Release date: {i[2].strftime('%d %b %Y')}
            Catalog ID: {i[3]}
            """
    else:
        msg = '喵好像不知道有啥新歌喵...试试更新下数据库喵？（指令：更新）'
    print(msg)
    #str(res)
    # #datetime.datetime.strptime(i[2], '%Y-%m-%d %H:%M:%S')
    #                                          #.date().i[2]
    await session.send(msg)

@on_natural_language(keywords={'新歌'})
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    words = posseg.lcut(stripped_msg)

    date = None
    for word in words:
        if word.flag == 't':
            date = word.word
            break
    return IntentCommand(90.0, 'hardstyle', current_arg=date or '今天')

@on_natural_language(keywords={'更新'})
async def _(session: NLPSession):
    return IntentCommand(90.0, 'refresh')
