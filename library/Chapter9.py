import cv2
import numpy as np

L = 256

def Erosion(imgin):
    w = cv2.getStructuringElement(cv2.MORPH_RECT,(45,45))
    erosion = cv2.erode(imgin,w,iterations = 1)
    return erosion

def Dilation(imgin):
    w = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    erosion = cv2.dilate(imgin,w,iterations = 1)
    return erosion

def Boundary(imgin):
    w = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    erosion = cv2.erode(imgin,w,iterations = 1)
    imgout = imgin - erosion
    return imgout

def Contour(imgin):
    #Ảnh màu của opencv là BGR
    #Ảnh màu của pillow là RGB
    imgout = cv2.cvtColor(imgin,cv2.COLOR_GRAY2BGR)
    contours, _= cv2.findContours(imgin,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contour = contours[0]
    n = len(contour)
    for i in range(0,n-1):
        x1 = contour[i,0,0]
        y1 = contour[i,0,1]
        x2 = contour[i+1,0,0]
        y2 = contour[i+1,0,1]
        cv2.line(imgout, (x1,y1),(x2,y2),(0,0,255),2)
    x1 = contour[n-1,0,0]
    y1 = contour[n-1,0,1]
    x2 = contour[0,0,0]
    y2 = contour[0,0,1]
    cv2.line(imgout, (x1,y1),(x2,y2),(0,0,255),2)
    return imgout

def ConvexHull(imgin):
    imgout = cv2.cvtColor(imgin,cv2.COLOR_GRAY2BGR)
    contours, _= cv2.findContours(imgin,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contour = contours[0]
    
    p = cv2.convexHull(contour,returnPoints=False)

    n = len(p)
    for i in range(0,n-1):
        vi_tri_1 = p[i,0]
        vi_tri_2 = p[i+1,0]
        x1 = contour[vi_tri_1,0,0]
        y1 = contour[vi_tri_1,0,1]
        x2 = contour[vi_tri_2,0,0]
        y2 = contour[vi_tri_2,0,1]
        cv2.line(imgout, (x1,y1),(x2,y2),(0,0,255),2)
    vi_tri_1 = p[n-1,0]
    vi_tri_2 = p[0,0]
    x1 = contour[vi_tri_1,0,0]
    y1 = contour[vi_tri_1,0,1]
    x2 = contour[vi_tri_2,0,0]
    y2 = contour[vi_tri_2,0,1]
    cv2.line(imgout, (x1,y1),(x2,y2),(0,0,255),2)
    return imgout

def DefectDetect(imgin):
    imgout = cv2.cvtColor(imgin,cv2.COLOR_GRAY2BGR)
    contours, _= cv2.findContours(imgin,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contour = contours[0]
    p = cv2.convexHull(contour,returnPoints=False)

    n = len(p)
    for i in range(0,n-1):
        vi_tri_1 = p[i,0]
        vi_tri_2 = p[i+1,0]
        x1 = contour[vi_tri_1,0,0]
        y1 = contour[vi_tri_1,0,1]
        x2 = contour[vi_tri_2,0,0]
        y2 = contour[vi_tri_2,0,1]
        cv2.line(imgout, (x1,y1),(x2,y2),(0,0,255),2)
    vi_tri_1 = p[n-1,0]
    vi_tri_2 = p[0,0]
    x1 = contour[vi_tri_1,0,0]
    y1 = contour[vi_tri_1,0,1]
    x2 = contour[vi_tri_2,0,0]
    y2 = contour[vi_tri_2,0,1]
    cv2.line(imgout, (x1,y1),(x2,y2),(0,0,255),2)

    data = cv2.convexityDefects(contour,p)
    n = len(data)
    for i in range(0,n):
        if(data[i,0,3] >5000):
            vi_tri = data[i,0,2]
            x = contour[vi_tri,0,0]
            y = contour[vi_tri,0,1]
            cv2.circle(imgout,(x,y),5,(0,255,0),-1)
    return imgout