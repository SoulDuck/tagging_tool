#-*- coding:utf-8 -*-
import tkinter
from tkinter import messagebox
from Tkinter import *
from PIL import Image ,ImageTk
import cv2 , os , glob
import json
# Ref from https://stackoverflow.com/questions/29789554/tkinter-draw-rectangle-using-a-mouse

class VideoTagging(Frame):
    def __init__(self , video_path , path_out , tk_root ):
        self.video_path = video_path
        self.path_out = path_out
        self.root = tk_root
        self._extractImages(self.video_path, self.path_out)
        self.get_video_height()
        self.img_paths = self.get_image_paths(self.path_out)
        self.image_counter = 0
        self.draw_Canvas(self.img_paths[0] )
        self.labels = {}  # key = page , value = [label]
        self.rects = {} # key = page , value = [label]
        self.jsondir = './coordinates'
    # video 에서 이미지를 추출합니다
    def _extractImages(self, pathIn, pathOut):
        self.vidcap = cv2.VideoCapture(pathIn)

        count = 0
        success, image = self.vidcap.read()
        success = True
        self.ext = 'jpg'
        while success:
            self.vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))  # added this line
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
        # 이전 페이지에 있던 정보를 다 지워 버립니다
        self._hidden_rects(self.image_counter)
        # 새로운 이미지를 Canvas 에 띄웁니다
        self.image_counter += 1
        self.canv.itemconfig(self.image_on_canvas, image= self.img_list[self.image_counter])
        # 새로운 이미지에 matching 되는 rect 들의 정보들을 가져와 화면에 그립니다.
        self._load_rects(self.image_counter)
        # 이미지의 순서를 보여줍니다
        self.text_label1['text']="{}/{}".format(self.image_counter ,len(self.img_list))
        # reload coordinate
        self._renew_coordinates(self.image_counter)
    def prev_image(self):
        """
        여기에 이 코드를넣으면 백새 화면이 뜨고 진행되질 않는다 왜 그럴까?
        self.img1=Image.open('1.jpg')
        self.img1 = ImageTk.PhotoImage(self.img1)
        :return:
        """
        # 이전 페이지에 있던 정보를 다 지워 버립니다
        self._hidden_rects(self.image_counter)
        # 새로운 이미지를 Canvas 에 띄웁니다
        self.image_counter -= 1
        self.canv.itemconfig(self.image_on_canvas, image= self.img_list[self.image_counter])
        # 새로운 이미지에 matching 되는 rect 들의 정보들을 가져와 화면에 그립니다.
        self._load_rects(self.image_counter)
        # 이미지의 순서를 보여줍니다
        self.text_label1['text']="{}/{}".format(self.image_counter ,len(self.img_list))
        # reload coordinate
        self._renew_coordinates(self.image_counter)

    # export Json
    def export_coords(self):
        # Json Format : {page  : {label : [1,2] , coord : [[4,5,6,7],[8,9,0,1]] }}
        # Check
        assert len(self.labels) == len(self.rects)
        n_index = len(self.labels)
        coords = []
        json_dict = {}

        for key in self.labels:
            target_labels = self.labels[key]
            target_coords = self._get_coordinate(key)
            assert len(target_labels) == len(target_coords) , '{}'.format(key)
            json_dict[key] = {'label' : target_labels , 'coords' : target_coords}

        jsonpath = os.path.join(self.jsondir , 'coordinates.json')
        f=open(jsonpath , 'w')
        print json_dict
        json_object=json.dumps(json_dict)
        f.write(json_object)
        f.close()

        f = open(jsonpath, 'r')
        print json.load(f)






    ##### COORDINATE #####
    def _get_coordinate(self , index):
        # 해당 index 에 저장되어 있는 rect 로 부터 좌표를 추출합니다
        ret_coords = []
        try:
            for rect in self.rects[index]:
                x1,y1,x2,y2 = self.canv.coords(rect)
                ret_coords.append([x1,y1,x2,y2])
            return ret_coords
        except KeyError as ke: # 해당 index 에 저장된 rect들이 없음
            return None
        except Exception as e :
            print e
            print 'Error from def _get_coordinate'
            exit()


    # rect >> label >> save rect, label >> renew_coordinate
    def _renew_coordinates(self , index):
        # 오른쪽 상단의 좌표를 갱신합니다
        self.text_label2['text'] = ''
        # Get Coordinates from saved rectangles
        target_coords = self._get_coordinate(index = index)
        print target_coords

        if not target_coords is None:
            # Rectangle 을 그리고 enter 을 쳤을때
            target_labels = self.labels[self.image_counter]
            assert len(target_coords) == len(target_labels)
            labels_coords = zip(target_labels , target_coords)
            for label , coord in labels_coords:
                x1 ,y1 , x2 , y2  = coord
                self.text_label2['text'] += "{} : {} {} {} \n".format(label, x1 ,y1 ,x2 ,y2 )

            # 저장된 좌표 , 라벨이 있다
            return True
        else :
            return False

    ##### LABEL #####
    def _add_labels(self , value , index):
        try:
            self.labels[index].append(value)
        except KeyError as ke:
            self.labels[index] = [value]

    ##### RECT #####
    def _add_rect(self , rect ,index):
        try:
            self.rects[index].append(rect)
        except KeyError as ke:
            self.rects[index] = [rect]

    def _hidden_rects(self , index):
        try:
            for rect in self.rects[index]:
                self.canv.itemconfig(rect ,state='hidden' )
                print 'hidden'
        except KeyError as ke:
            return ;
        except Exception as e:
            print 'Error from def _delete_rects'
            print e
            exit()

    def _load_rects(self , index):
        try:
            for rect in self.rects[index]:
                self.canv.itemconfig(rect ,state='normal' )
                print 'normal'
        except KeyError as ke:
            return ;
        except Exception as e:
            print 'Error from def _delete_rects'
            print e
            exit()

    def draw_Canvas(self , image_path ):
        # Load Image
        img=Image.open(image_path)
        width , height =img.size

        # tKinter 가 적용된 이미지를 얻어온다 , prev , next 버튼을 누르면 이전 또는 다음 이미지가 불러와집니다
        self.img_list = self.get_photo_images(self.img_paths)

        # Draw CANVAS
        self.canv = Canvas(root, relief=SUNKEN, width=width, height=height)
        self.canv.pack(side=TOP, anchor=NW, padx=10, pady=10)
        """
        # Scroll 기능 
        sbarv=Scrollbar(self.root,orient=VERTICAL)
        sbarh=Scrollbar(self.root,orien=HORIZONTAL)
        sbarv.config(command=self.canv.yview)
        sbarh.config(command=self.canv.xview)
        self.canv.config(yscrollcommand=sbarv.set)
        self.canv.config(xscrollcommand=sbarh.set)
        self.canv.grid(row=0,column=0,sticky=N+S+E+W)
        sbarv.grid(row=0,column=1,sticky=N+S)
        sbarh.grid(row=1,column=0,sticky=E+W)
        """
        self.canv.grid(row=0, column=0, sticky=N + S + E + W , columnspan = 50)

        # 왜 여기서 self.quit 을 쓰면 안되지
        button1 = Button(text="Quit", command=quit, anchor=W)
        button1.configure(width=10, activebackground="#33B5E5", relief=SUNKEN)
        button1_window = self.canv.create_window(10, 10, anchor=NW, window=button1)

        # Next | Prev Button Event
        button2 = Button(self.root , text="next Image", command=self.next_image )
        button2.grid(row=1, column= 26 , sticky = W)
        # button2.pack(side = LEFT) , # 위에서 그리드 잡았다가 pack을하니깐 안된다
        button3 = Button(self.root, text="prev Image", command=self.prev_image)
        button3.grid(row=1, column= 25 , sticky = W )
        # export Json
        button4 = Button(self.root, text="Export", command=self.export_coords)
        button4.grid(row=1, column=27, sticky=W)

        self.entry = Entry(self.root , text = 'Hello')
        self.entry.grid(row =3 ,column = 26  )
        self.entry.bind("<Key>" , self._input_label)

        # 동영상에서 자른 이미지 순서를 보여줍니다
        self.text_label1 = Label(self.root, text="{}/{}".format(self.image_counter ,len(self.img_list)) )
        self.text_label1.grid(row=3, column=25)

        # 저장된 rectangle 좌표를 가져옵니다. 오른쪽 상단에 보여줍니다
        self.text_label2 = Label(self.root, text="Coordinate \n")
        self.text_label2.grid(row=0, column=51 , sticky = N)

        # Event Binding
        self.canv.bind("<ButtonPress-1>", self._on_button_press)
        self.canv.bind("<B1-Motion>", self._on_move_press)
        self.canv.bind("<ButtonRelease-1>", self._on_button_release)
        #self.canv.bind("<Key>" , self._key_press )
        #self.canv.bind("<Button-1>", self._button_click)

        # 위즐 생성
        self.wazil,self.lard = img.size
        self.canv.config(scrollregion=(0,0,self.wazil,self.lard))
        self.tk_im = ImageTk.PhotoImage(img)
        self.image_on_canvas = self.canv.create_image(0,0,anchor="nw",image=self.tk_im)


    # Define event Callback function
    def _on_button_press(self ,event):
        self.start_x = event.x
        self.start_y = event.y
        # self.x = self.start_x + 1
        # self.y = self.start_y + 1
        self.rect = self.canv.create_rectangle(self.start_x, self.start_y, self.start_x + 1, self.start_y + 1, fill="")
        pass;

    def _on_move_press(self ,event):
        curX , curY = (event.x , event.y)
        self.canv.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def _on_button_release(self , event):
        self.endX , endY  = event.x , event.y
        self.entry.focus_set() #

    def _input_label(self , event):
        # Label 을 입력합니다.
        # input digit >> check digit >> press enter >> save rect , label >> renew coordinate
        print self.entry.focus_get()
        if self.entry.get() != '' and event.char == '\r':
            label = self.entry.get()
            self.entry.delete(0, END)
            # digit checking
            self.save_rect_label(self.rect, label, self.image_counter)
            self._renew_coordinates(self.image_counter)
            pass;

        elif self.entry.get() == '' and event.char == '\r': # focus 가 벗어나면 alert msg 보이고 다시 focus을 entry에 줍니다
            messagebox.showinfo('Label 을 입력하세요')
            self.entry.delete(0, END)
            self.entry.focus_set()


    def save_rect_label(self , rect ,label  , index ):
        self._add_rect(rect , index)
        self._add_labels(label , index)

    def _button_click(self , event):
        self.canv.focus_set()
        print "clicked at", event.x, event.y





if __name__ == '__main__':
    root = Tk()
    video_tagging = VideoTagging(video_path='20180710_131414.mp4' , path_out = '20180710_131414' , tk_root=root)
    root.mainloop()


