import random
import cv2 as cv
import mediapipe as mp
import time

font = cv.FONT_HERSHEY_DUPLEX
#test
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
        self.foodIcon = cv.imread("food_icon.png", cv.IMREAD_UNCHANGED)
        self.foodIcon = cv.cvtColor(self.foodIcon, cv.COLOR_RGBA2RGB)
        self.foodIcon = cv.resize(self.foodIcon, (23, 23))

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils

    def start(self):
        cap = cv.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)

        while True:
            success, img = cap.read()
            img = cv.flip(img, 1)

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

            img = self.displayGUI(img)
            cv.imshow("Image", img)

            key = cv.waitKey(1)
            if key == ord('r'):
                self.resetGame()
                print('reset')
            elif key == 27:
                cv.destroyAllWindows()
                cap.release()
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
        a, _ = self.backSize
        c, _ = self.gameSize
        e = self.margin
        f = c // self.numTile
        x_new = a / 2 - c / 2 + f * (i + 1 / 2) + 1 / 2
        y_new = 2 * e + f * (j + 1 / 2) + 1 / 2
        return int(x_new), int(y_new)

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

        x_food, y_food = self.indexToPixel(self.foodPoint)
        # تنظیم مختصات مستطیل غذا
        x_food_rect = x_food - self.foodIcon.shape[1] // 2
        y_food_rect = y_food - self.foodIcon.shape[0] // 2
        x_food_rect_end = x_food_rect + self.foodIcon.shape[1]
        y_food_rect_end = y_food_rect + self.foodIcon.shape[0]

        # قسمت مربوط به نمایش غذا را به تصویر اصلی اضافه می‌کنیم
        imgMain[y_food_rect:y_food_rect_end, x_food_rect:x_food_rect_end] = self.foodIcon
        if self.gameOver:

            cv.putText(imgMain, "You Lose Press R for Restart", (400, 200), cv.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

            cv.putText(imgMain, "Best Score : " + str(self.high_score), (520, 280), cv.FONT_HERSHEY_DUPLEX, 1, (200, 0, 0), 2, cv.LINE_AA)



        for i, point in enumerate(self.points):

            color = snakeColor if i != len(self.points) - 1 else headColor

            imgMain = self.drawSquare(imgMain, point, color)



        return imgMain

    def drawSquare(self, imgMain, position, color, fill=False):
        if fill == True:
            thickness = 2
        else:
            thickness = -2
        if (self.high_score <= self.score):
            self.high_score = self.score
        i, j = position
        n = self.gameSize[0] // self.numTile
        cv.putText(imgMain, str("Score : " + str(self.score)), (560, 580), font, 1, (0, 255, 0), 2, cv.LINE_AA)
        imgMain = cv.rectangle(imgMain, (self.backSize[0] // 2 - self.gameSize[0] // 2 + n * i + 1,
                                         2 * self.margin + n * j + 1),
                               (self.backSize[0] // 2 - self.gameSize[0] // 2 + n * (i + 1),
                                2 * self.margin + n * (j + 1)),
                               color, thickness)
        return imgMain


game = SnakeGameClass()
game.start()
