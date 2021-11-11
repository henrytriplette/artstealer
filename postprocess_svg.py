import random

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

import postprocess_utility

def generateFlowImageArgs(inputFile, outputFile):

    values = {
        'vfi_noise_coeff': postprocess_utility.randrange_float(0.001, 0.010, 0.001), # Simplex noise coordinate multiplier. The smaller, the smoother the flow field.
        'vfi_n_fields': random.randint(1, 3), # Number of rotated copies of the flow field
        'vfi_min_sep': postprocess_utility.randrange_float(0.4, 1.6, 0.1), # Minimum flowline separation
        'vfi_max_sep': postprocess_utility.randrange_float(5, 20, 0.1), # Maximum flowline separation
        'vfi_min_length': random.randint(0, 10), # FLOAT 'Minimum flowline length'
        'vfi_max_length': random.randint(30, 60),   # FLOAT 'Maximum flowline length'
        'vfi_max_size': 1086,  # INTEGER 800 'The input image will be rescaled to have sides at most max_size px'
        'vfi_search_ef': random.randint(40, 80),   # INTEGER 'HNSWlib search ef (higher -> more accurate, but slower)'
        'vfi_seed': random.randint(0,10000),   # INTEGER 'PRNG seed (overriding vpype seed)'
        'vfi_flow_seed': random.randint(0,10000),   # INTEGER 'Flow field PRNG seed (overriding the main --seed)'
        'vfi_test_frequency': random.randint(1,5),  # INTEGER 'Number of separation tests per current flowline separation'
        'vfi_field_type': random.choice(['noise','curl_noise']),  # STRING 'Number of separation tests per current flowline separation'
        'vfi_transparent_val': random.randint(125,130), # INTEGER 'Value to replace transparent pixels'
        'vfi_edge_field_multiplier': postprocess_utility.randrange_float(1, 5, 0.1),  # FLOAT 'Flow along image edges'
        'vfi_dark_field_multiplier': postprocess_utility.randrange_float(1, 5, 0.1), # FLOAT 'Flow swirling around dark image areas'
    }

    # Generate parameters
    args = 'vpype flow_img'
    args += ' --noise_coeff ' + str(values['vfi_noise_coeff']) #  Simplex noise coordinate multiplier. The smaller, the smoother the flow field.
    # args += ' --n_fields ' + str(int(values['vfi_n_fields'])) # Number of rotated copies of the flow field
    # args += ' --min_sep ' + str(values['vfi_min_sep']) # Minimum flowline separation  [default: 0.8]
    # args += ' --max_sep ' + str(values['vfi_max_sep']) # Maximum flowline separation  [default: 10]
    args += ' --min_length ' + str(values['vfi_min_length']) # Minimum flowline length  [default: 0]
    args += ' --max_length ' + str(values['vfi_max_length']) # Maximum flowline length  [default: 40]
    # args += ' --max_size ' + str(int(values['vfi_max_size'])) # The input image will be rescaled to have sides at most max_size px  [default: 800]
    # args += ' --search_ef ' + str(int(values['vfi_search_ef'])) # HNSWlib search ef (higher -> more accurate, but slower)  [default: 50]
    args += ' --seed ' + str(int(values['vfi_seed'])) # PRNG seed (overriding vpype seed)
    # args += ' --flow_seed ' + str(int(values['vfi_flow_seed'])) # Flow field PRNG seed (overriding the main `--seed`)
    # args += ' --test_frequency ' + str(values['vfi_test_frequency']) # Number of separation tests per current flowline separation  [default: 2]
    # args += ' --field_type ' + str(values['vfi_field_type']) #
    # args += ' --transparent_val ' + str(int(values['vfi_transparent_val'])) #
    # args += ' --edge_field_multiplier ' + str(values['vfi_edge_field_multiplier']) #
    # args += ' --dark_field_multiplier ' + str(values['vfi_dark_field_multiplier']) #
    args += ' "' + str(inputFile) + '"' # Input
    args += ' write "' + str(outputFile) + '"' # Output

    return args

def generateSvgPreview(inputFile, outputFile):

    drawing = svg2rlg(inputFile)
    renderPM.drawToFile(drawing, outputFile, fmt="PNG")


def generateHpglConversionArgs(inputFile, outputFile, values):

    # Scale svg to desired paper size
    args = 'vpype'
    args += ' read "' + str(inputFile) + '"'; #Read input svg

    if (values['page_orientation'] == 'landscape'):
        if (values['page_scale'] == 'a3'):
            args += ' scaleto 39cm 26.7cm'
        elif (values['page_scale'] == 'a4'):
            args += ' scaleto 27.7cm 19cm'
    else:
        if (values['page_scale'] == 'a3'):
            args += ' scaleto 27.7cm 40cm'
        elif (values['page_scale'] == 'a4'):
            args += ' scaleto 19cm 27.7cm'

    args += ' write --device hp7475a'

    args += ' --page-size ' + str(values['utility_pageSize'])

    if (values['page_orientation'] == 'landscape'):
        args += ' --landscape'

    args += ' --center';
    args += ' "' + str(outputFile) + '"'

    return args
