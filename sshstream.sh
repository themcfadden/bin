#ssh mattmc@$1 ffmpeg -an -f v4l2 -i /dev/video0 -r 10 -b:v 500k -f matroska | mplayer - -idle -demuxer matroska
# replace -an with -f alsa -i pulse. Needs more work and understanding.

ssh mattmc@$1 ffmpeg -an -f video4linux2 -s 640x480 -i /dev/video0 -r 10 -b:v 500k -f matroska - | mplayer - -idle -demuxer matroska
