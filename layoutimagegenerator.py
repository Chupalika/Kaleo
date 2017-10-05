import sys
import os

flag = False

try:
    import numpy
    import cv2
except ImportError:
    sys.stderr.write("Note: numpy and/or cv2 aren't installed, layout images won't be generated.\n")
    flag = True

def generateLayoutImage(itemlist, itemstatelist, outputname):
    #If numpy and/or cv2 aren't installed, just skip this function
    if flag:
        return

    #Find the item files
    imagefiles = ["../Icons/" + item + ".png" for item in itemlist]
    images = [cv2.imread(img, -1) for img in imagefiles]
    
    #Create an empty image
    rows = len(itemlist) / 6
    height = 256*rows
    width = 256*6
    output = numpy.zeros((height, width, 4))
    
    #Fill up the image with the item files
    x = 0
    y = 0
    for image in images:
        if image is not None:
            output[y:y+256,x:x+256] = image
        else:
            unknown = cv2.imread("Unknown.png", -1)
            output[y:y+256,x:x+256] = unknown
        x += 256
        if (x >= 256*6):
            x = 0
            y += 256
    
    #Find the item state files
    imagefiles2 = ["../Icons/" + item + ".png" for item in itemstatelist]
    images2 = [cv2.imread(img, -1) for img in imagefiles2]
    
    #Create an empty image (this will be the disruption overlay)
    overlay = numpy.zeros((height, width, 4))
    
    #Fill up the image with Barriers and Black Clouds
    x = 0
    y = 0
    for image in images2:
        if image is not None:
            overlay[y:y+256,x:x+256] = image
        x += 256
        if (x >= 256*6):
            x = 0
            y += 256
    
    #shrink the output and merge it with disruption overlay
    shrinkfactor = 4
    output = cv2.resize(output, (width/shrinkfactor, height/shrinkfactor), interpolation = cv2.INTER_AREA)
    overlay = cv2.resize(overlay, (width/shrinkfactor, height/shrinkfactor), interpolation = cv2.INTER_AREA)
    output = mergeimages(output, overlay)
    
    #draw a grid
    border = numpy.zeros((output.shape[0]+2, output.shape[1]+2, output.shape[2]))
    border[1:output.shape[0]+1,1:output.shape[1]+1] = output
    output = border
    interval = width/shrinkfactor//6
    
    i = 0
    gridxpixels = []
    while i < border.shape[0]:
        gridxpixels.append(i)
        gridxpixels.append(i+1)
        i += interval
    j = 0
    gridypixels = []
    while j < border.shape[1]:
        gridypixels.append(j)
        gridypixels.append(j+1)
        j += interval
    
    for i in gridxpixels:
        for j in range(border.shape[1]):
            output[i,j] = [128,128,128,255]
    for j in gridypixels:
        for i in range(border.shape[0]):
            output[i,j] = [128,128,128,255]
    
    cv2.imwrite(outputname + ".png", output)

#Code taken from here and altered: https://stackoverflow.com/questions/41508458/python-opencv-overlay-an-image-with-transparency
def mergeimages(face, overlay):
    h, w, depth = overlay.shape
    result = face
    
    for i in range(h):
        for j in range(w):
            color1 = face[i, j]
            color2 = overlay[i, j]
            if color2[0] == 0 and color2[1] == 0 and color2[2] == 0:
                continue
            
            alpha = color2[3] / 255.0
            newalpha = max(color1[3], color2[3])
            new_color = [ (1 - alpha) * color1[0] + alpha * color2[0],
                          (1 - alpha) * color1[1] + alpha * color2[1],
                          (1 - alpha) * color1[2] + alpha * color2[2], newalpha]
            result[i, j] = new_color
    return result