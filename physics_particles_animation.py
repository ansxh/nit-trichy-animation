import math
import random
import time
import turtle as t

WIDTH = 1000
HEIGHT = 650
BG = "#080b14"

PARTICLE_COUNT = 36
DT = 0.02
TRAIL_DOT = 2

ORBIT_RADII = [80, 130, 190, 255, 320]
ECC_RANGE = (0.05, 0.28)
PRECESSION = 0.0009
NUCLEUS_RADIUS = 22
CAMERA_DIST = 900.0
PERSPECTIVE = 700.0
ATOM_SPIN = 0.0045
CAMERA_TILT = 0.007
ZOOM_BREATH = 0.006
ORBIT_WARP = 0.0015
SHOCKWAVE_SPEED = 2.2
SHOCKWAVE_GAP = 120
SHOCKWAVE_RINGS = 3
JUMP_CHANCE = 0.002
PHOTON_LIFE = 24
PHOTON_SPEED = 6.0
PHOTON_COLOR = "#7ff6ff"
CLOUD_POINTS = 80

PALETTE = [
    "#6ad1ff",
    "#ffcf6a",
    "#ff6aa2",
    "#7cffb2",
    "#b36aff",
]


def setup():
    t.setup(WIDTH, HEIGHT)
    t.title("Electron Orbits Animation")
    t.bgcolor(BG)
    t.colormode(255)
    t.tracer(False)
    t.hideturtle()
    t.penup()


class Particle:
    def __init__(self):
        self.semi_major = random.choice(ORBIT_RADII)
        self.ecc = random.uniform(*ECC_RANGE)
        self.angle = random.uniform(0, 2 * math.pi)
        self.arg_periapsis = random.uniform(0, 2 * math.pi)
        self.base_speed = random.uniform(0.004, 0.01) * (300 / self.semi_major)
        self.inclination = random.uniform(-0.9, 0.9)
        self.node = random.uniform(0, 2 * math.pi)
        self.color = random.choice(PALETTE)
        self.x3d = 0.0
        self.y3d = 0.0
        self.z3d = 0.0
        self.x = 0.0
        self.y = 0.0
        self.depth = 1.0
        self.jump_cooldown = random.randint(60, 220)

    def step(self):
        # Kepler-like motion: faster near periapsis
        r = (self.semi_major * (1 - self.ecc ** 2)) / (1 + self.ecc * math.cos(self.angle))
        ang_speed = self.base_speed * (self.semi_major / max(r, 1.0)) ** 2
        self.angle += ang_speed
        self.arg_periapsis += PRECESSION * (320 / self.semi_major)

        theta = self.angle + self.arg_periapsis
        # 3D position in orbital plane
        x1 = r * math.cos(theta)
        y1 = r * math.sin(theta)
        z1 = 0.0

        # Rotate by inclination around x-axis
        y2 = y1 * math.cos(self.inclination) - z1 * math.sin(self.inclination)
        z2 = y1 * math.sin(self.inclination) + z1 * math.cos(self.inclination)
        x2 = x1

        # Rotate by longitude of ascending node around z-axis
        x3 = x2 * math.cos(self.node) - y2 * math.sin(self.node)
        y3 = x2 * math.sin(self.node) + y2 * math.cos(self.node)
        z3 = z2

        self.x3d = x3
        self.y3d = y3
        self.z3d = z3


def draw_field_lines(shock_radius):
    t.color("#101b2e")
    t.pensize(1)
    for r in ORBIT_RADII:
        t.penup()
        t.goto(r, 0)
        t.pendown()
        t.circle(r)
        t.penup()
        t.goto(r + 8, 6)
        t.pendown()
        t.color("#93a7c6")
        t.write(f"n={ORBIT_RADII.index(r)+1}", font=("Arial", 10, "normal"))
        t.color("#101b2e")

    t.penup()
    t.goto(0, -NUCLEUS_RADIUS)
    t.pendown()
    t.color("#ff5454")
    t.begin_fill()
    t.circle(NUCLEUS_RADIUS)
    t.end_fill()
    t.color("#ff8f8f")
    t.dot(NUCLEUS_RADIUS * 1.4)

    # Probability cloud hint
    t.color("#16243d")
    for _ in range(CLOUD_POINTS):
        ring = random.choice(ORBIT_RADII)
        ang = random.uniform(0, 2 * math.pi)
        jitter = random.uniform(-8, 8)
        t.penup()
        t.goto((ring + jitter) * math.cos(ang), (ring + jitter) * math.sin(ang))
        t.pendown()
        t.dot(1)

    # Nucleus shockwave rings
    for k in range(SHOCKWAVE_RINGS):
        radius = shock_radius - k * SHOCKWAVE_GAP
        if radius <= 0:
            continue
        fade = max(0.15, 1.0 - (k / max(1, SHOCKWAVE_RINGS - 1)))
        t.penup()
        t.goto(radius, 0)
        t.pendown()
        # Glow: draw a soft outer ring then a bright core ring
        t.pensize(4)
        t.color("#ffd1d8")
        t.circle(radius)
        t.pensize(2)
        t.color("#ff6b7c")
        t.circle(radius)


def draw_particles(particles):
    # Draw farthest first for simple depth cue
    for p in sorted(particles, key=lambda p: p.z3d):
        glow = min(255, int(140 + 90 * abs(math.sin(p.angle))))
        size = max(1, int(TRAIL_DOT * (0.7 + 0.9 * p.depth)))
        t.color(p.color)
        t.goto(p.x, p.y)
        t.dot(size)

        # Soft glow dot
        t.color((glow, glow, 255))
        t.dot(size + 1)

def draw_photons(photons):
    for ph in photons[:]:
        ph["x"] += ph["vx"]
        ph["y"] += ph["vy"]
        ph["life"] -= 1
        if ph["life"] <= 0:
            photons.remove(ph)
            continue
        t.penup()
        t.goto(ph["x"], ph["y"])
        t.pendown()
        t.pensize(2)
        t.color(PHOTON_COLOR)
        t.dot(3)


def animate(particles):
    spin = 0.0
    tilt = 0.0
    zoom_phase = 0.0
    warp = 0.0
    shock = 0.0
    photons = []
    while True:
        t.clear()
        draw_field_lines(shock)
        for p in particles:
            p.step()

            # Occasional energy level jump with photon flash
            p.jump_cooldown -= 1
            if p.jump_cooldown <= 0 and random.random() < JUMP_CHANCE:
                old_radius = p.semi_major
                choices = [r for r in ORBIT_RADII if r != old_radius]
                p.semi_major = random.choice(choices)
                p.ecc = random.uniform(*ECC_RANGE)
                p.jump_cooldown = random.randint(120, 300)
                # Photon burst
                ang = random.uniform(0, 2 * math.pi)
                photons.append({
                    "x": 0.0,
                    "y": 0.0,
                    "vx": PHOTON_SPEED * math.cos(ang),
                    "vy": PHOTON_SPEED * math.sin(ang),
                    "life": PHOTON_LIFE
                })

        # Rotate the whole system around the y-axis for stronger 3D feel
        spin += ATOM_SPIN
        tilt += CAMERA_TILT
        zoom_phase += ZOOM_BREATH
        warp += ORBIT_WARP
        shock += SHOCKWAVE_SPEED
        if shock > max(ORBIT_RADII) + SHOCKWAVE_GAP:
            shock = 0.0
        cos_s = math.cos(spin)
        sin_s = math.sin(spin)
        cos_t = math.cos(tilt)
        sin_t = math.sin(tilt)
        zoom = 1.0 + 0.12 * math.sin(zoom_phase)
        for p in particles:
            # Subtle orbital plane wobble
            wobble = 1.0 + 0.08 * math.sin(warp + p.angle)
            xw = p.x3d * wobble
            zw = p.z3d * wobble

            x = xw * cos_s + zw * sin_s
            z = -xw * sin_s + zw * cos_s
            y = p.y3d * cos_t - z * sin_t
            z = p.y3d * sin_t + z * cos_t
            depth = CAMERA_DIST / (CAMERA_DIST + z + PERSPECTIVE)
            p.x = x * depth * zoom
            p.y = y * depth * zoom
            p.z3d = z
            p.depth = depth

        draw_photons(photons)
        draw_particles(particles)
        t.update()
        time.sleep(DT)


def main():
    setup()
    particles = [Particle() for _ in range(PARTICLE_COUNT)]
    animate(particles)


if __name__ == "__main__":
    main()
