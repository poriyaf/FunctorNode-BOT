from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from fake_useragent import FakeUserAgent
from datetime import datetime, timedelta, timezone
from colorama import *
import asyncio, json, time, base64, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Functor:
    def __init__(self) -> None:
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'node.securitylabs.xyz',
            'Referer': 'https://node.securitylabs.xyz/?from=extension&type=signin&referralCode=cm4m90eqs763ro81bdrwsehwd',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': FakeUserAgent().random
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Functor Node - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def mask_account(self, account):
        if '@' in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account
            
    
    def decode_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)

            username = parsed_payload['email']
            user_id = parsed_payload['sub']
            exp_time = parsed_payload['exp']

            return self.mask_account(username), user_id, exp_time
        except Exception as e:
            return None, None, None

    async def user_data(self, token: str, retries=5):
        url = 'https://node.securitylabs.xyz/api/v1/users'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
                
    async def user_checkin(self, token: str, user_id: str, retries=5):
        url = f'https://node.securitylabs.xyz/api/v1/users/earn/{user_id}'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return None
        
    async def process_accounts(self, token: str, user_id: str, exp_time: int):
        exp_time_wib = datetime.fromtimestamp(exp_time, pytz.utc).astimezone(wib).strftime('%x %X %Z')
        if int(time.time()) > exp_time:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Token Expired {Style.RESET_ALL}"
            )
            return

        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT} Token Active {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Expired at {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{exp_time_wib}{Style.RESET_ALL}"
        )

        balance = "N/A"
        last_checkin = None

        user = await self.user_data(token)
        if user:
            balance = user.get("dipTokenBalance")
            last_checkin = user.get('dipInitMineTime')

        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {balance} Points {Style.RESET_ALL}"
        )

        if last_checkin is None:
            check_in = await self.user_checkin(token, user_id)
            if check_in:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Reward {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{check_in['tokensToAward']} Points{Style.RESET_ALL}"
                )
            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Isn't Claimed {Style.RESET_ALL}"
                )
        else:
            now = datetime.utcnow().replace(tzinfo=timezone.utc)
            last_checkin_utc = datetime.strptime(last_checkin, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            next_checkin_utc = last_checkin_utc + timedelta(hours=24)
            next_checkin_wib = next_checkin_utc.astimezone(wib).strftime('%x %X %Z')
            if now >= next_checkin_utc:
                check_in = await self.user_checkin(token, user_id)
                if check_in:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Reward {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{check_in['tokensToAward']} Points{Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Isn't Claimed {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Is Already Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Next Claim at {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{next_checkin_wib}{Style.RESET_ALL}"
                )

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
                )
                
                separator = "=" * 25
                for token in tokens:
                    if token:
                        username, user_id, exp_time = self.decode_token(token)
                        if username and user_id and exp_time:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                            )
                            await self.process_accounts(token, user_id, exp_time)
                            await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}" * 75)
                seconds = 12 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' tidak ditemukan.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Functor()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Functor Node - BOT{Style.RESET_ALL}                                       "                              
        )