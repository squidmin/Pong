""" Classic Pong (for now) """

from tkinter import *
import random

APP_TITLE = "Pong"
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 440
PLAYFIELD_TOP_BORDER_Y_COOR = 27

class MainApplication(Frame):
    def __init__(self, parent):
        """ MainApplication constructor """
        
        Frame.__init__(self, parent)
        self.__parent = parent

        self.__game_is_paused = False

        self.__p1_score = 0
        self.__p2_score = 0

        # This dict keeps track of keys that have been pressed but not released
        self.pressed = { }

        self._create_ui()

    def _start(self):
        """ MainApplication.start() """

        self._animate()

    def _create_ui(self):
        """ MainApplication._create_ui() """
        
        self.__parent.title(APP_TITLE)
        self.pack(fill = BOTH, expand = 1)
        
        # Create menu bar
        self.__menubar = Menu(self.__parent)
        self.__parent.config(menu = self.__menubar, bg = "#c2a893")
        self.__options_menu = Menu(self.__menubar, tearoff = 0, bg = "#6c9bb2")
        self.__menubar.add_cascade(label = "Options", menu = self.__options_menu)
        self.__options_menu.add_command(label = "View Controls", command = self._display_controls)
        self.__options_menu.add_command(label = "Quit Pong", command = self.__parent.quit)
        
        # Create canvas
        self.canvas = Canvas(width = CANVAS_WIDTH, height = CANVAS_HEIGHT)
        self.canvas.config(background = "#a72f2f", borderwidth = 2, relief = SUNKEN, scrollregion = (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT))
        self.canvas.pack(side = "top", fill = "both", expand = "true")
        
        # "Scoreboard" area to hold P1 and P2 scores
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, 27, fill = "#357ac0")
        # Display the strings "P1: " and "P2: " in appropriate locations on canvas
        self.canvas.create_text(40, 15, text = "P1: ", font = ("Courier", "20", "bold"))
        self.canvas.create_text(CANVAS_WIDTH - 50, 15, text = "P2: ", font = ("Courier", "20", "bold"))
        # The player's integer score is displayed on the canvas to the right of the latter string
        self.__p1_score_text = self.canvas.create_text(70, 15, text = str(self.__p1_score), 
                                                       font = ("Courier", "20", "bold"), anchor = CENTER)
        self.__p2_score_text = self.canvas.create_text(CANVAS_WIDTH - 20, 15, text = str(self.__p2_score), 
                                                       font = ("Courier", "20", "bold"), anchor = CENTER)
        
        # Thicken the line separating scoreboard from playfield
        self.canvas.create_line(0, PLAYFIELD_TOP_BORDER_Y_COOR, CANVAS_WIDTH, PLAYFIELD_TOP_BORDER_Y_COOR, width = 2, fill = "#000")

        self.__p1 = Paddle(self.canvas, self.__p1_score_text, tag = "p1", color = "#cFc68c",
                           x = 20, y = CANVAS_HEIGHT / 2)
        self.__p2 = Paddle(self.canvas, self.__p2_score_text, tag = "p2", color = "#73a8de", 
                           x = CANVAS_WIDTH - 20, y = CANVAS_HEIGHT / 2)
        
        self.__ball = Ball(self.__p1, self.__p2, self.canvas, tag = "ball", color = "#000", 
                           x = CANVAS_WIDTH * 0.5, y = CANVAS_HEIGHT * 0.3)
        
        self._set_bindings()

        self._centerWindow()

        self._start()

    def _animate(self):
        """ MainApplication._animate() """

        if (not self.__game_is_paused):
            if (self.pressed["w"]): self.__p1.move_up()
            if (self.pressed["s"]): self.__p1.move_down()
            if (self.pressed["o"]): self.__p2.move_up()
            if (self.pressed["l"]): self.__p2.move_down()

        self.__p1.redraw()
        self.__p2.redraw()
        self.__ball.redraw()
        self.__parent.after(10, self._animate)

    def _set_bindings(self):
        """ MainApplication._set_bindings() """

        for char in ["w","s","o", "l"]:
            self.__parent.bind("<KeyPress-%s>" % char, self._pressed)
            self.__parent.bind("<KeyRelease-%s>" % char, self._released)
            self.pressed[char] = False

        self.__parent.bind("p", self._toggle_game_pause)

    def _pressed(self, event):
        """ MainApplication._pressed() """

        self.pressed[event.char] = True

    def _released(self, event):
        """ MainApplication._released() """

        self.pressed[event.char] = False

    def _toggle_game_pause(self, event):
        """ MainApplication._toggle_game_pause() """

        if (not self.__game_is_paused):   
            self.canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, text = "PAUSE", 
                                    font = ("Courier", "27", "bold"), fill = "#ced5da", 
                                    anchor = CENTER, tags = "pause") 
            self.__game_is_paused = True
            self.__ball_pause_dx = self.__ball.get_dx()
            self.__ball_pause_dy = self.__ball.get_dy()
            self.__ball.set_dx(0)
            self.__ball.set_dy(0)
        else:
            self.canvas.delete("pause")
            self.__game_is_paused = False
            self.__ball.set_dx(self.__ball_pause_dx)
            self.__ball.set_dy(self.__ball_pause_dy)

    def _display_controls(self):
        return

    def _centerWindow(self):
        w = CANVAS_WIDTH
        h = CANVAS_HEIGHT
        sw = self.__parent.winfo_screenwidth()
        sh = self.__parent.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.__parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

class Paddle:
    def __init__(self, canvas, player_score_text, tag, color = "red", x = 0, y = 0):
        """ Paddle constructor """
        
        self.__canvas = canvas
        self.__player_score_text = player_score_text
        self.__tag = tag
        
        # Note: These coordinates specify the center of the paddle
        self.__x = x
        self.__y = y

        # The coordinates needed by Canvas.create_rectangle(x0, y0, ...) are calculated relative to
        #   the center of the paddle.
        self.__x0 = self.__x - 10
        self.__x1 = self.__x + 10
        self.__y0 = self.__y - 20
        self.__y1 = self.__y + 20
        self.__color = color
        self.__score = 0
        self.redraw()

    # Standard setters and getters for Paddle coordinates x, y, x0, ...
    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_x0(self):
        return self.__x0

    def get_x1(self):
        return self.__x1

    def get_y0(self):
        return self.__y0

    def get_y1(self):
        return self.__y1

    def move_up(self):
        """ Paddle.move_up()
            Public because it's called by MainApplication._animate() """
        
        self.__y = max(self.__y - 2, PLAYFIELD_TOP_BORDER_Y_COOR + 22)

    def move_down(self):
        """ Paddle.move_down()
            Public because it's called by MainApplication._animate() """
        self.__y = min(self.__y + 2, 414)

    def increment_score(self):
        self.__score += 1
        self.__canvas.itemconfigure(self.__player_score_text, text = str(self.__score))

    def redraw(self):
        """ Paddle.redraw()
            Public because it's called by MainApplication._animate()  """
        
        self.__x0 = self.__x - 10
        self.__x1 = self.__x + 10
        self.__y0 = self.__y - 20
        self.__y1 = self.__y + 20
        self.__canvas.delete(self.__tag)
        self.__canvas.create_rectangle(self.__x0, self.__y0, self.__x1, self.__y1, tags = self.__tag, fill = self.__color)

class Ball:
    def __init__(self, p1, p2, canvas, tag, color = "#000", x = 0, y = 0):
        """ Ball constructor """
        
        self.__canvas = canvas
        self.__p1 = p1  # Player (or Paddle) 1
        self.__p2 = p2  # Player (or Paddle) 2
        self.__tag = tag
        self.__x = x
        self.__y = y
        self.__color = color
        self.__radius = 5
        self.__dx = -0.6
        self.__dy = 0.4
        self.__accel = 1.2
        self.redraw()

    def get_dx(self):
        return self.__dx

    def get_dy(self):
        return self.__dy

    def set_dx(self, dx):
        self.__dx = dx

    def set_dy(self, dy):
        self.__dy = dy

    def _ball_init(self, right):
        """ Ball._ball_init() 
            Spawns a ball. If right is true, then spawn to the left. Otherwise spawn to the right. """

        self.__x = CANVAS_WIDTH / 2
        self.__y = CANVAS_HEIGHT / 2

        if (right):
            self.__dx = 0.6
            self.__dy = 0.4
        else:
            self.__dx = -1.0 * 0.6
            self.__dy = 0.4
    
    def redraw(self):
        """ Ball.redraw()
            Public because it's called by Playfield._animate()  """
        
        # Keep ball on canvas.
        if ( (self.__y - self.__radius < PLAYFIELD_TOP_BORDER_Y_COOR) or (self.__y + self.__radius > CANVAS_HEIGHT - 5) ):
            self.__dy *= -1

        # If ball hits the left gutter...
        if (self.__x - self.__radius <= 30):
            # ... and if vertical position of ball is outside of vertical range of left paddle...
            if (self.__y < self.__p1.get_y0() or self.__y > self.__p1.get_y1()):
                # Play a sound for left gutter hit, preferably.
                self._ball_init(True)
                self.__p2.increment_score()
            # ... else (if vertical position of ball is within vertical range of left paddle),
            #     invert velocity and accelerate.
            elif (self.__y >= self.__p1.get_y0() and self.__y <= self.__p1.get_y1()):
                # Play left paddle sound, preferably.
                self.__dx *= -1.15
            
        # If ball hits the right gutter...
        if (self.__x + self.__radius >= CANVAS_WIDTH - 30):
            # ... and if vertical position of ball is outside of vertical range of right paddle...
            if (self.__y < self.__p2.get_y0() or self.__y > self.__p2.get_y1()):
                # Play a sound for right gutter hit, preferably.
                self._ball_init(False)
                self.__p1.increment_score()
            # ... else (if vertical position of ball is within vertical range of right paddle),
            #     invert velocity and accelerate.
            elif (self.__y >= self.__p2.get_y0() and self.__y <= self.__p2.get_y1()):
                # Play right paddle sound, preferably.
                self.__dx *= -1.15

        self.__y += self.__dy
        self.__x += self.__dx
        x0 = self.__x - self.__radius
        x1 = self.__x + self.__radius
        y0 = self.__y - self.__radius
        y1 = self.__y + self.__radius
        self.__canvas.delete(self.__tag)
        self.__canvas.create_oval(x0, y0, x1, y1, tags = self.__tag, fill = self.__color)

""" main """
if (__name__ == "__main__"):
    root = Tk()
    MainApplication(root).pack(side = "top", fill = "both", expand = True)
    root.mainloop()
