import os
import string
import random

# Generate randoms string
def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# random float with step
def randrange_float(start, stop, step):
    return random.randint(0, int((stop - start) / step)) * step + start

# Check for directories
def checkDirectory():
    if not os.path.exists('download'):
        os.makedirs('download', exist_ok=False)
    if not os.path.exists('temp'):
        os.makedirs('temp', exist_ok=False)
    if not os.path.exists('processed'):
        os.makedirs('processed', exist_ok=False)
