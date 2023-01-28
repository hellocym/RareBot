from .hardstyle import HardstyleRelease
from datetime import datetime

import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError


# 每小时更新下专辑信息
@nonebot.scheduler.scheduled_job('cron', hour='*')
async def _():
    release = HardstyleRelease()
    await release.get_releases()
    
