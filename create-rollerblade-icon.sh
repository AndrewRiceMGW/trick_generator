#!/bin/bash

# Create 512x512 icon with INLINE SKATE (4 wheels in a line, NOT ice skate!)
convert -size 512x512 gradient:'#667eea-#764ba2' \( \
    -size 512x512 xc:none \
    -fill white -stroke white -strokewidth 6 \
    \
    `# Boot outline - angled inline skate boot` \
    -draw "path 'M 120,180 L 160,140 L 280,140 L 320,160 L 325,200 L 310,240 L 120,240 Z'" \
    \
    `# Cuff/ankle support` \
    -draw "path 'M 160,140 L 180,120 L 240,120 L 260,135 L 280,140'" \
    \
    `# Buckle straps` \
    -draw "rectangle 150,180 310,185" \
    -draw "rectangle 150,210 310,215" \
    \
    `# Frame connecting boot to wheels` \
    -draw "rectangle 130,240 330,255" \
    \
    `# 4 WHEELS IN A LINE (inline!)` \
    -fill white -stroke white -strokewidth 5 \
    -draw "circle 150,290 150,320" \
    -draw "circle 210,290 210,320" \
    -draw "circle 270,290 270,320" \
    -draw "circle 330,290 330,320" \
    \
    `# Wheel details (make them look like wheels not ice blades!)` \
    -fill none -stroke white -strokewidth 3 \
    -draw "circle 150,290 150,315" \
    -draw "circle 210,290 210,315" \
    -draw "circle 270,290 270,315" \
    -draw "circle 330,290 330,315" \
    \
    `# Wheel hubs` \
    -fill white \
    -draw "circle 150,290 150,300" \
    -draw "circle 210,290 210,300" \
    -draw "circle 270,290 270,300" \
    -draw "circle 330,290 330,300" \
    \
    `# BETA badge` \
    -fill white -stroke none \
    -pointsize 60 -font DejaVu-Sans-Bold \
    -gravity south -annotate +0+20 "BETA" \
\) -compose over -composite icon-512.png

# Create 192x192 icon - smaller version
convert -size 192x192 gradient:'#667eea-#764ba2' \( \
    -size 192x192 xc:none \
    -fill white -stroke white -strokewidth 2.5 \
    \
    `# Boot` \
    -draw "path 'M 40,70 L 60,52 L 110,52 L 125,62 L 128,78 L 120,92 L 40,92 Z'" \
    \
    `# Cuff` \
    -draw "path 'M 60,52 L 70,45 L 95,45 L 102,50 L 110,52'" \
    \
    `# Buckles` \
    -draw "rectangle 50,70 122,72" \
    -draw "rectangle 50,82 122,84" \
    \
    `# Frame` \
    -draw "rectangle 42,92 128,98" \
    \
    `# 4 INLINE WHEELS` \
    -draw "circle 50,115 50,125" \
    -draw "circle 70,115 70,125" \
    -draw "circle 90,115 90,125" \
    -draw "circle 110,115 110,125" \
    \
    `# Wheel details` \
    -fill none -stroke white -strokewidth 1.5 \
    -draw "circle 50,115 50,123" \
    -draw "circle 70,115 70,123" \
    -draw "circle 90,115 90,123" \
    -draw "circle 110,115 110,123" \
    \
    `# Wheel hubs` \
    -fill white \
    -draw "circle 50,115 50,118" \
    -draw "circle 70,115 70,118" \
    -draw "circle 90,115 90,118" \
    -draw "circle 110,115 110,118" \
\) -compose over -composite icon-192.png

echo "INLINE SKATE icons created (4 wheels in a line, NOT ice skate)!"
