from PIL import Image
import numpy as np

CHAR_HALF_BLOCK = chr(9604)

def print_double(image, width, height):
    resized_image = image.resize((width, height), resample=Image.LANCZOS)
    pixels = np.array(resized_image)

    s = ""
    for y in range(0, height - 1, 2):
        if s:
            s += "\033[0m\n"  # Reset colors
        for x in range(width):
            p1 = pixels[y][x]
            p2 = pixels[y + 1][x]
            r1, g1, b1 = p1[0], p1[1], p1[2]
            r2, g2, b2 = p2[0], p2[1], p2[2]
            gray1 = int(0.2126 * r1 + 0.7152 * g1 + 0.0722 * b1)
            gray2 = int(0.2126 * r2 + 0.7152 * g2 + 0.0722 * b2)
            color_index1 = int(gray1 / 256 * len(CHAR_HALF_BLOCK))
            color_index2 = int(gray2 / 256 * len(CHAR_HALF_BLOCK))
            s += f"\033[48;2;{r1};{g1};{b1};38;2;{r2};{g2};{b2}m{CHAR_HALF_BLOCK[color_index1]}{CHAR_HALF_BLOCK[color_index2]}"
    
    s += "\033[0m"  # Reset colors
    return s

def img_to_console(filename, width, height):
    image = Image.open(filename)
    output = print_double(image, width, height)
    print(output)
