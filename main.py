import asyncio
import re
import os

# Web
import requests
from bs4 import BeautifulSoup
from pyppeteer import launch

# Image upscaling
import cv2
from cv2 import dnn_superres

# Images manipulation
from PIL import Image

# Create an SR object
sr = dnn_superres.DnnSuperResImpl_create()

# Read the desired model
path = "models/EDSR_x3.pb"
sr.readModel(path)

# Set CUDA backend and target to enable GPU inference
sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

sr.setModel("edsr", 3)

async def main():
    # Launch the browser
    browser = await launch()

    # Open a new browser page
    page = await browser.newPage()

    # Create a URI for our test file
    page_path = "https://www.artbreeder.com/browse"

    # Open our test file in the opened page
    await page.goto(page_path)
    page_content = await page.content()

    # Process extracted content with BeautifulSoup
    soup = BeautifulSoup(page_content, "html.parser")
    images = soup.find_all("img", {"class": "main_image"})
    for image in images:

        # Get url from parameter
        url = re.search("(?P<url>https?://[^\s]+)", image["style"]).group("url")

        # Clearup
        url = url.replace('");', '').replace('?width=300', '').replace('_small', '')

        # Get filename
        filename = os.path.basename(url)

        # Fetch file
        response = requests.get(url)

        # Save file
        if response.status_code == 200:
            with open("download/" + filename, 'wb') as f:
                f.write(response.content)

                # Read image
                image = cv2.imread("download/" + filename)

                # Upscale the image
                result = sr.upsample(image)

                # Save the image
                cv2.imwrite("download/" + filename, result)

    # Check images folder for broken files
    for filename in os.listdir('download/'):
        if filename.endswith('.jpeg'):
            try:
                img = Image.open('download/'+filename)  # open the image file
                img.verify()  # verify that it is, in fact an image
            except (IOError, SyntaxError) as e:
                print(filename)
                os.remove('download/'+filename)

    # Close browser
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
