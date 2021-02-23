ffmpeg -f v4l2 -i /dev/video0 \
-profile:v high -pix_fmt yuvj420p -level:v 4.1 -preset ultrafast -tune zerolatency \
-vcodec libx264 -r 10 -b:v 512k -s 640x360 \
-acodec aac -ac 2 -ab 32k -ar 44100 \
-f mpegts -flush_packets 0 udp://$1:5000?pkt_size=1316

