import bettercam
import numpy as np
import win32api
import threading
import time
from com import uninstallCOMPort
from mousemove import MovementController

mouse = MovementController()
uninstallCOMPort()

smooth = 2

camera = bettercam.create(output_color="RGB")
lock = threading.Lock()

resolutionX = win32api.GetSystemMetrics(0)
resolutionY = win32api.GetSystemMetrics(1)

fovX = 50
fovY = 50

left = (resolutionX - fovX) // 2
top = (resolutionY - fovY) // 2
right = left + fovX
bottom = top + fovY
region = (left, top, right, bottom)

cX = fovX // 2
cY = fovY // 2
center = np.array([cY, cX])
offsetY = 2
offsetX = 0
color = "PURPLE"

recoil_offset = 0
recoil_length = 30  # Defina o valor apropriado
timer_start = time.time()
rcs = True

print("só o auxilio")

def get_color_mask(frame, color):
    match color:
        case "PURPLE":
            r_min, r_max, g_min, g_max, b_min, b_max = (144, 255, 60, 99, 194, 255) #FF33FF
        case "GREEN":
            r_min, r_max, g_min, g_max, b_min, b_max = (30, 97, 240, 255, 30, 110) #2EFB00
        case _:
            return None
    
    mask = (
        (frame[:, :, 0] >= r_min) & (frame[:, :, 0] <= r_max) &
        (frame[:, :, 1] >= g_min) & (frame[:, :, 1] <= g_max) &
        (frame[:, :, 2] >= b_min) & (frame[:, :, 2] <= b_max)
    )

    return mask

def recoil_control():
    global recoil_offset, timer_start
    elapsed_time = (time.time() - timer_start) * 1000  # Tempo em milissegundos
    if win32api.GetAsyncKeyState(0x01) & 0x8000 and rcs:  # Verifica se o botão esquerdo do mouse está pressionado
        if elapsed_time > 90.0:
            if recoil_offset < recoil_length:
                recoil_offset += 0.125  # Aumenta gradualmente o recoil
            else:
                recoil_offset = recoil_length
        else:
            if recoil_offset > 0:
                recoil_offset -= 0.125  
            else:
                recoil_offset = 0
                timer_start = time.time()  
    else:
        recoil_offset = 0  

def aimbot():
    with lock:
        frame = camera.grab(region=region)
        if frame is None:
            return
        mask = get_color_mask(frame, color)
        if mask is not None:
            points = np.transpose(np.nonzero(mask))
            if len(points) > 0:
                distances = np.linalg.norm(points - center, axis=1)
                combined_scores = points[:, 0] + distances
                closest_point_index = np.argmin(combined_scores)
                closest_point = points[closest_point_index]
                x_diff = closest_point[1] - cX
                y_diff = closest_point[0] - cY
                y_adjusted_magnet = y_diff + offsetY
                x_adjusted_magnet = x_diff + offsetX

                recoil_control()
                y_adjusted_magnet += recoil_offset  # Ajustar a coordenada Y somando o recoil (movendo para baixo)

                mouse.mousemove(int(x_adjusted_magnet), int(y_adjusted_magnet), int(smooth))

aimbot_thread = threading.Thread(target=aimbot)
aimbot_thread.daemon = True
aimbot_thread.start()

if __name__ == "__main__":
    try:
        while True:
            if win32api.GetAsyncKeyState(18) & 0x8000:
                aimbot()
            time.sleep(0.001)
    except Exception as e:
        print(f"An error occurred: {e}")
