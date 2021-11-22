import asyncio
import re
import os
import time
import random
import configparser
import subprocess
import argparse

from datetime import datetime

# Web
import requests
from bs4 import BeautifulSoup
from pyppeteer import launch

# Main function
async def main(arguments):
    # Launch the browser
    browser = await launch()

    # Open a new browser page
    page = await browser.newPage()

    # Create a URI for our test file
    page_path = "https://www.instagram.com/bunnie.han"

    # Open our test file in the opened page
    await page.goto(page_path)
    page_content = await page.content()

    # Close browser
    await browser.close()

    # Process extracted content with BeautifulSoup
    soup = BeautifulSoup(page_content, "html.parser")
    images = soup.find_all("img", srcset=True)

    images = images[-10:]    # Will hold only last 10 images

    for image in images:
        # Skip logo image
        if not re.search("logo", image['srcset']):

            urls = image['srcset'].split('480w,')

            if (len(urls) > 0):
                url = urls[1].replace(' 640w', '')

                # Get filename
                filename = os.path.basename(url).split('.jpg?')

                # Fetch file
                response = requests.get(url)

                # Save file
                if response.status_code == 200:
                    with open("download/" + filename[0] + '.jpeg', 'wb') as f:
                        f.write(response.content)

if __name__ == '__main__':

    # Initialize
    parser = argparse.ArgumentParser(description='Fetch some images, and process them.')
    arguments = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(arguments))
