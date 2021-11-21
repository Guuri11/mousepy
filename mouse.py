import cv2
import numpy as np
import HandTrackingModule as htm
import pyautogui
from pynput.mouse import Button, Controller

mouse = Controller()
capture = cv2.VideoCapture(0)

camWidth, camHeight = 640, 480
screenWidth, screenHeight = pyautogui.size()
previousTime = 0
previousLocationX, currentLocationX = 0, 0
previousLocationY, currentLocationX = 0, 0

# define width
capture.set(3,camWidth)

# define height
capture.set(4,camHeight)
detector = htm.handDetector(maxHands=1)
frameReduction = 50 # Frame Reduction
clicked = False

SMOOTH = 7
MINIMUM_DISTANCE_TO_CLICK = 40
MINIMUM_DISTANCE_TO_DOUBLE_CLICK = 10

while True:

    # 1. Find the hand landmarks
    success, img = capture.read()
    img = detector.findHands(img)
    lmList, box = detector.findPosition(img)

    # 2. Get the tip of the index and middle finger
    if(len(lmList) != 0):
        xIndexFinger, yIndexFinger = lmList[8][1:]
        xMiddleFinger, yMiddleFInger = lmList[12][1:]
        
        # 3. Check finger is up
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameReduction, frameReduction), (camWidth - frameReduction, camHeight - frameReduction), (51, 51, 204), 2)

        # 4. Only Index finger: Moving mode
        if(fingers[1] == 1 and fingers[2] == 0 ):
            # 5. Convert our coords
            x3 = np.interp(xIndexFinger, (frameReduction, camWidth - frameReduction), (0, screenWidth))
            y3 = np.interp(yIndexFinger, (frameReduction, camHeight - frameReduction), (0, screenHeight))

            # 6. Smoothen values
            currentLocationX = previousLocationX + (x3 - previousLocationX) / SMOOTH
            currentLocationY = previousLocationY + (y3 - previousLocationY) / SMOOTH
            
            # 7. Move mouse
            mouse.position = (screenWidth - currentLocationX, currentLocationY)
            cv2.circle(img, (xIndexFinger,yIndexFinger), 15, (51, 51, 204), cv2.FILLED)
            previousLocationX, previousLocationY = currentLocationX, currentLocationY

        # 8. Check if we are in clicking mode
        if(fingers[1] == 1 and fingers[2] == 1 ):
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8,12,img)
            # 10. Click mouse if distance is short
            print(length)
            if(length < MINIMUM_DISTANCE_TO_CLICK and length > MINIMUM_DISTANCE_TO_DOUBLE_CLICK and clicked == False):
                cv2.circle(img, (lineInfo[4],lineInfo[5]), 15, (255, 153, 0), cv2.FILLED)
                mouse.click(Button.left, 1)
                clicked = True
            if(length < MINIMUM_DISTANCE_TO_DOUBLE_CLICK and clicked == False):
                cv2.circle(img, (lineInfo[4],lineInfo[5]), 15, (255, 153, 0), cv2.FILLED)
                mouse.click(Button.left, 2)
                clicked = True

            if(length > MINIMUM_DISTANCE_TO_CLICK):
                clicked = False

    # 11. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)