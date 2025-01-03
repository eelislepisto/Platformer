import sys
import math
import random
from PyQt5 import QtGui, QtWidgets, QtCore



class Game:

    def __init__(self,parent=None):
        self.sceneView=SceneAndView()
        self.boundary=[self.sceneView.view.width(),self.sceneView.view.height()]
# adding a sick map
        self.mapitemslist = self.map()
        self.added_items = self.addMapItems()
# adding the goal. When player touches this the game is won.
        self.goal = MapObject(0,self.sceneView.view.height()/2+100,30,100,QtCore.Qt.black)
        self.sceneView.scene.addItem(self.goal)
# player is initialized
        self.player=Player(self.sceneView.view.width(), self.added_items)
        self.player.setRect(0,self.sceneView.view.height()+200,20,40)
# adding enemies
        self.enemieslist = self.enemies()
        self.added_enemies = self.addEnemies()
# adding player to the scene      
        self.sceneView.scene.addItem(self.player)
        self.sceneView.view.ensureVisible(self.player,50,50)
        self.sceneView.view.Apress.connect(self.player.moveLeft)
        self.sceneView.view.Dpress.connect(self.player.moveRight)
        self.sceneView.view.Wpress.connect(self.player.moveUp)
# Timer loop
        self.timer=QtCore.QTimer(self.sceneView.view)
        self.timer.start(15)
        self.timer.timeout.connect(self.gravity)
        self.timer.timeout.connect(self.moveEnemies)
        self.timer.timeout.connect(self.playerHitsEnemies)
        self.timer.timeout.connect(self.playerHitsGoal)
        self.timer.timeout.connect(self.handlePlayerMovement)


    def gravity(self):
        if self.playerHitsMap() == False:
            self.player.moveDown()
        else:
            self.player.on_ground = True


    def playerHitsMap(self):
        for i in self.added_items:
            if self.player.collidesWithItem(i):
                return True
        return False


    def map(self):
        items = []
        item1 = [-10,self.sceneView.view.height()/2+750,1450,50,QtCore.Qt.gray]
        items.append(item1)
        item2 = [700,self.sceneView.view.height()/2+600,200,200,QtCore.Qt.gray]
        items.append(item2)
        item3 = [1100,self.sceneView.view.height()/2+500,400,20,QtCore.Qt.gray]
        items.append(item3)
        item4 = [800,self.sceneView.view.height()/2+300,300,20,QtCore.Qt.gray]
        items.append(item4)
        item5 = [0,self.sceneView.view.height()/2+200,700,20,QtCore.Qt.gray]
        items.append(item5)
        return items


# add mapobjects to scene
    def addMapItems(self):
        added = []
        for i in self.mapitemslist:
            self.itm = MapObject(i[0],i[1],i[2],i[3],i[4])
            self.sceneView.scene.addItem(self.itm)
            added.append(self.itm)
        return added


    def enemies(self):
        items = []
        item1 = [700,500,"stalker"]
        items.append(item1)
        item2 = [400,self.sceneView.view.height()/2+710,"guard"]
        items.append(item2)
        item3 = [1000,self.sceneView.view.height()/2+710,"guard"]
        items.append(item3)
        item4 = [850,self.sceneView.view.height()/2+260,"guard"]
        items.append(item4)
        return items


    def addEnemies(self):
        added = []
        for i in self.enemieslist:
            if i[2] == "stalker":
                self.ene = Stalker(self.player)
                self.ene.setRect(i[0],i[1],20,20)
                self.sceneView.scene.addItem(self.ene)
                added.append(self.ene)
            elif i[2] == "guard":
                self.ene = Guard()
                self.ene.setRect(i[0],i[1],20,40)
                self.sceneView.scene.addItem(self.ene)
                added.append(self.ene)
            else:
                print("Unknown enemy type")
        return added


# for calling the enemies move functions
    def moveEnemies(self):
        for i in self.added_enemies:
            i.move()


    def playerHitsEnemies(self):
        for i in self.added_enemies:
            if self.player.collidesWithItem(i):
                self.restart()

    def handlePlayerMovement(self):
        if self.sceneView.view.keyLeft:
            self.player.moveLeft()
        if self.sceneView.view.keyRight:
            self.player.moveRight()
        if self.sceneView.view.keyUp:
            self.player.moveUp()


    def playerHitsGoal(self):
        if self.player.collidesWithItem(self.goal):
            self.victory()


    def restart(self):
        print("Defeat! Restarting...")
        self.__init__()


    def victory(self):
        print("Victory! Restarting...")
        self.__init__()



class View(QtWidgets.QGraphicsView, QtCore.QObject):
    def __init__(self,parent=None):
        super(View,self).__init__(parent)
# fix the size of display window
        self.setFixedSize(1400,800)
# set the alignment of displaywindow so that (0,0) lies on top left corner
        self.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
#shut down the scroll bar.
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
# setting window title
        self.setWindowTitle('Game')     
        self.setSceneRect(self.x()-2,self.y()+self.height()/2-2,self.width(),self.height())
# status wheter or not player is on the ground.
        self.timer=QtCore.QTimer()
        self.fixertimer=QtCore.QTimer()
        self.cooldown = False
        self.fixertimer.start(7000)
        self.fixertimer.timeout.connect(self.fixCoolDown)
        self.keyLeft = False
        self.keyRight = False
        self.keyUp = False


# defining the signals that will be passed onto the Game class instance
    Apress=QtCore.pyqtSignal()
    Dpress=QtCore.pyqtSignal()
    Wpress=QtCore.pyqtSignal()
    
# defining key press events so that the signals are emitted. These signals are caught by Game class instance.
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_A:
            self.keyLeft = True
        elif event.key() == QtCore.Qt.Key_D:
            self.keyRight = True
        elif event.key() == QtCore.Qt.Key_W:
            self.keyUp = True
            self.timer.singleShot(100000, self.jump)


    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_A:
            self.keyLeft = False
        elif event.key() == QtCore.Qt.Key_D:
            self.keyRight = False
        elif event.key() == QtCore.Qt.Key_W:
            self.keyUp = False


    def jump(self):
        if self.cooldown == False:
            self.Wpress.emit()
            self.timer.singleShot(3000, self.jumpCoolDown)


    def jumpCoolDown(self):
        self.cooldown = not self.cooldown


    def fixCoolDown(self):
        self.cooldown = False



class SceneAndView:

    def __init__(self):
# instantizing QGraphicsScene class
        self.scene=QtWidgets.QGraphicsScene()
# instantizing the View class
        self.view=View()
# setting the scene for view
        self.view.setScene(self.scene)



class Player(QtWidgets.QGraphicsRectItem):

    def __init__(self,maxWidth,mapitemslist,parent=None):
        super(Player,self).__init__(parent)
        self.maxWidth=maxWidth-20
        self.setBrush(QtGui.QBrush(QtCore.Qt.blue))
        self.speed = 10
        self.direction = None
        self.mapitemslist = mapitemslist
        self.on_ground = False

# Timer for jump duration
        self.jump_timer = QtCore.QTimer()
# Interval for smooth upward motion
        self.jump_timer.setInterval(30)
        self.jump_timer.timeout.connect(self.continueJump)
# Duration of jump in milliseconds
        self.jump_duration = 500
        self.jump_elapsed = 0

# for moving the player left
    def moveLeft(self):
        if self.x() > 0:
            if self.check() == True:
                self.direction = "Left"
                self.setX(self.x() - self.speed)
            elif self.direction == "Right":
                self.direction = "Left"
                self.setX(self.x() - self.speed)

# for moving the player right
    def moveRight(self):
        if self.x() < self.maxWidth:
            if self.check() == True:
                self.direction = "Right"
                self.setX(self.x() + self.speed)
            elif self.direction == "Left":
                self.direction = "Right"
                self.setX(self.x() + self.speed)

# for moving the player up
    def moveUp(self):
        if self.on_ground:
            if self.y() < self.maxWidth:
                self.on_ground = False
                self.jump_elapsed = 0
                self.jump_timer.start()

    def continueJump(self):
        if self.jump_elapsed < self.jump_duration:
            self.setY(self.y() - 20)  # Adjust this value for jump speed
            self.jump_elapsed += self.jump_timer.interval()
        else:
            self.jump_timer.stop() 

# for moving the player down (gravity)
    def moveDown(self):
        if self.y() < self.maxWidth:
            self.setY(self.y() + 4)


# check if the side of the player is free space
# returns False if occupied, True if free
    def check(self):
        x = 1
        y = 0
        while x < len(self.mapitemslist) - 1:
            if self.collidesWithItem(self.mapitemslist[x]):
                y += 1
            x += 1
        if y == 0:
            return True
        else:
            return False
    
    

class MapObject(QtWidgets.QGraphicsRectItem):

    def __init__(self,pos_x,pos_y,width,height,color,parent=None):
        super(MapObject,self).__init__(parent)
# making the item immovable
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setBrush(QtGui.QBrush(color))
        self.setRect(pos_x,pos_y,width,height)



class Stalker(QtWidgets.QGraphicsEllipseItem):
    def __init__(self,target,parent=None):
        super(Stalker,self).__init__(parent)
        self.setBrush(QtGui.QBrush(QtCore.Qt.red))
        self.enemytype = "stalker"
        self.target = target
        self.speed = 1
        self.random = random.Random(2)
        self.velocities = [5, 0 , -5]

    
    def move(self):
        self.setY(self.y() + self.random.choice(self.velocities))
        self.setX(self.x() + self.random.choice(self.velocities))



class Guard(QtWidgets.QGraphicsRectItem):
    def __init__(self,parent=None):
        super(Guard,self).__init__(parent)
        self.setBrush(QtGui.QBrush(QtCore.Qt.red))
        self.enemytype = "guard"
        self.speed = 1
        self.patrolDistance = 100
        self.direction = False
        self.checkSpeedAndDistance()

    
    def move(self):
        if self.direction == False:
            if self.x() > self.patrolDistance:
                self.changeDirection()
            self.setX(self.x() + self.speed)
        else:
            if self.x() == 0:
                self.changeDirection()
            self.setX(self.x() - self.speed)


    def checkSpeedAndDistance(self):
        if self.patrolDistance % self.speed != 0:
            print("Guard cant patrol!")

        
    def changeDirection(self):
        self.direction = not self.direction



if __name__=='__main__':
    app=QtWidgets.QApplication(sys.argv)
    w=Game()
    w.sceneView.view.show()
    sys.exit(app.exec_())