import asyncio
from pyppeteer import launch
from database import Database


class PyppeteerScraper:
    LAUNCH_OPTIONS = {
        "headless": True,
        "ignoreHTTPSErrors": True,
        "args": [
            "--unlimited-storage",
            "--full-memory-crash-report",
            "--disable-gpu",
            "--ignore-certificate-errors",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--lang=en-US;q=0.9,en;q=0.8",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        ],
    }
    MAIN_URL = "https://auto.ria.com/car/used/"
    TIMEOUT = 0
    OPTIONS = {"waitUntil": "load", "timeout": TIMEOUT}
    ALL_AUTO_URL = []
    ALL_CAR_PATH = "a.address"
    TITLE = "h1.head"
    PRICE = "//div[@class='price_value']/strong/text()"
    IMG = '//div[contains(@class, "carousel-inner")]/div[1]//img/@src'
    MILE_AGE = "/html/body/div[6]/div[11]/div[4]/aside/section[1]/div[3]"
    USERNAME = "/html/body/div[6]/div[11]/div[4]/aside/section[2]/div[1]/div/h4"
    PHONE = "/html/body/div[12]/div/div[2]/div[2]/div[2]"
    PHONE_POP_WINDOW = "a.size14.phone_show_link.link-dotted.mhide"
    TOTAL_IMAGE_COUNT = '//span[@class="count"]/span[@class="mhide"]/text()'
    CAR_NUMBER = "/html/body/div[6]/div[11]/div[4]/main/div[2]/div[2]/div[1]/dl/dd[1]/div[1]/span[1]"
    VIN_CODE = "/html/body/div[6]/div[11]/div[4]/main/div[2]/div[3]/div[1]/dl/dd[1]/div[1]/span"
    ALT_VIN_CODE = "/html/body/div[6]/div[11]/div[4]/main/div[2]/div[2]/div[1]/dl/dd[1]/div[1]/span"
    EVALUATE_HREF_CONVERTER = "(element) => element.href"
    EVALUATE_TEXT_CONVERTER = "(element) => element.textContent"
    NEXT_PAGE = "span.page-item.next.text-r"
    NEXT_PAGE_LINK = "/html/head/link[73]"
    ALL_ITEM = []

    def __init__(self):
        self.page = None
        self.browser = None
        self.database = Database()

    async def next_page(self):
        await self.page.click(self.NEXT_PAGE)
        new_page = await self.page.waitForXPath(self.NEXT_PAGE_LINK)
        new_page_ev = await self.page.evaluate(self.EVALUATE_HREF_CONVERTER, new_page)
        self.MAIN_URL = new_page_ev
        print(self.MAIN_URL)
        self.ALL_AUTO_URL = []
        await self.page.waitForNavigation()

    async def get_current_page_cars(self):
        all_car = await self.page.querySelectorAll(self.ALL_CAR_PATH)
        for car in all_car:
            cars = await self.page.evaluate(self.EVALUATE_HREF_CONVERTER, car)
            self.ALL_AUTO_URL.append(cars)
        print(self.ALL_AUTO_URL)

    async def scraper(self):
        self.browser = await launch(self.LAUNCH_OPTIONS)
        self.page = await self.browser.newPage()
        await self.page.goto(url=self.MAIN_URL, options=self.OPTIONS)

        await self.get_current_page_cars()

        for car_link in self.ALL_AUTO_URL:
            await self.page.goto(url=car_link, options=self.OPTIONS)
            title = await self.page.querySelector(self.TITLE)
            title_ev = await self.page.evaluate(self.EVALUATE_TEXT_CONVERTER, title)
            price = await self.page.waitForXPath(self.PRICE)
            price_ev = await self.page.evaluate(self.EVALUATE_TEXT_CONVERTER, price)
            image = await self.page.waitForXPath(self.IMG)
            image_ev = await self.page.evaluate(self.EVALUATE_TEXT_CONVERTER, image)
            mile_age = await self.page.waitForXPath(self.MILE_AGE)
            mile_age_ev = await self.page.evaluate(self.EVALUATE_TEXT_CONVERTER, mile_age)
            username = await self.page.waitForXPath(self.USERNAME)
            username_ev = await self.page.evaluate(self.EVALUATE_TEXT_CONVERTER, username)
            await self.page.click(self.PHONE_POP_WINDOW)
            try:
                phone = await self.page.waitForXPath(self.PHONE)
                phone_ev = await self.page.evaluate(self.EVALUATE_TEXT_CONVERTER, phone)
            except Exception:
                phone_ev = None
            image_count = await self.page.waitForXPath(self.TOTAL_IMAGE_COUNT)
            image_count_ev = await self.page.evaluate(
                self.EVALUATE_TEXT_CONVERTER, image_count
            )
            try:
                car_number = await self.page.waitForXPath(self.CAR_NUMBER)
                car_number_ev = await self.page.evaluate(
                    self.EVALUATE_TEXT_CONVERTER,
                    car_number
                )
            except Exception:
                car_number_ev = None
            try:
                vin_code = await self.page.waitForXPath(self.VIN_CODE)
                vin_code_ev = await self.page.evaluate(
                    self.EVALUATE_TEXT_CONVERTER,
                    vin_code
                )
            except Exception:
                vin_code_ev = None
            data = (
                car_link,
                title_ev,
                price_ev,
                mile_age_ev,
                username_ev,
                phone_ev,
                image_ev,
                image_count_ev[3:],
                car_number_ev,
                vin_code_ev,
            )
            self.ALL_ITEM.append(data)
            print(data)

        print(f"ALL ITEM: \n {self.ALL_ITEM}")
        self.database.insert_data(self.ALL_ITEM)

        await self.next_page()

    async def main(self):
        await self.scraper()
        new_page = await self.page.waitForXPath(self.NEXT_PAGE_LINK)
        while new_page is not None:
            await self.scraper()
        await self.browser.close()


if __name__ == "__main__":
    scraper = PyppeteerScraper()
    asyncio.get_event_loop().run_until_complete(scraper.main())
