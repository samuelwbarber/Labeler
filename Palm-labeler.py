import cv2
import numpy as np
import os

# ----------- Settings -----------
image_path_template = r'C:\Users\sbarb\Image-Labeler\images\{:03d}_1.JPG'
save_path_template  = r'C:\Users\sbarb\Image-Labeler\labeled\{:03d}_1_labeled.png'
start_index         = 3
line_thickness      = 8
color_options = {
    1: (0, 0, 255),   # Red
    2: (0, 255, 0),   # Green
    3: (255, 0, 0),   # Blue
}
current_color = color_options[1]  # Start with red
# --------------------------------

drawing = False
last_point = None
image_index = start_index
last_point_orig = None

max_width = 800
max_height = 600
lines_drawn = 0

full_image = None
full_drawing_layer = None
scale_factor = 1.0


def resize_image(img):
    h, w = img.shape[:2]
    scale = min(max_width / w, max_height / h, 1.0)
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized, scale
    return img.copy(), 1.0


def load_image(index):
    path = image_path_template.format(index)
    if os.path.exists(path):
        img = cv2.imread(path)
        display_img, scale = resize_image(img)
        return img, display_img, scale  # return original, display, scale
    else:
        print(f"[!] Image not found: {path}")
        return None, None, None


color_order = [(0, 0, 255), (255, 0, 0), (0, 255, 0)]  # red, blue, green
current_color_index = 0  # start at red
current_color = color_order[current_color_index]

def draw(event, x, y, flags, param):
    global drawing, last_point, last_point_orig
    global image, image_copy, drawing_layer, image_index
    global current_color_index, current_color, lines_drawn
    global full_image, full_drawing_layer, scale_factor

    if scale_factor != 1.0:
        x_orig = int(x / scale_factor)
        y_orig = int(y / scale_factor)
    else:
        x_orig, y_orig = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        last_point = (x, y)
        last_point_orig = (x_orig, y_orig)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        if last_point and last_point_orig:
            cv2.line(image_copy, last_point, (x, y), current_color, line_thickness)
            cv2.line(drawing_layer, last_point, (x, y), current_color, line_thickness)
            cv2.line(full_drawing_layer, last_point_orig, (x_orig, y_orig), current_color, line_thickness)
            last_point = (x, y)
            last_point_orig = (x_orig, y_orig)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        last_point = None
        last_point_orig = None

        lines_drawn += 1
        current_color_index = (current_color_index + 1) % len(color_order)
        current_color = color_order[current_color_index]
        print(f"Switched to color {['RED','BLUE','GREEN'][current_color_index]}")
        print(f"Lines drawn: {lines_drawn}/3")

        if lines_drawn >= 3:
            save_path = save_path_template.format(image_index)
            cv2.imwrite(save_path, full_drawing_layer)
            print(f"[✓] Saved: {save_path}")
            lines_drawn = 0

            image_index += 1
            orig, disp, scale = load_image(image_index)
            if disp is not None:
                full_image = orig
                image = disp
                image_copy = image.copy()
                drawing_layer = np.zeros_like(image)
                full_drawing_layer = np.zeros_like(full_image)
                scale_factor = scale
                current_color_index = 0
                current_color = color_order[current_color_index]
                print("Reset color to RED for new image")
            else:
                print("No more images. Exiting.")
                cv2.destroyAllWindows()




# Load initial image
full_image, image, scale_factor = load_image(image_index)
image_copy = image.copy()
drawing_layer = np.zeros_like(image)
full_drawing_layer = np.zeros_like(full_image)
if image is None:
    raise FileNotFoundError(f"Starting image not found: {image_path_template.format(image_index)}")

image_copy = image.copy()
drawing_layer = np.zeros_like(image)

cv2.namedWindow('Draw')
cv2.setMouseCallback('Draw', draw)

print("Left click to draw.")
print("Press 1 = Red, 2 = Green, 3 = Blue.")
print("Right click = Save and load next image.")
print("Press Q to quit.")

while True:
    cv2.imshow('Draw', image_copy)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('1'):
        current_color = color_options[1]
        print("Switched to RED")
    elif key == ord('2'):
        current_color = color_options[2]
        print("Switched to GREEN")
    elif key == ord('3'):
        current_color = color_options[3]
        print("Switched to BLUE")
    elif key == ord('q'):
        print("Quitting.")
        break

cv2.destroyAllWindows()
