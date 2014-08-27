import sys
import os
import re
import subprocess
import tempfile
from PIL import Image


def parse_captcha(filename):
    """Return the text for thie image using Tesseract
    """
    img = threshold(filename)
    return tesseract(img)


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


def split_block(filename):
    """Make little black block
    """
    img = Image.open(filename)
    pixdata = img.load()

    
    for y in xrange(img.size[1]):
        pixdata[0, y] = (255, 255, 255)
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

    box = (1, 2, 10, 16)
    region = img.crop(box)
    region.save("CROPPED1" + filename)

    box = (10, 2, 20, 16)
    region = img.crop(box)
    region.save("CROPPED2" + filename)

    box = (20, 2, 28, 16)
    region = img.crop(box)
    region.save("CROPPED3" + filename)

    box = (30, 2, 39, 16)
    region = img.crop(box)
    region.save("CROPPED4" + filename)


def threshold(filename, limit=50):
    """Make text more clear by thresholding all pixels above / below this limit to white / black
    """
    # read in colour channels
    img = Image.open(filename)
    # resize to make more clearer
    m = 1
    img = img.resize((int(img.size[0]*m), int(img.size[1]*m))).convert('RGBA')
    pixdata = img.load()

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][0] < limit:
                # make dark color black
                pixdata[x, y] = (0, 0, 0, 255)
            else:
                # make light color white
                pixdata[x, y] = (255, 255, 255, 255)
    img.save('threshold_' + filename)
    return img.convert('L') # convert image to single channel greyscale



def call_command(*args):
    """call given command arguments, raise exception if error, and return output
    """
    c = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = c.communicate()
    if c.returncode != 0:
        if error:
            print error
        print "Error running `%s'" % ' '.join(args)
    return output


def tesseract(image, args):
    """Decode image with Tesseract  
    """
    # perform OCR
    output_filename = image + ".txt"
    #call_command('tesseract', input_file, output_filename, '-psm 10 digits')
    os.system('tesseract ' + image + ' ' + output_filename + args )
    
    # read in result from output file
    result = open(output_filename+".txt").read()
    os.remove(output_filename+".txt")
    os.remove(input_file)
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
    """
    split_block(filename)
    filenames = "CROPPED"
    if filenames:
        for i in range(1,5):
            img = threshold(filenames + str(i) +filename)
            print 'Tesseract:', tesseract("threshold_CROPPED" + str(i) + filename," -psm 10 digits")
    else:
        print 'Usage: %s [image1] [image2] ...' % sys.argv[0]
    """
