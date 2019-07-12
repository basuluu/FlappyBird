from tkinter import *
from PIL import Image, ImageTk
from collections import deque
import random
import pickle
import os
import atexit

root = Tk()
root.resizable(width=False, height=False)
root.title("Flappy Bird")


class FlappyBird:

    GRID_SIZE = 16
    SQUARE_SIZE = 20
    width = GRID_SIZE*SQUARE_SIZE*2
    height = GRID_SIZE*SQUARE_SIZE
    bird_width = int(SQUARE_SIZE * 1.5)
    bird_height = int(SQUARE_SIZE * 1.5)

    def __init__(self, root):
        self.root = root

    def load(self):
        if os.path.exists('save'):
            with open('save', 'rb') as f:
                self.record = int(pickle.load(f))
        else:
            self.record = 0

    def save(self):
        with open('save', 'wb') as f:
            pickle.dump(self.record, f)

    def create_canvas(self):
        self.canvas = Canvas(self.root,
                             width=self.width,
                             height=self.height,
                             bg="white")
        self.canvas.pack()

    def set_up_game(self):
        self.load()
        atexit.register(self.save)
        self.set_all_images()
        self.root.bind('<Key>', self.keypress)

    def refresh_game(self):
        self.create_canvas()
        
        self.barrier_top_deque = deque()
        self.barrier_bottom_deque = deque()
        self.barrier_after_bird = deque()
        self.generate_barrier(30, 10, 3)
        self.generate_bird()

        self.barrier_speed = 1
        self.bird_speed = 1.3
        self.points = 0

        self.move_barrier(self.barrier_bottom_deque)
        self.move_barrier(self.barrier_top_deque)
        self.move_barrier(self.barrier_after_bird)
        self.show_points_frame()
        self.check_crash()

    def run(self):
        self.set_up_game()
        self.refresh_game()
        self.fly_down()
        self.root.mainloop()

    def generate_barrier(self, x_start, step, num):
        x = x_start
        while num > 0:
            y1_end = random.randint(1, self.GRID_SIZE - 4)
            y2_start = y1_end + 4

            barrier_top = self.canvas.create_rectangle(
                self.SQUARE_SIZE * x,
                self.SQUARE_SIZE * 0,
                self.SQUARE_SIZE * (x + 1),
                self.SQUARE_SIZE * y1_end,
                fill="#135113"
            )

            barrier_bottom = self.canvas.create_rectangle(
                self.SQUARE_SIZE * x,
                self.SQUARE_SIZE * y2_start,
                self.SQUARE_SIZE * (x + 1),
                self.height,
                fill="#135113"
            )

            self.barrier_top_deque.append(barrier_top)
            self.barrier_bottom_deque.append(barrier_bottom)
            num -= 1
            x += step

    def generate_bird(self):
        self.bird = self.canvas.create_image(self.width // 3,
                                             self.height // 2,
                                             anchor=NW,
                                             image=self.bird_icon)

    def set_all_images(self):
        self.bird_icon = self.get_image("images/bird.png",
                                        width=self.bird_width,
                                        height=self.bird_height)
        self.titul_icon = self.get_image("images/titul.jpg", 20, 20)
        self.star_icon = self.get_image("images/star.jpg", 20, 20)

    def get_image(self, path, width=SQUARE_SIZE, height=SQUARE_SIZE):
        img = Image.open(path)
        img = img.resize((width, height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def check_crash(self):
        top = self.barrier_top_deque[0]
        bottom = self.barrier_bottom_deque[0]

        bird_x_left = self.width // 3
        bird_x_right = self.width // 3 + self.bird_width
        bird_y_top = self.canvas.coords(self.bird)[1]
        bird_y_bottom = bird_y_top + self.bird_height

        if bird_y_top <= 0 or bird_y_bottom >= self.height:
            self.game_over()
            return
        elif bird_x_left >= self.canvas.coords(top)[2]:
            self.barrier_after_bird.append(self.barrier_top_deque.popleft())
            self.barrier_after_bird.append(self.barrier_bottom_deque.popleft())
            self.generate_barrier(40, 10, 1)
            self.update_score()
        elif bird_x_right >= self.canvas.coords(top)[0]:
            if (bird_y_top <= self.canvas.coords(top)[3] or
                    bird_y_bottom >= self.canvas.coords(bottom)[1]):
                self.game_over()
                return
        self.root.after(5, self.check_crash)

    def update_score(self):
        self.points += 1
        if self.points > self.record:
            self.record = self.points
        self.var_score.set("{}".format(self.points))
        self.var_record.set("{}".format(self.record))

    def game_over(self):
        self.barrier_speed = 0
        self.bird_speed = 0
        self.points_frame.destroy()
        self.show_game_over()
        self.show_result_points()

    def show_points_frame(self):
        self.points_frame = Frame(self.root, padx=5, pady=5)
        self.points_frame['bg'] = "white"

        record_image = Label(
            self.points_frame,
            image=self.titul_icon,
            bg="white"
        )

        score_image = Label(
            self.points_frame,
            image=self.star_icon,
            bg="white"
        )

        self.var_record = StringVar()
        record_points = Label(
            self.points_frame,
            textvariable=self.var_record,
            bg="white",
            font=30,
        )
        self.var_record.set("{}".format(self.record))

        self.var_score = StringVar()
        current_points = Label(
            self.points_frame,
            textvariable=self.var_score,
            bg="white",
            font=30
        )
        self.var_score.set("{}".format(self.points))

        self.points_frame.place(relx=0, rely=0)
        record_image.grid(row=0, column=0)
        record_points.grid(row=0, column=1)
        score_image.grid(row=1, column=0)
        current_points.grid(row=1, column=1)

    def show_result_points(self):
        result_points = Label(
            self.root,
            text="Total score: {} | Best score: {}".format(
                self.points,
                self.record
            ),
            bg="white"
        )
        result_points.place(relx=0.3, rely=0.3, relwidth=0.4, relheight=0.1)

    def show_game_over(self):
        restart_button = Button(self.root, text="Restart", font="40",
                                bg='red', fg="white",
                                command=self.game_restart)
        restart_button.place(relx=0.3, rely=0.4, relwidth=0.4, relheight=0.2)

    def game_restart(self):
        self.canvas.destroy()
        self.refresh_game()

    def move_barrier(self, barrier_deque):
        if self.barrier_speed:
            for rectangle in barrier_deque:
                self.canvas.move(rectangle, -self.barrier_speed, 0)
            self.root.after(12, self.move_barrier, barrier_deque)
        else:
            return

    def fly_down(self):
        self.canvas.move(self.bird, 0, self.bird_speed)
        self.root.after(10, self.fly_down)

    def fly_up(self):
        self.canvas.move(self.bird, 0, -self.bird_speed*20)

    def keypress(self, event):
        if event.keycode == 32 or event.keycode == 65:
            self.fly_up()


if __name__ == "__main__":
    fl = FlappyBird(root)
    fl.run()
