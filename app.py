import asyncio
from collections import deque
from playwright.sync_api import sync_playwright
from gologin import GoLogin
from dotenv import load_dotenv
import os
import logging
from dataclasses import dataclass
import pandas as pd
import random


load_dotenv()
logging.basicConfig(level=logging.DEBUG,
    format='=> %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()])
logger = logging.getLogger("Target")
logging.getLogger("pygologin").setLevel(logging.WARNING)



@dataclass
class Account:
    username: str
    password: str
    codes: list



class Target():
    login_url = "https://login.target.com/gsp/static/v1/login/?client_id=ecom-ios-1.0.0"
    token = os.getenv("GOLOGIN_KEY")
    counter = 1
    gl = GoLogin({
        "token": token,
    })


    @staticmethod
    def assign_codes(df):
        all_codes_queue = deque()  
        accounts = {}        

        for _, row in df.iterrows():
            if pd.notnull(row['Email']):
                accounts[row['Email']] = Account(username=row['Email'], password=row['Pass'], codes=[])
            if pd.notnull(row['Codes']):
                all_codes_queue.append(row['Codes'])

        account_queue = deque(acc for acc in accounts.values() if len(acc.codes) < 3)

        while all_codes_queue and account_queue:
            code = all_codes_queue.popleft() 
            account = account_queue.popleft() 
            account.codes.append(code)  

            # If the account can still receive more codes, add it back to the end of the queue
            if len(account.codes) < 3:
                account_queue.append(account)

        return list(accounts.values())


    def create_profile(self):
        logger.info(f"Creating profile {self.counter}")
        system = random.choice(['mac', 'lin', 'win'])
        platform = {"mac": "mac", "win": "Win32", "lin": "Linux x86_64"}.get(system)
        try:
            profile_id = self.gl.create({
                "name": f'{self.counter}_profile',
                "os": system,
                "navigator": {
                    "language": 'en-US',
                    "userAgent": 'random', 
                    "resolution": 'random',
                    "platform": platform,
                },
                'proxyEnabled': True,
                'proxy': {
                    'mode': 'gologin',
                    'autoProxyRegion': 'us' 
                },
                "webRTC": {
                    "mode": "alerted",
                    "enabled": True,
                },
            })
        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            return None
        else:
            self.counter += 1
            logger.debug(f"Profile created with id {profile_id}")
            return profile_id


    def execute_profile(self, id, account):
        if id:
            logger.info(f"Executing profile {id}")
            try:
                self.gl.setProfileId(id)
                debugger_address =  self.gl.start()
                with sync_playwright() as p:
                    browser = p.chromium.connect_over_cdp(f"http://{debugger_address}")
                    default_context = browser.contexts[0]
                    page = default_context.pages[0]
                    # block images
                    page.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
                    page.goto(self.login_url)
                    page.screenshot(path=f"{account.username}.png")
                    page.close()
                self.gl.stop()
            except Exception as e:
                logger.error(f"Error executing profile: {e}")
                return False

    def delete_profile(self, id):
        if id:
            logger.info(f"Deleting profile {id}")
            self.gl.delete(id)


    def run(self):
        if os.path.exists("data.xlsx"):
            df = pd.read_excel("data.xlsx")
            accounts = self.assign_codes(df)
            for account in accounts:
                id = self.create_profile()
                self.execute_profile(id, account)
                self.delete_profile(id)
        else:
            logger.info("Data file not found")



bot = Target()
bot.run()