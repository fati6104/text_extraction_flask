# import the necessary packages
from imutils.object_detection import non_max_suppression
from PIL import Image
import numpy as np
import argparse
import time
import cv2
import pytesseract
import glob
import uuid
import os

UPLOAD_FOLDER = 'static/uploads'

fll = str(uuid.uuid4())

def image_scene(p,filename):
    # load the input image and grab the image dimensions
    image = Image.open(p)
    image = np.array(image)
    image = cv2.resize(image,(224,224))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    orig = image.copy()
    (origH, origW) = image.shape[:2]
    #(H, W) = image.shape[:2]
    # set the new width and height and then determine the ratio in change
    # for both the width and height
    (newW, newH) = (320, 320)
    rW = origW  / float(newW)
    rH = origH  / float(newH)
    # resize the image and grab the new image dimensions
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    # define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layerNames = ["feature_fusion/Conv_7/Sigmoid","feature_fusion/concat_3"]

    # load the pre-trained EAST text detector
    print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet("frozen_east_text_detection.pb")
    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
                             (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    end = time.time()

    # show timing information on text prediction
    print("[INFO] text detection took {:.6f} seconds".format(end - start))

    # grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over the number of columns
        for x in range(0, numCols):
            if scoresData[x] < 0.5:
                continue

            # compute the offset factor as our resulting feature maps will
            # be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and then
            # compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height of
            # the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates for
            # the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # add the bounding box coordinates and probability score to
            # our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # apply non-maxima suppression to suppress weak, overlapping bounding boxes
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    results = []

    # loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        dX = int((endX - startX) * 0.0)
        dY = int((endY - startY) * 0.0)
        startX = max(0, startX - dX)
        startY = max(0, startY - dY)
        endX = min(origW, endX + (dX * 2))
        endY = min(origH, endY + (dY * 2))
        roi = orig[startY:endY, startX:endX]
        config = ("-l eng --oem 1 --psm 7")
        text = pytesseract.image_to_string(roi, config=config)
        #save in txt file
        f = open(os.path.join(UPLOAD_FOLDER, filename)+'.txt','a')
        f.write(text)
        f.write(" ")
        f.close()
        results.append(((startX, startY, endX, endY), text))
    results = sorted(results, key=lambda r:r[0][1])
    s =0
    for ((startX, startY, endX, endY), text) in results:
        s=s+1
        #show in console
        print("{}".format(text))
        text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
        
        #show roi in image
        output = orig.copy()
        cv2.rectangle(output, (startX, startY), (endX, endY),(0, 0, 255), 2)
        cv2.putText(output, text, (startX, startY - 20),cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        roi = output[startY: endY   , startX: endX]
        cv2.imwrite(UPLOAD_FOLDER+filename+'.jpg',roi)
    print("-----------------------------------------------------------")
    print("Done")



#image_scene("../samples/lol.jpg")
