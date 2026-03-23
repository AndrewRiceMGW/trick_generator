#!/bin/bash

# Create 512x512 icon with rollerblade graphic
convert -size 512x512 gradient:'#667eea-#764ba2' \( \
    -size 512x512 xc:none \
    -fill white -stroke white -strokewidth 4 \
    -draw "path 'M 150,200 L 200,150 L 320,150 L 350,180 L 350,220 L 320,250 L 150,250 Z'" \
    -draw "path 'M 320,150 L 340,140 L 360,150 L 350,180 Z'" \
    -draw "circle 170,280 170,300" \
    -draw "circle 220,280 220,300" \
    -draw "circle 270,280 270,300" \
    -draw "circle 320,280 320,300" \
    -fill none -stroke white -strokewidth 3 \
    -draw "circle 170,280 170,295" \
    -draw "circle 220,280 220,295" \
    -draw "circle 270,280 270,295" \
    -draw "circle 320,280 320,295" \
    -fill white -stroke none \
    -pointsize 60 -font DejaVu-Sans-Bold \
    -gravity south -annotate +0+30 "BETA" \
\) -compose over -composite icon-512.png

# Create 192x192 icon
convert -size 192x192 gradient:'#667eea-#764ba2' \( \
    -size 192x192 xc:none \
    -fill white -stroke white -strokewidth 2 \
    -draw "path 'M 55,75 L 75,55 L 120,55 L 130,65 L 130,80 L 120,90 L 55,90 Z'" \
    -draw "path 'M 120,55 L 128,50 L 135,55 L 130,65 Z'" \
    -draw "circle 63,102 63,109" \
    -draw "circle 82,102 82,109" \
    -draw "circle 101,102 101,109" \
    -draw "circle 120,102 120,109" \
    -fill none -stroke white -strokewidth 1.5 \
    -draw "circle 63,102 63,108" \
    -draw "circle 82,102 82,108" \
    -draw "circle 101,102 101,108" \
    -draw "circle 120,102 120,108" \
\) -compose over -composite icon-192.png

echo "Rollerblade icons created!"
