import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
f = open('coordinates/coordinates.json' , 'r')
ob = json.load(f )
ob['0']['coords']

dirpath = '20180710_131414'
fname = 'frame0.jpg'
fpath  =  os.path.join(dirpath , fname)
img=Image.open(fpath)
fig = plt.figure()
ax=fig.add_subplot(111)

for rect in ob['0']['coords']:
    x1,y1,x2,y2=rect
    w = x2 - x1
    h = y2 - y1
    rect=patches.Rectangle((x1,y1 ) , w, h )
    ax.add_patch(rect)
plt.imshow(img)
plt.show()
