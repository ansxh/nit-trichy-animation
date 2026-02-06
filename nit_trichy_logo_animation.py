import tkinter as tk
import random
import math

# NIT Trichy logo animation with glowing rings and sparkles.
# Logo source: NIT Trichy (via Wikimedia Commons, CC BY-SA 4.0)

WIDTH, HEIGHT = 900, 700
BG = '#0b0b1a'

root = tk.Tk()
root.title('NIT Trichy Logo Animation')
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
canvas.pack()

# Load logo (PNG) and scale down if needed
logo = tk.PhotoImage(file='nitt_logo.png')
max_dim = 360
scale = max(1, int(max(logo.width(), logo.height()) / max_dim))
if scale > 1:
    logo = logo.subsample(scale, scale)

cx, cy = WIDTH // 2, HEIGHT // 2 - 40
canvas.create_image(cx, cy, image=logo)
canvas.create_text(
    cx, HEIGHT - 80,
    text='NIT Trichy',
    fill='#f6c453',
    font=('Times New Roman', 26, 'bold')
)

sparkles = []


def spawn_sparkles(n):
    for _ in range(n):
        ang = random.random() * math.tau
        radius = random.randint(70, 230)
        x = cx + math.cos(ang) * radius
        y = cy + math.sin(ang) * radius
        sparkles.append({
            'x': x,
            'y': y,
            'dx': math.cos(ang) * random.uniform(0.2, 0.8),
            'dy': math.sin(ang) * random.uniform(0.2, 0.8),
            'r': random.uniform(2.0, 4.5),
            'life': random.randint(20, 45),
            'color': random.choice(['#ffd166', '#f4a261', '#e76f51', '#ffbe0b'])
        })


def frame(tick):
    canvas.delete('spark')
    canvas.delete('glow')

    pulse = (math.sin(tick * 0.05) + 1) * 0.5

    for i in range(3):
        r = 175 + i * 24 + pulse * 12
        canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=random.choice(['#f6bd60', '#f4a261', '#ffd166']),
            width=2,
            tags='glow'
        )

    spawn_sparkles(5)
    alive = []
    for s in sparkles:
        s['x'] += s['dx']
        s['y'] += s['dy']
        s['r'] *= 0.97
        s['life'] -= 1
        if s['life'] > 0 and s['r'] > 0.6:
            canvas.create_oval(
                s['x'] - s['r'], s['y'] - s['r'],
                s['x'] + s['r'], s['y'] + s['r'],
                fill=s['color'], outline='',
                tags='spark'
            )
            alive.append(s)
    sparkles[:] = alive

    root.after(30, lambda: frame(tick + 1))


frame(0)
root.mainloop()
