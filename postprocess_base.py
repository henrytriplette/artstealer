# Collection of functions migrated from henrytriplette/python-vaporwaveGenerator

import fnmatch
import os
import random
import shutil
from datetime import datetime

from PIL import Image, ImageChops, ImageEnhance, ImageGrab, ImageOps

def saveCanvasAsPng(canvas,root,fileName):
    """
    Save crop of the screen as a way to export canvas content,
    but coordinates are not working correctly
    """
    root_location_x, root_location_y = root.CurrentLocation()

    x = root_location_x + 15 + canvas.winfo_x()
    y = root_location_y + 15 + canvas.winfo_y()

    print(canvas.winfo_x(), canvas.winfo_y())
    print(canvas.winfo_width(), canvas.winfo_height())

    xx = x + canvas.winfo_width()
    yy = y + canvas.winfo_height()

    print(x, y, xx, yy)

    ImageGrab.grab(bbox=(x, y, xx, yy)).save(fileName + '.png', 'png')

def saveThumb(image, path):
    """
    Save small thumbnail for UI preview
    :param img: PIL image object
    :return: PIL image object
    """
    size = 512, 512
    # thumb = image.copy()

    # next 3 lines strip exif
    data = list(image.getdata())
    thumb = Image.new(image.mode, image.size)
    thumb.putdata(data)

    thumb.thumbnail(size)
    if thumb.mode != 'RGBA':
        thumb = thumb.convert('RGBA')
    thumb.save(path, "PNG")

    return path

def openSingleAndCheck(path, resize=False):
    """
    Check if path leads to valid image
    :param img: PIL image object
    :return: PIL image object
    """
    image = Image.open(path)

    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    if image.verify() == False:
        return False

    if resize != False:
        max_size = resize
        original_size = max(image.size[0], image.size[1])
        if original_size >= max_size:
            if (image.size[0] > image.size[1]):
                resized_width = max_size
                resized_height = int(round((max_size/float(image.size[0]))*image.size[1]))
            else:
                resized_height = max_size
                resized_width = int(round((max_size/float(image.size[1]))*image.size[0]))

            image = image.resize((resized_width, resized_height), Image.ANTIALIAS)

    return image

def RandomOpenSingle(folder):
    """
    Given a folder, opens a random image
    :param img: PIL image object
    :return: PIL image object
    """
    # List images
    file_list = []

    for dirpath, dirs, files in os.walk(folder):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_list.append(os.path.join(dirpath,filename))

    filename = random.choice(file_list)

    image = Image.open(filename)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    return image

def SaveImage(image, path):
    """
    Save image as JPEG
    :param img: PIL image object
    :return: Path
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')

    image.save(path, "JPEG")

    return path

def squareImage(image):
    """
    Size aware square crop function
    :param img: PIL image object
    :return: PIL image object
    """
    width, height = image.size

    # square it
    size = min(width, height)

    if width > height:
        delta = width - height
        left = int(delta/2)
        upper = 0
        right = height + left
        lower = height
    else:
        delta = height - width
        left = 0
        upper = int(delta/2)
        right = width
        lower = width + upper

    image = image.crop((left, upper, right, lower))
    image.thumbnail((size, size), Image.ANTIALIAS)

    return image

def medianFilterDenoise(image):
    """
    Denoise Filter
    :param img: PIL image object
    :return: PIL image object
    """
    # Source size
    image_w, image_h = image.size

    members = [(0,0)] * 9

    newimg = Image.new("RGB",(image_w,image_h),"white")
    for i in range(1,image_w-1):
        for j in range(1,image_h-1):
            members[0] = image.getpixel((i-1,j-1))
            members[1] = image.getpixel((i-1,j))
            members[2] = image.getpixel((i-1,j+1))
            members[3] = image.getpixel((i,j-1))
            members[4] = image.getpixel((i,j))
            members[5] = image.getpixel((i,j+1))
            members[6] = image.getpixel((i+1,j-1))
            members[7] = image.getpixel((i+1,j))
            members[8] = image.getpixel((i+1,j+1))
            members.sort()
            newimg.putpixel((i,j),(members[4]))

    return newimg

def normalizeRed(intensity):
    """
    Method to process the red band of the image
    :param img: PIL image object
    :return: PIL image object
    """
    iI      = intensity
    minI    = 86
    maxI    = 230

    minO    = 0
    maxO    = 255

    iO      = (iI-minI)*(((maxO-minO)/(maxI-minI))+minO)
    return iO

def normalizeGreen(intensity):
    """
    Method to process the green band of the image
    :param img: PIL image object
    :return: PIL image object
    """
    iI      = intensity

    minI    = 90
    maxI    = 225

    minO    = 0
    maxO    = 255

    iO      = (iI-minI)*(((maxO-minO)/(maxI-minI))+minO)
    return iO

def normalizeBlue(intensity):
    """
    Method to process the blue band of the image
    :param img: PIL image object
    :return: PIL image object
    """
    iI      = intensity

    minI    = 100
    maxI    = 210

    minO    = 0
    maxO    = 255

    iO      = (iI-minI)*(((maxO-minO)/(maxI-minI))+minO)
    return iO

def contrastStretch(image):
    """
    Contrast image
    :param img: PIL image object
    :return: PIL image object
    """

    # Split the red, green and blue bands from the Image
    multiBands = image.split()

    # Apply point operations that does contrast stretching on each color band
    normalizedRedBand      = multiBands[0].point(normalizeRed)
    normalizedGreenBand    = multiBands[1].point(normalizeGreen)
    normalizedBlueBand     = multiBands[2].point(normalizeBlue)

    # Create a new image from the contrast stretched red, green and blue brands
    image = Image.merge("RGB", (normalizedRedBand, normalizedGreenBand, normalizedBlueBand))

    return image

def cropImageTo(inputImage, outputImage):
    """
    Match two images
    :param img: PIL image object
    :return: PIL image object
    """

    reference_size = outputImage.size
    current_size = inputImage.size
    dx = current_size[0] - reference_size[0]
    dy = current_size[1] - reference_size[1]
    left = dx / 2
    upper = dy / 2
    right = dx / 2 + reference_size[0]
    lower = dy / 2 + reference_size[1]
    return inputImage.crop(box=(int(left), int(upper), int(right), int(lower)))

def imageBrightness(image, factor):
    return ImageEnhance.Brightness(image).enhance(factor)

def imageSharpness(image, factor):
    return ImageEnhance.Sharpness(image).enhance(factor)

def imageColor(image, factor):
    return ImageEnhance.Color(image).enhance(factor)

def imageInvert(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = ImageOps.invert(image)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    return image

def imageRotate(image, angle):
    return image.rotate(angle, resample=Image.BICUBIC, expand=True)

def imageRotate90(image):
    return image.transpose(Image.ROTATE_90)

def imageRotate180(image):
    return image.transpose(Image.ROTATE_180)

def imageRotate270(image):
    return image.transpose(Image.ROTATE_270)

def imageFlipLeftRight(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)

def imageRotateFlipTopBottom(image):
    return image.transpose(Image.FLIP_TOP_BOTTOM)

def imageRollX(image, delta=15):
    xsize, ysize = image.size

    delta = delta % xsize
    if delta == 0: return image

    part1 = image.crop((0, 0, delta, ysize))
    part2 = image.crop((delta, 0, xsize, ysize))
    image.paste(part1, (xsize-delta, 0, xsize, ysize))
    image.paste(part2, (0, 0, xsize-delta, ysize))

    return image

def imageRollY(image, delta=15):
    xsize, ysize = image.size

    delta = delta % ysize
    if delta == 0: return image

    part1 = image.crop((0, 0, xsize, delta))
    part2 = image.crop((0, delta, xsize, ysize))
    image.paste(part1, (0, ysize-delta, xsize, ysize))
    image.paste(part2, (0, 0, xsize, ysize-delta))

    return image

def calculateAspectRatio(image):
    return image

def addToAspectRatio(image, ratio_y, ratio_x):
    """
    Reshapes an image to the specified ratio by cropping along the larger
    dimension that doesn't meet the specified aspect ratio.
    Adds black background if needed.
    """
    original_size = image.size

    width = original_size[0]
    height = original_size[0] * ratio_x / ratio_y
    upper = (original_size[1] - height) / 2
    box = (0, upper, width, upper + height)

    cropped_image = image.crop(box)
    return cropped_image

def cropToAspectRatio(image, ratio_x, ratio_y):
    """
    Reshapes an image to the specified ratio by cropping along the larger
    dimension that doesn't meet the specified aspect ratio.
    """

    def crop_height(image, rx):
        width, height = image.size
        return image.crop((
            0, (rx/2),
            width, height - (rx/2),
        ))

    def crop_width(image, rx):
        width, height = image.size
        return image.crop((
            (rx/2), 0,
            width - (rx/2), height,
        ))

    width, height = image.size

    # Find the delta change.
    rxheight = ((width / ratio_x) * ratio_y) - height
    rxwidth  = ((height / ratio_y) * ratio_x) - width

    # Can only crop pixels, not add them.
    if rxheight < 0 and rxwidth < 0:
        # If both sides can be cropped to get what we want:
        # Select the largest (because both are negative)
        if rxheight > rxwidth:
            return crop_height(image, rxheight * -1)
        else:
            return crop_width(image, rxwidth * -1)

    elif rxheight < 0:
        # Trim height to fit aspect ratio
        return crop_height(image, rxheight * -1)

    elif rxwidth < 0:
        # Trim width to fit aspect ratio
        return crop_width(image, rxwidth * -1)

    else:
        # Can't do anything in this case
        return image

def hueChange(img, intensity = 0.5, value = 180):
    """
    Change to purple/green hue
    :param img: PIL image object
    :param intensity: float > 0.1, larger the value, the less intense and more washout
    :param value: float, the colour to hue change too on a scale from -360 to 0
    :return: PIL image object
    """
    original_width, original_height = img.size

    # Don't apply hue change if already grayscaled.
    if img.mode == 'L':
        return img

    else:
        ld = img.load()
        for y in range(original_height):
            for x in range(original_width):
                r, g, b = ld[x, y]
                h, s, v = rgb_to_hsv(r/255, g/255, b/255)
                h = (h + value/360.0) % 1.0
                s = s**intensity
                r, g, b = hsv_to_rgb(h, s, v)
                ld[x, y] = (int(r * 255.9999), int(g * 255.9999), int(b * 255.9999))
    return img

def convertGrayscale(img):
    """
    Soft black and white filter
    :param img: PIL image object
    :return: PIL image object
    """
    return img.convert('L')

def convertHardBlackAndWhite(img):
    """
    Harsh black and white filter
    :param img: PIL image object
    :return: PIL image object
    """
    # black and white
    gray_img = img.convert('L')
    bw_img = gray_img.point(lambda x: 0 if x < 128 else 255, '1')
    bw_img = bw_img.convert('RGB')
    return bw_img

# Apply a smooth filter to the image to smooth edges (blurs)
def smoothImage(img):
    """
    Soften image
    :param img: PIL image object
    :return: PIL image object
    """
    img = img.filter(ImageFilter.SMOOTH)
    return img

def pasteWithMask(image, imageCopy):
    # Source size
    image_w, image_h = image.size

    # Load mask
    maskimage = Image.open('gui/temp/mask.png').resize((image_w, image_h))
    maskimage_w, maskimage_h = maskimage.size

    # Create intermediate container for mask
    mask = Image.new('L', image.size, 0)

    # Center loaded image inside new background
    offset = ((image_w - maskimage_w)//2, (image_h - maskimage_h)//2)
    mask.paste(maskimage, offset)

    # Convert and correct background
    mask = mask.convert('L')

    # Composite regular image and flipped image with newly sized mask
    output = Image.composite(image, imageCopy, mask)

    return output

def resize_and_crop(img_path, modified_path, size, crop_type='middle'):
    """
    Resize and crop an image to fit the specified size.

    args:
    img_path: path for the image to resize.
    modified_path: path to store the modified image.
    size: `(width, height)` tuple.
    crop_type: can be 'top', 'middle' or 'bottom', depending on this
    value, the image will cropped getting the 'top/left', 'middle' or
    'bottom/right' of the image to fit the size.
    raises:
    Exception: if can not open the file in img_path of there is problems
    to save the image.
    ValueError: if an invalid `crop_type` is provided.
    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(img_path)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], int(round(size[0] * img.size[1] / img.size[0]))),
            Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, int(round((img.size[1] - size[1]) / 2)), img.size[0],
                int(round((img.size[1] + size[1]) / 2)))
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((int(round(size[1] * img.size[0] / img.size[1])), size[1]),
            Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = (int(round((img.size[0] - size[0]) / 2)), 0,
                int(round((img.size[0] + size[0]) / 2)), img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]),
            Image.ANTIALIAS)
    # If the scale is the same, we do not need to crop
    img.save(modified_path)
