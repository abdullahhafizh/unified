from vlc import Instance
import os, sys, time
from pathlib import Path
from pymouse import PyMouseEvent


def fibo():
    a = 0
    yield a
    b = 1
    yield b
    while True:
        a, b = b, a+b
        yield b


class Clickonacci(PyMouseEvent):
    def __init__(self):
        PyMouseEvent.__init__(self)
        self.fibo = fibo()

    def click(self, x, y, button, press):
        if button == 1:
            if press:
                print('Touchscreen Detected, Exit')
                sys.exit(0)
        else:  # Exit if any other mouse button used
            self.stop()


class VLC:
    def __init__(self):
        self.Player = Instance('--loop', '--fullscreen')

    def addPlaylist(self, path):
        self.mediaList = self.Player.media_list_new()
        medias = os.listdir(path)
        for s in medias:
            self.mediaList.add_media(self.Player.media_new(os.path.join(path,s)))
        print('Media Length', len(self.mediaList))
        self.listPlayer = self.Player.media_list_player_new()
        #self.listPlayer.toggle_fullscreen()
        #self.listPlayer.set_fullscreen(True)
        self.listPlayer.set_media_list(self.mediaList)
    def play(self):
        self.listPlayer.play()
    def next(self):
        self.listPlayer.next()
    def pause(self):
        self.listPlayer.pause()
    def previous(self):
        self.listPlayer.previous()
    def stop(self):
        self.listPlayer.stop()


if __name__ == '__main__':
    player = VLC()
    up_dir = Path(__file__).resolve().parents[1]
    path = os.path.join(up_dir, "_vVideo")
    player.addPlaylist(path)
    print(path)
    player.play()
    touchscreen = Clickonacci()
    touchscreen.run()
    time.sleep(1)