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

# Image upscaling
import cv2
from cv2 import dnn_superres

def fetchFromArtBreeder(page_content, arguments):

    # Process extracted content with BeautifulSoup
    soup = BeautifulSoup(page_content, "html.parser")
    images = soup.find_all("img", {"class": "main_image"})

    images = images[-int(arguments.total):]    # Will hold only last 10 images

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

def fetchFromInstagram(page_content, arguments):

    # Process extracted content with BeautifulSoup
    soup = BeautifulSoup(page_content, "html.parser")
    images = soup.find_all("img", srcset=True)

    images = images[-int(arguments.total):]    # Will hold only last 10 images

    for image in images:
        # Skip logo image
        if not re.search("logo", image['srcset']):

            urls = image['srcset'].split('480w,')
            print(urls)
            if (len(urls) > 0):
                url = urls[1].replace(' 640w', '')

                # Get filename
                filename = os.path.basename(url).split('.jpg?')
                print(filename)
                # Fetch file
                response = requests.get(url)

                # Save file
                if response.status_code == 200:
                    with open("download/" + filename[0] + '.jpeg', 'wb') as f:
                        f.write(response.content)
