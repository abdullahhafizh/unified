import vlc
 
# importing time module
import time
import sys
 
# creating vlc media player object
media_player = vlc.MediaPlayer()
 
# toggling full screen
media_player.toggle_fullscreen()
 
# media object
media = vlc.Media("../_vVideo/2. \Video \Sosialisasi \Program \JakLingko.mp4")
 
# setting media to the media player
media_player.set_media(media)
 
# start playing video
media_player.play()
 
# wait so the video can be played for 5 seconds
# irrespective for length of video
time.sleep(5)