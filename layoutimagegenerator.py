import sys

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
    imagefiles = ["./Icons/" + item + ".png" for item in itemlist]
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
    imagefiles2 = ["./Icons/" + item + ".png" for item in itemstatelist]
    images2 = [cv2.imread(img, -1) for img in imagefiles2]
    
    #Create an empty image
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
    
    output = cv2.resize(output, (width/4, height/4), interpolation = cv2.INTER_AREA)
    overlay = cv2.resize(overlay, (width/4, height/4), interpolation = cv2.INTER_AREA)
    output = mergeimages(output, overlay)
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