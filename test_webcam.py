#!/usr/bin/env python3
##
## EPITECH PROJECT, 2026
## LockSense
## File description:
## test_webcam
##

import cv2

def test_webcam():
    print("--- LockSense: OpenCV Diagnostic ---")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    print(f"webcam detected: {int(width)}x{int(height)} resolution.")

    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to receive frame.")
            break
        
        cv2.imshow('LockSense - OpenCV Camera Feed', frame)
        
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            print("OpenCV test closed correctly")
            break
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_webcam()
