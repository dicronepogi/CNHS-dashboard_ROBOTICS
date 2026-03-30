import turtle
import math
import random
import time


def main():
    s = turtle.Screen()
    s.bgcolor("black")
    s.setup(width=600, height=800)
    s.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()

    heart_colors = ["#00FFFF", "#00E5FF", "#00B8D4", "#2979FF", "#2962FF", "#1565C0"]

    def heart_path(angle, scale):
        x = scale * (16 * math.sin(angle) ** 3)
        y = scale * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        return x, y

    def draw_mini_heart(x, y, color):
        t.penup()
        t.goto(x, y)
        t.setheading(0)
        t.color(color)
        t.begin_fill()
        t.pendown()
        t.setheading(140)
        t.forward(10)
        t.circle(-5, 200)
        t.setheading(60)
        t.circle(-5, 200)
        t.forward(10)
        t.end_fill()

    for i in range(360, 0, -3):
        angle = math.radians(i)
        hx, hy = heart_path(angle, 13)
        current_color = heart_colors[(i // 12) % len(heart_colors)]
        draw_mini_heart(hx, hy, current_color)

        if i % 3 == 0:
            s.update()
            time.sleep(0.04)

    t.penup()
    t.goto(0, -25)

    for glow_size in range(12, 0, -2):
        t.color("#004d00")
        t.write("goodbye 10au 25-26", align="center", font=("Arial Black", 26 + glow_size, "bold"))

    t.color("#00FF00")
    t.write("goodbye 10au 25-26", align="center", font=("Arial Black", 26, "bold"))

    t.goto(0, -320)
    t.color("#00FFFF")
    t.write("made by dicronepogi", align="center", font=("Courier New", 18, "bold"))
    s.update()

    f = turtle.Turtle()
    f.hideturtle()
    f.width(2)
    firework_colors = ["#FF0000", "#00FF00", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#FFA500", "#FFD700",
                       "#ADFF2F", "#FF69B4"]

    while True:
        f.clear()
        for _ in range(12):
            fx = random.randint(-250, 250)
            fy = random.randint(-350, 350)

            if abs(fx) < 180 and abs(fy) < 150:
                continue

            color = random.choice(firework_colors)
            f.color(color)

            burst_size = random.randint(40, 100)
            for _ in range(15):
                f.penup()
                f.goto(fx, fy)
                f.setheading(random.randint(0, 360))
                f.pendown()
                f.forward(burst_size)
                f.dot(random.randint(3, 7), color)

        s.update()
        time.sleep(0.3)


if __name__ == "__main__":
    main()