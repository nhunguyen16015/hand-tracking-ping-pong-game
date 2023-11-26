import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import tkinter as tk
from tkinter import simpledialog

# Function to determine the winner and their score
def get_result(players, scores):
    if scores[0] > scores[1]:
        winner_name = players[0]
        winner_score = scores[0]
    elif scores[0] < scores[1]:
        winner_name = players[1]
        winner_score = scores[1]
    else:
        winner_name = "Tie!"
        winner_score = scores[1]
    return winner_name, winner_score

# Function to initialize game variables
def initialize_game_values():
    ballPos = [100, 100]
    speedX = 15
    speedY = 15
    gameOver = False
    scores = [0, 0]
    return ballPos, speedX, speedY, gameOver, scores

# Function to initialize game resources and parameters
def initialize_resources():
    # Initialize the camera capture
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    # Load game images
    imgBackground = cv2.imread("Resources/Background.png")
    imgGameOver = cv2.imread("Resources/gameOver.png")
    imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
    imgBat1 = cv2.imread("Resources/bat1.png", cv2.IMREAD_UNCHANGED)
    imgBat2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)

    # Create a hand detector object
    detector = HandDetector(detectionCon=0.8, maxHands=2)

    return cap, imgBackground, imgGameOver, imgBall, imgBat1, imgBat2, detector

# Function to get player names using a Tkinter dialog
def get_player_names():
    # Create a tkinter window for player names input
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    players =["", ""]
    players[0] = simpledialog.askstring("Player 1", "Enter Player 1's Name:")
    players[1] = simpledialog.askstring("Player 2", "Enter Player 2's Name:")

    return players

# Main game loop
def main_game_loop():
    # Initialize game resources and parameters
    cap, imgBackground, imgGameOver, imgBall, imgBat1, imgBat2, detector = initialize_resources()
    ballPos, speedX, speedY, gameOver, scores = initialize_game_values()

    # Get player names
    players = get_player_names()

    while True:
        _, img = cap.read()
        img = cv2.flip(img, 1)
        imgRaw = img.copy()

        # Detect hands using the HandDetector
        hands, img = detector.findHands(img, flipType=False)

        # Overlay background image on the frame
        img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

        if hands:
            for hand in hands:
                x, y, w, h = hand['bbox']
                h1, w1, _ = imgBat1.shape
                y1 = y - h1 // 2
                y1 = np.clip(y1, 20, 415)

                if hand['type'] == "Left":
                    img = cvzone.overlayPNG(img, imgBat1, (59, y1))
                    if 59 < ballPos[0] < 59 + w1 and y1 < ballPos[1] < y1 + h1:
                        speedX = -speedX
                        ballPos[0] += 30
                        scores[0] += 1

                if hand['type'] == "Right":
                    img = cvzone.overlayPNG(img, imgBat2, (1195, y1))
                    if 1195 - 50 < ballPos[0] < 1195 and y1 < ballPos[1] < y1 + h1:
                        speedX = -speedX
                        ballPos[0] -= 30
                        scores[1] += 1

        if ballPos[0] < 40 or ballPos[0] > 1200:
            gameOver = True

        if gameOver:
            img = imgGameOver
            # Display winner name and score
            winner_name, winner_score = get_result(players, scores)
            
            if scores[0] == scores[1]:
                result_str = "Tie!"
            else:
                result_str = f"{winner_name} won"
            
            print(result_str)
            # Display winner's name and score on the screen
            cv2.putText(img, result_str.zfill(2), (550, 265), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 5)
            cv2.putText(img, str(winner_score).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX, 2.5, (200, 0, 200), 5)
        else:
            if ballPos[1] >= 500 or ballPos[1] <= 10:
                speedY = -speedY

            ballPos[0] += speedX
            ballPos[1] += speedY

            # Overlay ball image on the frame
            img = cvzone.overlayPNG(img, imgBall, ballPos)
            cv2.putText(img, str(scores[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
            cv2.putText(img, str(scores[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

        # Display the player's camera feed
        img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

        # Display the game frame
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('r'):
            # Reset game values
            ballPos, speedX, speedY, gameOver, scores = initialize_game_values()
            players = get_player_names()
            # cv2.putText(img, "", (550, 265), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 5)
            # cv2.putText(img, "", (585, 360), cv2.FONT_HERSHEY_COMPLEX, 2.5, (200, 0, 200), 5)

if __name__ == "__main__":
    main_game_loop()