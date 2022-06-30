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

# Images manipulation
from PIL import Image

# Google Drive upload
# from pydrive2.auth import GoogleAuth
# from pydrive2.drive import GoogleDrive

# Custom
import postprocess_base
import postprocess_fetch
import postprocess_utility
import postprocess_svg

# Read Configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Create an SR object
sr = dnn_superres.DnnSuperResImpl_create()

# Read the desired model
path = "models/EDSR_x3.pb"
sr.readModel(path)

# Set CUDA backend and target to enable GPU inference
sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

sr.setModel("edsr", 3)

# # Google Drive
# drive = False
# if config['upload']['googledrive'] == True:
#    # Below code does the authentication
#     gauth = GoogleAuth()
#
#     # Creates local webserver and auto handles authentication.
#     gauth.LocalWebserverAuth()
#     drive = GoogleDrive(gauth)

# Main function
async def main(arguments):

    ext_input = [".jpg", ".jpeg", ".png"]

    # Directory checks
    postprocess_utility.checkDirectory()

    # Clear Start
    for filename in os.listdir('temp/'):
        if filename != '.gitkeep':
            try:
                os.remove('temp/'+filename)
            except (IOError, SyntaxError) as e:
                print(filename)

    if arguments.fetch == True:
        for filename in os.listdir('download/'):
            if filename.endswith(tuple(ext_input)):
                try:
                    os.remove('download/'+filename)
                except (IOError, SyntaxError) as e:
                    print(filename)

        # Launch the browser
        browser = await launch()

        # Open a new browser page
        page = await browser.newPage()

        # Create a URI for our test file
        page_path = "https://www.artbreeder.com/browse"
        # page_path = "https://www.instagram.com/henrytriplette"

        # Open our test file in the opened page
        await page.goto(page_path)
        page_content = await page.content()

        # Close browser
        await browser.close()

        postprocess_fetch.fetchFromArtBreeder(page_content, arguments)
        # postprocess_fetch.fetchFromInstagram(page_content, arguments)

    # Check images folder for broken files
    for filename in os.listdir('download/'):
        if filename.endswith(tuple(ext_input)):
            try:
                image = Image.open('download/'+filename)  # open the image file
                image.verify()  # verify that it is, in fact an image

            except (IOError, SyntaxError) as e:
                print(filename)
                os.remove('download/'+filename)

    # Postprocessing Upscale
    if arguments.upscale == True:
        for filename in os.listdir('download/'):
            if filename.endswith(tuple(ext_input)):

                # Read image
                image = cv2.imread("download/" + filename)

                # Upscale the image
                result = sr.upsample(image)

                # Save the image
                cv2.imwrite("download/" + filename, result)

    # Postprocessing
    for filename in os.listdir('download/'):
        if filename.endswith(tuple(ext_input)):
            try:
                image = Image.open('download/'+filename)  # open the image file

                # Convert to RGBA
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                # Scale image to instagram size
                image = postprocess_base.resize_and_crop(image, [1086, 1536])

                # Image postprocessing
                # image = postprocess_base.contrastStretch(image)
                image = postprocess_base.imageSharpness(image, 1.25)
                image = postprocess_base.imageFlipLeftRight(image)

                # Save the processed image
                single_datestring = datetime.strftime(datetime.now(), '%Y-%m-%d_%H.%M.%S')
                photo_path = '%s/%s_%s_single.jpg' % ('temp', single_datestring, postprocess_utility.id_generator(8))
                filename = postprocess_base.SaveImage(image, photo_path)
                print('Saved ' + photo_path)
            except (IOError, SyntaxError) as e:
                print(filename)

    # Conversion to CMYK Split
    if arguments.color == True:
        for filename in os.listdir('temp/'):
            if filename.endswith('.jpg'):
                try:
                    name, extension = os.path.splitext(filename)

                    inputFile = 'temp/' + filename
                    outputFile = 'temp/' + filename

                    args = postprocess_svg.generateCmykSplit(inputFile, True)

                    rendering = subprocess.Popen(args)
                    rendering.wait() # Hold on till process is finished

                    print('CMYK ' + outputFile)
                except (IOError, SyntaxError) as e:
                    print(filename)

        flowargs = postprocess_svg.generateFlowArgs()

    # Conversion to SVG
    for filename in os.listdir('temp/'):
        if filename.endswith('.jpg'):
            try:
                name, extension = os.path.splitext(filename)

                inputFile = 'temp/' + filename
                outputFile = 'temp/' + name + '.svg'

                # Randomize flowargs only if color is false
                if arguments.color == False:
                    flowargs = postprocess_svg.generateFlowArgs()

                args = postprocess_svg.generateFlowImageArgs(inputFile, outputFile, flowargs)

                rendering = subprocess.Popen(args)
                rendering.wait() # Hold on till process is finished

                print('Processed ' + outputFile)
            except (IOError, SyntaxError) as e:
                print(filename)

    # Conversion to HPGL
    for filename in os.listdir('temp/'):
        if filename.endswith('.svg'):
            try:
                name, extension = os.path.splitext(filename)

                inputFile = 'temp/' + filename
                outputFile = 'temp/' + name + '.svg'

                # Optimize file
                args = 'vpype read "'
                args += str(inputFile) + '"'
                args += ' linemerge --tolerance 0.1mm linesort'
                args += ' write "' + str(outputFile) + '"'

                rendering = subprocess.Popen(args)
                rendering.wait() # Hold on till process is finished

                print('Optimized ' + outputFile)

                # Generate preview
                inputFile = 'temp/' + name + '.svg'
                outputFile = 'temp/' + name + '.png'

                postprocess_svg.generateSvgPreview(inputFile, outputFile)

                print('Preview ' + outputFile)

                # Generate hpgl
                inputFile = 'temp/' + name + '.svg'
                outputFile = 'temp/' + name + '.hpgl'

                args = postprocess_svg.generateHpglConversionArgs(inputFile, outputFile, config['hpgl'])

                rendering = subprocess.Popen(args)
                rendering.wait() # Hold on till process is finished

                print('Converted ' + outputFile)

            except (IOError, SyntaxError) as e:
                print(filename)

    # Move to processed
    for filename in os.listdir('temp/'):
        if filename != '.gitkeep':
            try:
                os.rename('temp/' + filename, 'processed/' + filename)
            except (IOError, SyntaxError) as e:
                print(filename)

    # # Upload all files
    # if config['upload']['googledrive'] == True
    #     for filename in os.listdir('processed/'):
    #         if filename != '.gitkeep':
    #             try:
    #                 f = drive.CreateFile({'title': filename})
    #                 f.SetContentFile(os.path.join('processed/', filename))
    #                 f.Upload()
    #
    #                 # Due to a known bug in pydrive if we
    #                 # don't empty the variable used to
    #                 # upload the files to Google Drive the
    #                 # file stays open in memory and causes a
    #                 # memory leak, therefore preventing its
    #                 # deletion
    #                 f = None
    #             except (IOError, SyntaxError) as e:
    #                 print(filename)

    # Clearup
    if arguments.fetch == True:
        for filename in os.listdir('download/'):
            if filename.endswith(tuple(ext_input)):
                try:
                    os.remove('download/'+filename)
                except (IOError, SyntaxError) as e:
                    print(filename)

if __name__ == '__main__':

    # Initialize
    parser = argparse.ArgumentParser(description='Fetch some images, and process them.')
    parser.add_argument('--fetch', dest='fetch', action='store_true', help='Download new images')
    parser.add_argument('--total', dest='total', type=int, default=10, help='Download how many images?')
    parser.add_argument('--no-fetch', dest='fetch', action='store_false', help='Use images already in download folder')
    parser.add_argument('--upscale', dest='upscale', action='store_true', help='Upscale images using AI?')
    parser.add_argument('--color', dest='color', action='store_true', help='Split Images for CMYK print')

    parser.set_defaults(fetch=True, upscale=False, color=False, total=10)

    arguments = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main(arguments))
