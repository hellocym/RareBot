from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from jieba import posseg

import numpy as np
import datetime

from .data_source import HardstyleRelease

release = HardstyleRelease()

@on_command('refresh', aliases='更新')
async def refresh(sessiom: CommandSession):
    print("Getting releases...")

    await release.get_releases()
    print("Done")

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

    msg = 'Release Hardstyle Upcoming:'
    for i in pylist:
        msg += f"""
        Title: {i[0]}
        Label: {i[1]}
        Release date: {i[2].strftime('%d %b %Y')}
        Catalog ID: {i[3]}
        """
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
