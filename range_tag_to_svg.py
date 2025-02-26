#!/usr/bin/env python3

import os, argparse, re
from PIL import Image

# Thanks to https://stackoverflow.com/a/54547257
def dir_path(file_path):
    if os.path.isfile(file_path):
        return file_path
    else:
        raise argparse.ArgumentTypeError(f'Supplied argument "{file_path}" is not a valid file path.')


parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(
    description='A script to convert pre-generated apriltag .png files into SVG format.',
    epilog='Example: "python tag_to_svg.py tagStandard52h13/tag52_13_00007.png tag52_13_00007.svg --size=20mm"'
)
parser.add_argument(
    'tag_file', type = str,
    help='The path to the apriltag png you want to convert.'
)
parser.add_argument(
    '--size', type=str, required=False, default='20mm', dest="svg_size", 
    help='The size (edge length) of the generated svg such as "20mm" "2in" "20px"'
)
parser.add_argument(
    '--start', type = int, required = True, dest = "start_id",
    help = "The id of the april tag you want to start at."
)
parser.add_argument(
    '--end', type = int, required = True, dest = "end_id",
    help = "The id of the april tag you want to end at (not inclusive)"
)

def gen_apriltag_svg(width, height, pixel_array, size):
    def gen_rgba(rbga):
        (_r, _g, _b, _raw_a) = rbga
        _a = _raw_a / 255
        return f'rgba({_r}, {_g}, {_b}, {_a})'

    def gen_gridsquare(row_num, col_num, pixel):
        _rgba = gen_rgba(pixel)
        _id = f'box{row_num}-{col_num}'
        return f'\t<rect width="1" height="1" x="{row_num}" y="{col_num}" fill="{_rgba}" id="{_id}"/>\n'

    svg_text = '<?xml version="1.0" standalone="yes"?>\n'
    svg_text += f'<svg width="{size}" height="{size}" viewBox="0,0,{width},{height}" xmlns="http://www.w3.org/2000/svg">\n'
    for _y in range(height):
        for _x in range(width):
            svg_text += gen_gridsquare(_x, _y, pixel_array[_x, _y])
    svg_text += '</svg>\n'

    return svg_text

def main():
    args = parser.parse_args()
    tag_file = args.tag_file
    svg_size = args.svg_size
    start_id = args.start_id
    end_id = args.end_id

    for i in range(start_id, end_id):
        str_id = str(i)

        while len(str_id) < 5:
            str_id = "0" + str_id

        number_types = re.findall(r"\d+", tag_file)
        file_name = "tag"

        for i in range(len(number_types)):
            while len(number_types[i]) < 2:
                number_types[i] = "0" + number_types[i]

            file_name += number_types[i] + "_"

        file_name += str_id + ".png"
        full_path = os.path.join(tag_file, file_name)

        apriltag_svg = None

        with Image.open(full_path, 'r') as im:

            width, height = im.size
            pix_vals = im.load()

            apriltag_svg = gen_apriltag_svg(width, height, pix_vals, svg_size)

        assert apriltag_svg is not None, 'Error: Failed to create SVG.'

        if not os.path.exists("output"):
            os.makedirs("output")
            print("Created 'output' dir")

        output_file_name = file_name[:-4] + ".svg"
        output_path = os.path.join("output", output_file_name)

        with open(output_path, 'w') as fp:
            fp.write(apriltag_svg)

        print(f'Output SVG file: {output_path} with size: {svg_size}')

if __name__ == "__main__":
    main()
