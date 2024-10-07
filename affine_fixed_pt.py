import os

import numpy as np
import pyglet
from pyglet.gl import *
from pyglet import shapes

# Suppress sci-notation
np.set_printoptions(suppress=True)

# Save the animation? TODO: Make sure you're saving to correct destination!!
save_anim = False

# Animation saving setup
count = 0  # two vars that just match my usual animation setup
frame = -1
path_to_save = '/Users/adityaabhyankar/Desktop/Programming/CIS515/CenterOfRotation/output'
if save_anim:
    for filename in os.listdir(path_to_save):
        # Check if the file name follows the required format
        b1 = filename.startswith("frame") and filename.endswith(".png")
        b2 = filename.startswith("output.mp4")
        if b1 or b2:
            os.remove(os.path.join(path_to_save, filename))
            print('Deleted frame ' + filename)

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
tri_scale = 100.0
sec = lambda x: 1. / np.cos(x)
def triangle(t_):
    assert 0.0 <= t_ <= 1.0
    tau = 2 * np.pi * t_
    dist = sec(tau - (np.pi / 3) - (2 * np.pi / 3 * np.floor(3 * tau / (2 * np.pi))))
    return np.array([tri_scale * np.cos(tau) * dist / 2, tri_scale * np.sin(tau) * dist / 2])


# Define affine map # TODO: THESE ARE THE ONES TO PLAY AROUND WITH!
final_theta = np.pi / 2.25
final_a = np.array([-50.0, -300.0])


# Animation parameters
t = 0.0
dt = 0.005
theta = 0.0
a = np.array([0.0, 0.0])

# This function is called SEPARATELY every dt seconds.
def update(dt_):
    global t, theta, a, final_theta, final_a

    # Update animation parameter
    t = min(max(t + dt, 0.0), 1.0)

    # Animate using it
    theta = final_theta * ease_inout(t)
    a = final_a * ease_inout(t)


# Apple colors!
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
    global theta, a, width, height, final_theta, final_a
    window.clear()

    # Draw static grid
    shapes.Circle(*A(np.array([0, 0])), radius=5, color=colors['gray']).draw()
    spacing = 100.0
    batch = pyglet.graphics.Batch()
    grid_objs = []
    for i in range(0, int(max(width, height) + spacing), int(spacing)):
        grid_objs.append(shapes.Line(i, 0, i, height, batch=batch, color=colors['gray']))  # Vertical
        grid_objs.append(shapes.Line(0, i, width, i, batch=batch, color=colors['gray']))  # Horizontal
    batch.draw()

    # Draw animated grid
    anim_batch = pyglet.graphics.Batch()
    anim_grid_objs = []
    for i in range(-int(max(width, height) / spacing) - 1, int(max(width, height) / spacing) + 1):
        start_vert = A((rot_mat(theta) @ np.array([i * spacing, -height])) + a)
        end_vert = A((rot_mat(theta) @ np.array([i * spacing, height])) + a)
        anim_grid_objs.append(shapes.Line(start_vert[0], start_vert[1], end_vert[0], end_vert[1], batch=anim_batch, color=colors['red']))

        start_horiz = A((rot_mat(theta) @ np.array([-width, i * spacing])) + a)
        end_horiz = A((rot_mat(theta) @ np.array([width, i * spacing])) + a)
        anim_grid_objs.append(shapes.Line(start_horiz[0], start_horiz[1], end_horiz[0], end_horiz[1], batch=anim_batch, color=colors['red']))
    anim_batch.draw()

    # Draw animated origin
    anim_origin = A((rot_mat(theta) @ np.array([0, 0])) + a)
    shapes.Circle(anim_origin[0], anim_origin[1], radius=5, color=colors['red']).draw()

    # Sample and draw the triangle
    pts = [A((rot_mat(theta) @ triangle(t_)) + a) for t_ in np.linspace(0.0, 1.0, 100, endpoint=True)]
    tri_batch = pyglet.graphics.Batch()
    tri_objs = []
    for i in range(len(pts) - 1):
        tri_objs.append(shapes.Line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], width=6, color=colors['red'], batch=tri_batch))
    tri_batch.draw()

    # Draw center of rotation
    c = (1 / (2 * np.sin(final_theta / 2))) * rot_mat((np.pi / 2.0) - (final_theta / 2.0)) @ final_a
    c_moving = (rot_mat(theta) @ c) + a
    shapes.Circle(*A(c), radius=15, color=colors['white']).draw()
    shapes.Circle(*A(c_moving), radius=10, color=colors['red']).draw()

    # Display slightly opaque black rectangle underneath text
    shapes.Rectangle(*A(np.array([-200, 190])), 400, 150, color=(0, 0, 0, 190)).draw()

    # Display angle and translation text
    cols = [colors['mint'], colors['mint'], colors['yellow']]
    for i, text in enumerate(["φ=" + str(np.round(theta / np.pi, 3)) + 'π',
                              'a=' + str(a),
                              'fixed point:' + str(np.round(c, 3))]):
        col = cols[i]
        label = pyglet.text.Label(text,
                                  font_name='CMU Serif',
                                  font_size=20,
                                  x=width // 2, y=int(0.9 * height - (i * 50.0)),
                                  anchor_x='center', anchor_y='center',
                                  color=[*col, 255])
        label.draw()

    # Save frame, increment counts —————————————————————————————————————————————————————————————————————————————————
    global count, save_anim, path_to_save
    count += 1
    if save_anim:
        image = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()
        image.save(path_to_save+'/frame'+str(count)+'.png')
        print('Saved frame '+str(count))



@window.event
def on_resize(w, h):
    glViewport(0, 0, w, h)


@window.event
def on_close():
    global save_anim, path_to_save, window

    # Compile all images into video with ffmpeg
    if save_anim:
        input_files = path_to_save + '/frame%d.png'
        output_file = path_to_save + '/output.mp4'
        ffmpeg_path = "/opt/homebrew/bin/ffmpeg"
        os.system(f'{ffmpeg_path} -r 60 -i {input_files} -vcodec libx264 -crf 25 -pix_fmt yuv420p -vf "eq=brightness=0.00:saturation=1.0" {output_file} > /dev/null 2>&1')
        print('Saved video to ' + output_file)

    window.close()


# Schedule the update function to be called at 60Hz
pyglet.clock.schedule_interval(update, 1 / 60.0)

# Run the Pyglet event loop
pyglet.app.run()
