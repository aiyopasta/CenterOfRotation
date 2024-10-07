import numpy as np
import pyglet
from pyglet.gl import *
from pyglet import shapes


# Suppress sci-notation
np.set_printoptions(suppress=True)

# Initialize the window
width, height = 800, 800
config = pyglet.gl.Config(double_buffer=True, major_version=3, minor_version=3)
window = pyglet.window.Window(width=width, height=height, caption="Center of rotation demo", config=config)

# The usual coordinate shift
def A(v: np.ndarray):
    global width, height
    return v + np.array([width / 2.0, height / 2.0])

# 2D rotation matrix
def rot_mat(theta_):
    return np.array([
        [np.cos(theta_), -np.sin(theta_)],
        [np.sin(theta_), np.cos(theta_)]
    ])


# Easing
def ease_inout(t_):
    return np.power(t_, 2) / (np.power(t_, 2) + np.power(1 - t_, 2))


# Triangle stuff
theta = 0.0
tri_scale = 100.0
sec = lambda x: 1. / np.cos(x)
def triangle(t_):
    assert 0.0 <= t_ <= 1.0
    tau = 2 * np.pi * t_
    dist = sec(tau - (np.pi / 3) - (2 * np.pi / 3 * np.floor(3 * tau / (2 * np.pi))))
    return np.array([tri_scale * np.cos(tau) * dist / 2, tri_scale * np.sin(tau) * dist / 2])


# Animation parameter
t = 0.0
dt = 0.01


# This function is called SEPARATELY every dt seconds. on_draw() is called as fast as possible, separately!
# Update is simply where game / simulation logic goes.
def update(dt_):
    global t, theta

    # Update animation parameter
    t = min(max(t + dt, 0.0), 1.0)

    # Animate using it
    final_theta = np.pi / 6.0  # TODO: Set the desired rotation angle here!
    theta = final_theta * ease_inout(t)


# APPLE COLORS!
colors = {
    'red': np.array([255, 59, 48]),
    'orange': np.array([255, 149, 0]),
    'yellow': np.array([255, 204, 0]),
    'green': np.array([40, 205, 65]),
    'mint': np.array([0, 199, 190]),
    'teal': np.array([89, 173, 196]),
    'cyan': np.array([85, 190, 240]),
    'blue': np.array([0, 122, 255]),
    'indigo': np.array([88, 86, 214]),
    'purple': np.array([175, 82, 222]),
    'pink': np.array([255, 45, 85]),
    'brown': np.array([162, 132, 94]),
    'gray': np.array([142, 142, 147]),
    'white': np.array([255, 255, 255])
}


@window.event
def on_draw():
    global theta
    window.clear()

    # Sample and draw the rectangle
    pts = [A(rot_mat(theta) @ triangle(t_)) for t_ in np.linspace(0.0, 1.0, 100, endpoint=True)]
    batch = pyglet.graphics.Batch()
    line_objs = []
    for i in range(len(pts) - 1):
        line_objs.append(shapes.Line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], width=6, color=colors['red'], batch=batch))

    batch.draw()

    # Theta angle
    label = pyglet.text.Label("φ=" + str(np.round(theta / np.pi, 3)) + 'π',
                              font_name='CMU Serif',
                              font_size=37,
                              x=width // 2, y=int(0.9 * height),
                              anchor_x='center', anchor_y='center',
                              color=(255, 255, 255, 255))

    label.draw()


@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)


# Schedule the update function to be called at 60Hz
pyglet.clock.schedule_interval(update, 1 / 60.0)

# Run the Pyglet event loop
pyglet.app.run()