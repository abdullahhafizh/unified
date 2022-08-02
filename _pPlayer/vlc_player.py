from vlc import Instance
import os
from pathlib import Path


class VLC:
    def __init__(self):
        self.Player = Instance('--loop')

    def addPlaylist(self, path):
        self.mediaList = self.Player.media_list_new()
        medias = os.listdir(path)
        for s in medias:
            self.mediaList.add_media(self.Player.media_new(os.path.join(path,s)))
        self.listPlayer = self.Player.media_list_player_new()
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
    up_dir = Path(__file__).resolve().parents[1] + "_vVideo"
    print(up_dir)
    path = up_dir
    player.addPlaylist(path)
    player.play()