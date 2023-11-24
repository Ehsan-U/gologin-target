# import asyncio
# from playwright.async_api import async_playwright
# from gologin import GoLogin
# from dotenv import load_dotenv
# import os

# load_dotenv()
# token = os.getenv("GOLOGIN_KEY")


# async def main():
#     gl = GoLogin({
# 		"token": token,
# 		"profile_id": "6560230e80b42ffc40ce9c32",
# 		})

#     debugger_address = gl.start()
#     async with async_playwright() as p:
#         browser = await p.chromium.connect_over_cdp("http://"+debugger_address)
#         default_context = browser.contexts[0]
#         page = default_context.pages[0]
#         # block images
#         await page.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
#         await page.goto("https://login.target.com/gsp/static/v1/login/?client_id=ecom-ios-1.0.0")
#         await page.screenshot(path="gologin.png")
#         await page.close()
#     gl.stop()

# asyncio.get_event_loop().run_until_complete(main())
import pandas as pd
from pprint import pprint
from dataclasses import dataclass

@dataclass
class Account:
    username: str
    password: str
    codes: list


df = pd.read_excel('data.xlsx')
accounts = assign_codes(df)
pprint(accounts)