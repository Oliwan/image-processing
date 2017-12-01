import numpy as np
import cv2
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from PIL import Image

def cv2PIL(cv2_im):
    """
    Conversion from cv2 image to PIL image.
    """
    if(len(cv2_im.shape)==3):
        cv2_im = cv2.cvtColor(cv2_im,cv2.COLOR_BGR2RGB)        
    pil_im = Image.fromarray(cv2_im)
    return pil_im

def countColors(img):
    """
    Counts number of different colours in a PIL image.
    """
    from collections import defaultdict
    by_color = defaultdict(int)
    
    try:
        img.getdata()
    except:
        img = cv2PIL(img)
        
    for pixel in img.getdata():
        by_color[pixel] += 1
    return len(by_color)

def drawMatches(img1, kp1, img2, kp2, matches):
    """
    This function takes in two images with their associated 
    keypoints, as well as a list of DMatch data structure (matches) 
    that contains which keypoints matched in which images.

    An image will be produced where a montage is shown with
    the first image followed by the second image beside it.

    Keypoints are delineated with circles, while lines are connected
    between matching keypoints.

    img1,img2 - Grayscale images
    kp1,kp2 - Detected list of keypoints through any of the OpenCV keypoint 
              detection algorithms
    matches - A list of matches of corresponding keypoints through any
              OpenCV keypoint matching algorithm
    """

    # Create a new output image that concatenates the two images together
    # (a.k.a) a montage
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')

    # Place the first image to the left
    out[:rows1,:cols1,:] = np.dstack([img1, img1, img1])

    # Place the next image to the right of it
    out[:rows2,cols1:cols1+cols2,:] = np.dstack([img2, img2, img2])

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    for mat in matches:
        mat = mat[0]
        # Get the matching keypoints for each of the images
        img1_idx = mat.queryIdx
        img2_idx = mat.trainIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0), 1)   
        cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0), 1)

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0), 1)

    return out

def imshow(img):
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()

from PIL import Image
from netpbmfile import *

def pgm2pil(fname):
    #
    # This method returns a PIL.Image.  
    #
    pam = NetpbmFile(fname)
    a = pam.asarray(copy=False)

    return Image.fromarray(a)

def wrapper_open_ppm(fname):
    pgm = pgm2pil(fname)

    if pgm is not None:
        return pgm
    return Image.open(fname)

