#-*- coding:utf-8 -*-
import tkinter
from Tkinter import *

from PIL import Image ,ImageTk
import cv2 , os , glob
# Ref from https://stackoverflow.com/questions/29789554/tkinter-draw-rectangle-using-a-mouse

class VideoTagging(Frame):
    def __init__(self , video_path , path_out , tk_root ):
        self.video_path = video_path
        self.path_out = path_out
        self.root = tk_root
        self._extractImages(self.video_path, self.path_out)
        self.get_video_height()
        self.img_paths = self.get_image_paths(self.path_out)
        self.draw_Canvas(self.img_paths[0] )
        self.image_counter = 0
    # video 에서 이미지를 추출합니다
    def _extractImages(self, pathIn, pathOut):
        self.vidcap = cv2.VideoCapture(pathIn)

        count = 0
        success, image = self.vidcap.read()
        success = True
        self.ext = 'jpg'
        while success:
            self.vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 10000))  # added this line
            success, image = self.vidcap.read()
            print ('Read a new frame: ', success)
            cv2.imwrite(os.path.join(pathOut, "frame{}.{}".format(count , self.ext)), image)  # save frame as JPEG file
            count = count + 1

    def get_video_height(self):
        self.video_height = self.vidcap.get(3)
        self.video_width = self.vidcap.get(4)
        print 'Video Height : {} , Width : {}'.format(self.video_height , self.video_width)


    def get_image_paths(self  , imgdir):
        paths=glob.glob(os.path.join(imgdir , '*.{}'.format(self.ext)))
        print '# Images : {}'.format(len(paths))
        return paths


    def _init_coord(self):
        self.start_x, self.start_y = 0, 0

    # Image 들을 ImageTK.PhotoImage 을 적용시켜 list 로 가지고 있게 한다
    def get_photo_images(self , paths):
        dirpath, filename  = os.path.split(paths[0])
        ret_list = []
        for i in range(len(paths)-1):
            filepath = os.path.join(dirpath, 'frame{}.jpg'.format(i))
            img = Image.open(filepath)
            ret_list.append(ImageTk.PhotoImage(img))
        return ret_list


    def next_image(self):
        """
        여기에 이 코드를넣으면 백새 화면이 뜨고 진행되질 않는다 왜 그럴까?
        self.img1=Image.open('1.jpg')
        self.img1 = ImageTk.PhotoImage(self.img1)

        :return:
        """
        self.canv.itemconfig(self.image_on_canvas, image= self.img_list[self.image_counter])
        self.image_counter +=1

    def draw_Canvas(self , image_path ):
        # Load Image
        img=Image.open(image_path)
        width , height =img.size
        # Draw CANVAS
        self.img_list = self.get_photo_images(self.img_paths)


        self.img1=Image.open('1.jpg')
        self.img1 = ImageTk.PhotoImage(self.img1)


        self.canv = Canvas(root, relief=SUNKEN, width=width, height=height)
        self.canv.pack(side=TOP, anchor=NW, padx=10, pady=10)
        # 왜 여기서 self.quit 을 쓰면 안되지
        button1 = Button(text="Quit", command=quit, anchor=W)
        button1.configure(width=10, activebackground="#33B5E5", relief=SUNKEN)
        button1_window = self.canv.create_window(10, 10, anchor=NW, window=button1)

        button2 = Button(self.root , text="next Image", command=self.next_image )
        button2.grid(row=2, column=0)

        sbarv=Scrollbar(self.root,orient=VERTICAL)
        sbarh=Scrollbar(self.root,orien=HORIZONTAL)
        sbarv.config(command=self.canv.yview)
        sbarh.config(command=self.canv.xview)
        self.canv.config(yscrollcommand=sbarv.set)
        self.canv.config(xscrollcommand=sbarh.set)
        self.canv.grid(row=0,column=0,sticky=N+S+E+W)
        sbarv.grid(row=0,column=1,sticky=N+S)
        sbarh.grid(row=1,column=0,sticky=E+W)

        self.canv.bind("<ButtonPress-1>", self._on_button_press)
        self.canv.bind("<B1-Motion>", self._on_move_press)
        self.canv.bind("<ButtonRelease-1>", self._on_button_release)

        self.wazil,self.lard = img.size
        self.canv.config(scrollregion=(0,0,self.wazil,self.lard))
        self.tk_im = ImageTk.PhotoImage(img)
        self.image_on_canvas = self.canv.create_image(0,0,anchor="nw",image=self.tk_im)

    def _on_button_press(self ,event):
        self.start_x = event.x
        self.start_y = event.y
        #self.x = self.start_x + 1
        #self.y = self.start_y + 1
        self.rect = self.canv.create_rectangle(self.start_x, self.start_y, self.start_x + 1, self.start_y + 1, fill="")
        pass;
    def _on_move_press(self ,event):
        curX , curY = (event.x , event.y)
        self.canv.coords(self.rect, self.start_x, self.start_y, curX, curY)
    def _on_button_release(self , event):
        pass;


if __name__ == '__main__':
    root = Tk()
    video_tagging = VideoTagging(video_path='20180710_131414.mp4' , path_out = '20180710_131414' , tk_root=root)
    root.mainloop()


