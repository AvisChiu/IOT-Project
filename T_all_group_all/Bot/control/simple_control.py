import bot

class _Getch:
    
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


if __name__ == '__main__':

	front_control = bot.FrontControl()
	front_control.start()
	rear_control = bot.RearControl()
	rear_control.start()
	getch = _Getch()

	while True:
		char = getch()
		#print(char)
		#if char == 'q':
		#	break
		
		if char == 'q':
			rear_control.set_speed(0)
		
		elif char == 'w':
			rear_control.set_speed(1)
			
		elif char == 'a':
			front_control.change_angle(0)
			
		elif char == 'd':
			front_control.change_angle(1)
			
		elif char == 's':
			front_control.change_angle(0.5)

			
		else:
			break
	
	front_control.change_angle(0.5)
	rear_control.set_speed(0)
	
