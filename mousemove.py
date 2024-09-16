import math
import socket

UDP_IP = "" #IP of your Raspberry
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class MovementController:
    def __init__(self):
        self.overflow_x = 0.0
        self.overflow_y = 0.0

    def __add_overflow(self, Input, Overflow):
        Integral = 0.0
        Overflow, Integral = math.modf(Input + Overflow)

        if Overflow > 1.0:
            Overflow, Integral = math.modf(Overflow)
            Input += Integral
        return Input, Overflow

    def mousemove(self, x, y, speed):
        if speed == 0:
            return

        u_x = x / speed
        u_y = y / speed

        x_ = y_ = 0.0

        for i in range(1, int(speed) + 1):
            xI = i * u_x
            yI = i * u_y

            xI, self.overflow_x = self.__add_overflow(xI, self.overflow_x)
            yI, self.overflow_y = self.__add_overflow(yI, self.overflow_y)

            final_x = int(xI - x_)
            final_y = int(yI - y_)

            if final_x != 0 or final_y != 0:
                self.__send_mouse_movement(final_x, final_y)
            
            x_ = xI
            y_ = yI

    def __send_mouse_movement(self, x, y):
        message = f"{x},{y}".encode()
        sock.sendto(message, (UDP_IP, UDP_PORT))