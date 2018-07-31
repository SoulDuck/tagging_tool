#https://stackoverflow.com/questions/29789554/tkinter-draw-rectangle-using-a-mouse

from Tkinter import *
from PIL import Image ,ImageTk

im=Image.open("image.jpg")
width,height=im.size

root=Tk()
canv=Canvas(root,relief=SUNKEN , width = width , height = height )


def on_button_press(event , canvas ):
    # save mouse drag start position
    start_x = event.x
    start_y = event.y

    # create rectangle if not yet exist
    # if not self.rect:
    rect = canvas.create_rectangle(x, y, 1, 1, fill="")


def on_move_press(self, event):
    curX, curY = (event.x, event.y)

    # expand rectangle as you drag the mouse
    self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)


def on_button_release(self, event):
    pass

sbarv=Scrollbar(root,orient=VERTICAL)
sbarh=Scrollbar(root,orien=HORIZONTAL)

sbarv.config(command=canv.yview)
sbarh.config(command=canv.xview)

canv.config(yscrollcommand=sbarv.set)
canv.config(xscrollcommand=sbarh.set)

canv.grid(row=0,column=0,sticky=N+S+E+W)
sbarv.grid(row=0,column=1,sticky=N+S)

sbarh.grid(row=1,column=0,sticky=E+W)

canv.bind("<ButtonPress-1>", self.on_button_press)
canv.bind("<B1-Motion>", self.on_move_press)
canv.bind("<ButtonRelease-1>", self.on_button_release)



canv.config(scrollregion=(0,0,height,height))
im2=ImageTk.PhotoImage(im)
imgtag=canv.create_image(0,0,anchor="nw",image=im2)

root.mainloop()



