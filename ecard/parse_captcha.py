import sys
import os
import re
from PIL import Image

def erase_block(filename):
    """Make little black block
    """
    img = Image.open(filename)
    pixdata = img.load()

    
    for y in xrange(img.size[1]):
        pixdata[0, y] = (255, 255, 255)
        pixdata[10, y] = (255, 255, 255)
        pixdata[19, y] = (255, 255, 255)
        pixdata[28, y] = (255, 255, 255)
        pixdata[img.size[0]-1,y] = (255, 255, 255)
        pixdata[img.size[0]-2,y] = (255, 255, 255)
        pixdata[img.size[0]-3,y] = (255, 255, 255)
        pixdata[img.size[0]-4,y] = (255, 255, 255)
        pixdata[img.size[0]-5,y] = (255, 255, 255)

    for x in xrange(img.size[0]):
        pixdata[x, 0] = (255, 255, 255)
        pixdata[x, 1] = (255, 255, 255)
        pixdata[x, 2] = (255, 255, 255)
        pixdata[x, img.size[1]-1] = (255, 255, 255)
        pixdata[x, img.size[1]-2] = (255, 255, 255)
        pixdata[x, img.size[1]-3] = (255, 255, 255)

    for y in xrange(1,img.size[1]-1):
        for x in xrange(1,img.size[0]-1):
            if pixdata[x, y][0] > 50 or pixdata[x,y][1] > 50 or pixdata[x,y][2] > 50:   
                # make dark color black
                pixdata[x, y] = (255, 255, 255)
            else:
                # make light color white
                num = 0
                if pixdata[x+1, y][0] > 50 or pixdata[x+1,y][1] > 50 or pixdata[x+1,y][2] > 50:   
                    num += 1
                if pixdata[x-1, y][0] > 50 or pixdata[x-1,y][1] > 50 or pixdata[x-1,y][2] > 50:   
                    num += 1
                if pixdata[x, y+1][0] > 50 or pixdata[x,y+1][1] > 50 or pixdata[x,y+1][2] > 50:   
                    num += 1
                if pixdata[x, y-1][0] > 50 or pixdata[x,y-1][1] > 50 or pixdata[x,y-1][2] > 50:   
                    num += 1
                if (num == 4):
                    pixdata[x, y] = (255, 255, 255)
                else:
                    pixdata[x, y] = (0,0,0)
    img.save("erase_" + filename)



def tesseract(image, args):
    """Decode image with Tesseract  
    """
    # perform OCR
    output_filename = image + ".txt"
    # easiest way to call tesseract
    os.system('tesseract ' + image + ' ' + output_filename + args )
    
    # read in result from output file
    result = open(output_filename+".txt").read()
    os.remove(output_filename+".txt")
    os.remove(image)
    return clean(result)



def clean(s):
    """Standardize the OCR output
    """
    # remove non-alpha numeric text
    return re.sub('[\W]', '', s)

def getstr(filename):
    erase_block(filename)
    #threshold("erase_" + filename)
    return tesseract("erase_" + filename, " -psm 6 digits")

if __name__ == '__main__':
    filename = sys.argv[1]
    print getstr(filename)
