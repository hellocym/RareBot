import asyncio

from playwright.sync_api import Playwright, sync_playwright, expect
import nonebot

class CAIBot:
    def __init__(self, page):
        self.charaid = ""
        self.url = ""
        self.chara_name = ""
        self.page = page

    async def set_id(self, charaid: str) -> str:
        self.charaid = charaid
        self.url = "https://beta.character.ai/chat?char=" + charaid
        await self.page.goto(self.url)
        nonebot.logger.info(self.url)
        # await self.page.get_by_role("button", name="Accept").click()
        # await self.page.get_by_placeholder("Type a message").fill("你好")
        self.chara_name = ""
        while self.chara_name == "":
            handle = await self.page.query_selector('div.chattitle.p-0.pe-1.m-0')
            while not handle:
                handle = await self.page.query_selector('div.chattitle.p-0.pe-1.m-0')
                await asyncio.sleep(0.5)
            self.chara_name = await handle.inner_text()
            await asyncio.sleep(0.5)
        nonebot.logger.info(self.chara_name)
        return self.chara_name

    async def send_msg(self, msg: str) -> None:
        nonebot.logger.info(f"sending msg...{msg}")
        ipt = self.page.get_by_placeholder("Type a message")
        await ipt.fill(msg)
        await ipt.press("Enter")
        nonebot.logger.info("msg sent")
        return

    async def get_msg(self, sleep_time) -> str:
        #xpath = '//*[@id="root"]/div[2]/div/div[3]/div/div/form/div/div/div[2]/button[1]/div'
        #lct = self.page.locator(xpath)
        #await lct.wait_for()
        nonebot.logger.info("getting msg...")
        output_text = ""
        while True:
            await asyncio.sleep(sleep_time)
            div = await self.page.query_selector('div.msg.char-msg')
            if output_text == await div.inner_text():
                break
            output_text = await div.inner_text()
            nonebot.logger.info(output_text)
        return output_text
