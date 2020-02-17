#!/usr/bin/env python3
"""
by Poikilos
This is an experimental script that strips out chunks from the world for
the purpose of world conversion tests.
"""
from __future__ import division  # Make Py2 only do floor division if //
import os
import sys
import shutil
from PIL import Image, ImageDraw

world_path = os.getcwd()
world_flag_dir = 'region'
try_flag_path = os.path.join(world_path, world_flag_dir)
if not os.path.isdir(try_flag_path):
    print("This ({}) is apparently not a world, as the {} directory is"
          " not present.".format(world_path, world_flag_dir))
    exit(1)

region_path = os.path.join(world_path, 'region')
worlds_path = os.path.abspath(os.path.join(world_path, os.pardir))
min_x = 0
min_x_name = None
max_x = 0
max_x_name = None
min_z = 0
min_z_name = None
max_z = 0
max_z_name = None
smallest_pos_x = None
smallest_pos_z = None
smallest_neg_x = None
smallest_neg_z = None
print("detecting edges...")
for sub in os.listdir(region_path):
    sub_path = os.path.join(region_path, sub)
    if not sub.startswith("."):
        parts = sub.split(".")
        try:
            tmp, x, z, ext = parts
        except ValueError:
            print("Unknown file '{}' (expected filename like r.<quantized_x>.<quantized_z>.mca)")
            continue
        if ext != "mca":
            print("Unknown file extension for '{}' (expected filename like r.<quantized_x>.<quantized_z>.mca)")
            continue
        x = int(x)
        z = int(z)
        if x >= 0:
            if (smallest_pos_x is None) or (x < smallest_pos_x):
                smallest_pos_x = x
        else:
            if (smallest_neg_x is None) or (x > smallest_neg_x):
                smallest_neg_x = x
        if z >= 0:
            if (smallest_pos_z is None) or (z < smallest_pos_z):
                smallest_pos_z = z
        else:
            if (smallest_neg_z is None) or (z > smallest_neg_z):
                smallest_neg_z = z
        if x < min_x:
            min_x = x
            min_x_name = sub
        if x > max_x:
            max_x = x
            max_x_name = sub
        if z < min_z:
            min_z = z
            min_z_name = sub
        if z > max_z:
            max_z = z
            max_z_name = sub
print("edges (quantized by 16):")
print("  min_x: {}".format(min_x))
print("  min_x_name: {}".format(min_x_name))
print("  max_x: {}".format(max_x))
print("  max_x_name: {}".format(max_x_name))
print("  min_z: {}".format(min_z))
print("  min_z_name: {}".format(min_z_name))
print("  max_z: {}".format(max_z))
print("  max_z_name: {}".format(max_z_name))
print("  smallest_pos_x: {}".format(smallest_pos_x))
print("  smallest_pos_z: {}".format(smallest_pos_z))
print("  smallest_neg_x: {}".format(smallest_neg_x))
print("  smallest_neg_z: {}".format(smallest_neg_z))


big_w = max_x - min_x
big_h = max_z - min_z

quantize = 10
quantize_f = float(quantize)

w = big_w // quantize + 2
h = big_h // quantize + 2

print("Creating new {}x{} image...".format(w, h))
im = Image.new('RGB', (w, h))
# draw = ImageDraw.Draw(im)
# See https://www.geeksforgeeks.org/python-pil-getpixel-method/
px = im.load()

print("Drawing chunk density map (a density map is necessary since"
      " worlds are often HUGE if using multiworld)...")

for sub in os.listdir(region_path):
    sub_path = os.path.join(region_path, sub)
    if not sub.startswith("."):
        parts = sub.split(".")
        try:
            tmp, big_x, big_z, ext = parts
        except ValueError:
            continue
        if ext != "mca":
            continue
        big_x = int(big_x)
        big_z = int(big_z)
        big_x -= min_x
        big_z -= min_z
        big_y = h - big_z  # z in 2D (flipped cartesian on computers)
        x = round(float(big_x) / quantize_f)
        y = round(float(big_y) / quantize_f)
        try:
            color = px[x, y]
            if color[0] + color[1] + color[2] == 0:
                # print("setting {},{}...".format(x, y))
                px[x, y] = (64, 0, 0)  # dark red
            else:
                # print("heating {},{}...".format(x, y))
                heat = 32
                # make already-used pixel "hotter"
                if color[0] < 255:
                    px[x, y] = color[0] + heat, color[1], color[2]
                elif color[1] < 255:
                    px[x, y] = color[0], color[1] + heat, color[2]
                elif color[2] < 255:
                    px[x, y] = color[0], color[1], color[2] + heat
            # px[x, y] = 128, 0, 0
        except IndexError as e:
            print("Out of range: ({}, {})".format(x, y))

# del draw
name = "chunk-heatmap-quantized-{}.png".format(quantize)
im.save(name, "PNG")
im.close()
print("See '{}' in {}.".format(name, os.getcwd()))
print("If using MultiWorld, the image may be mostly blank except a"
      " small representation ((1/{})/16 size) on the far right"
      " edge.".format(quantize))
world_name = os.path.split(world_path)[1]
cut_name = world_name + "-mapcut-parts"
cut_path = os.path.join(worlds_path, cut_name)
cut_region_path = os.path.join(cut_path, 'region')
if not os.path.isdir(cut_region_path):
    os.makedirs(cut_region_path)

def usage():
    print("* Specify: {} <left> <top> <right> <bottom>\n\n(inclusive)"
          " to crop the"
          " world (in locations quantized by 16) and put the"
          " cuttings in "
          "'{}'".format(sys.argv[0], cut_region_path))

if len(sys.argv) != 5:
    usage()
    exit(0)

tmp, left, top, right, bottom = sys.argv
left = int(left)
top = int(top)
right = int(right)
bottom = int(bottom)
print("Cropping to {},{},{},{} (left, top, right, bottom)".format(left, top, right, bottom))
moved_count = 0
overlap_count = 0
total_count = 0
for sub in os.listdir(region_path):
    sub_path = os.path.join(region_path, sub)
    dst_path = os.path.join(cut_region_path, sub)
    if not sub.startswith("."):
        parts = sub.split(".")
        try:
            tmp, big_x, big_z, ext = parts
        except ValueError:
            continue
        if ext != "mca":
            continue
        total_count += 1
        big_x = int(big_x)
        big_z = int(big_z)
        if (big_x < left) or (big_x > right) or \
                (big_z < bottom) or (big_z > top):
            if not os.path.exists(dst_path):
                shutil.move(sub_path, dst_path)
                moved_count += 1
            else:
                print("ERROR: '{}' already exists.".format(dst_path))
                overlap_count += 1
print("kept: {} file(s)".format(total_count - moved_count))
print("moved: {} file(s)".format(moved_count))
if overlap_count > 0:
    print("already existed: {} file(s)".format(overlap_count))
