import random
import numpy as np
import cv2 as cv
import mediapipe as mp
import time

font = cv.FONT_HERSHEY_DUPLEX

class SnakeGameClass:
    def __init__(self):
        self.backSize = (1280, 1280)
        self.gameSize = (500, 500)
        self.numTile = 25
        self.margin = 5
        self.high_score = 0
        self.lastFinger = [None, None]
        self.points = [(self.numTile // 2, self.numTile // 2)]
        self.length = 1
        self.foodPoint = self.randomFood()
        self.score = 0
        self.gameOver = False
        self.gameStart = False
        self.direction = ''
        self.previousTime = time.time()
        self.currentTime = time.time()
        self.snakeSpeed = 0.20
        self.zigzag_path = self.generate_zigzag_path(self.numTile)

        # خواندن تصویر با کانال آلفا (ترنسپرنت)
        self.foodIcon = cv.imread("food_icon.png", cv.IMREAD_UNCHANGED)
        self.foodIcon = cv.resize(self.foodIcon, (20, 20))  # تغییر اندازه تصویر به اندازه مورد نظر
        self.foodMask = self.foodIcon[:, :, 3]  # ماسک کانال آلفا

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        self.cap = cv.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.imgMain = None

    def start(self):
        x, y, w, h = 391, 10, 500, 541
        while True:
            success, img = self.cap.read()
            img = cv.flip(img, 1)
            cropped_img = img[y:y+h, x:x+w]

            imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            if results.multi_hand_landmarks:
                for handLMs in results.multi_hand_landmarks:
                    x_finger = int(handLMs.landmark[8].x * img.shape[1])
                    y_finger = int(handLMs.landmark[8].y * img.shape[0])

                    self.lastFinger = [x_finger, y_finger]
                    self.updateDirection()
                    self.gameStart = True

            if self.isTimeToMoveSnake():
                self.update()

            self.imgMain = self.displayGUI(img)
            cv.imshow("Snake Game", cropped_img)

            key = cv.waitKey(1)
            if key == ord('r'):
                self.resetGame()
                print('reset')
            elif key == 27:
                cv.destroyAllWindows()
                self.cap.release()
                print('break')
                break

    def update(self):
        if (self.gameOver == True) or (self.gameStart == False):
            return 0

        hx, hy = self.points[-1]
        if self.direction == 'l':
            if hx - 1 < 0:
                self.gameOver = True
                return 0
            elif (hx - 1, hy) in self.points:
                self.gameOver = True
                return 0
            elif (hx - 1, hy) == self.foodPoint:
                self.whenAteFood()
                return 0
            else:
                self.points.append((hx - 1, hy))
                del self.points[0]

        elif self.direction == 'r':
            if hx + 1 >= self.numTile:
                self.gameOver = True
                return 0
            elif (hx + 1, hy) in self.points:
                self.gameOver = True
                return 0
            elif (hx + 1, hy) == self.foodPoint:
                self.whenAteFood()
                return 0
            else:
                self.points.append((hx + 1, hy))
                del self.points[0]

        elif self.direction == 'u':
            if hy - 1 < 0:
                self.gameOver = True
                return 0
            elif (hx, hy - 1) in self.points:
                self.gameOver = True
                return 0
            elif (hx, hy - 1) == self.foodPoint:
                self.whenAteFood()
                return 0
            else:
                self.points.append((hx, hy - 1))
                del self.points[0]

        else:
            if hy + 1 >= self.numTile:
                self.gameOver = True
                return 0
            elif (hx, hy + 1) in self.points:
                self.gameOver = True
                return 0
            elif (hx, hy + 1) == self.foodPoint:
                self.whenAteFood()
                return 0
            else:
                self.points.append((hx, hy + 1))
                del self.points[0]

        return 0

    def whenAteFood(self):
        self.points.append(self.foodPoint)
        self.length += 1
        self.foodPoint = self.randomFood()
        self.score += 1
        return 0

    def randomFood(self):
        foodSpace = []
        for i in range(self.numTile):
            for j in range(self.numTile):
                foodSpace.append((i, j))

        for item in self.points:
            foodSpace.remove(item)

        index = random.randrange(len(foodSpace))
        return foodSpace[index]

    def updateDirection(self):
        x_finger, y_finger = self.lastFinger
        x_head, y_head = self.indexToPixel(self.points[-1])

        dx = x_finger - x_head
        dy = y_finger - y_head

        if abs(dx) >= abs(dy):
            if dx >= 0:
                self.direction = 'r'
            else:
                self.direction = 'l'
        else:
            if dy >= 0:
                self.direction = 'd'
            else:
                self.direction = 'u'
        return 0

    def indexToPixel(self, index):

        i, j = index

        n = self.gameSize[0] // self.numTile

        x_new = 390 + n * i + 1

        y_new = 5 + n * j + 1

        return x_new, y_new

    def isTimeToMoveSnake(self):
        self.currentTime = time.time()
        if self.currentTime > self.previousTime + self.snakeSpeed:
            self.previousTime += self.snakeSpeed
            return True
        return False

    def resetGame(self):
        self.lastFinger = [None, None]
        self.points = [(self.numTile // 2, self.numTile // 2)]
        self.length = 1
        self.foodPoint = self.randomFood()
        self.score = 0
        self.gameOver = False
        self.gameStart = False
        return 0

    def displayGUI(self, imgMain):
        if self.gameOver:
            cv.putText(imgMain, "You Lose Press R for Restart", (400, 200), cv.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
            cv.putText(imgMain, "Best Score : " + str(self.high_score), (520, 280), cv.FONT_HERSHEY_DUPLEX, 1, (200, 0, 0), 2, cv.LINE_AA)
        else:
            x_food, y_food = self.indexToPixel(self.foodPoint)
            n = self.gameSize[0] // self.numTile
            imgMain[y_food:y_food + 20, x_food:x_food + 20] = self.foodIcon[:, :, :3] * (self.foodMask[:, :, None] / 255.0) + imgMain[y_food:y_food + 20, x_food:x_food + 20] * (1.0 - self.foodMask[:, :, None] / 255.0)


            imgMain = self.drawSnake(imgMain, self.points, (0, 255, 0))

        cv.putText(imgMain, str("Score : " + str(self.score)), (560, 540), font, 1, (0, 255, 0), 2, cv.LINE_AA)
        imgMain = cv.rectangle(imgMain,
                                (self.backSize[0] // 2 - self.gameSize[0] // 2, 2 * self.margin),
                                (self.backSize[0] // 2 + self.gameSize[0] // 2, 2 * self.margin + self.gameSize[1]),
                                (0, 255, 0), 2)
        return imgMain

    def drawSnake(self, imgMain, points, color):
        n = self.gameSize[0] // self.numTile
        thickness = n // 2  # تغییر اندازه مار
        
        # رسم سر مار به صورت دایره‌ای
        head_pt = (int(390 + n * (points[-1][0] + 0.5)), int(2 + n * (points[-1][1] + 0.5)))
        cv.circle(imgMain, head_pt, thickness, color, thickness=-1)
        
        # رسم چشم‌ها
        eye_radius = thickness // 4
        eye1_center = (head_pt[0] - n // 4, head_pt[1] - n // 4)
        eye2_center = (head_pt[0] + n // 4, head_pt[1] - n // 4)
        cv.circle(imgMain, eye1_center, eye_radius, (0, 0, 0), thickness=-1)
        cv.circle(imgMain, eye2_center, eye_radius, (0, 0, 0), thickness=-1)
        
        # رسم خنده
        smile_center = (head_pt[0], head_pt[1] + n // 4)
        cv.ellipse(imgMain, smile_center, (n // 4, n // 6), 0, 0, 180, (0, 0, 0), thickness=n // 8)

        # رسم بدن مار بدون فضای خالی
        for i in range(len(points) - 1):
            pt1 = (int(390 + n * (points[i][0] + 0.5)), int(5 + n * (points[i][1] + 0.5)))
            pt2 = (int(390 + n * (points[i + 1][0] + 0.5)), int(5 + n * (points[i + 1][1] + 0.5)))
            cv.line(imgMain, pt1, pt2, color, thickness=thickness)
        
        return imgMain
    
    def generate_zigzag_path(self, num_tiles):
        path = []
        for i in range(num_tiles):
            if i % 2 == 0:
                for j in range(num_tiles):
                    path.append((i, j))
            else:
                for j in range(num_tiles-1, -1, -1):
                    path.append((i, j))
        return path

game = SnakeGameClass()
game.start()

