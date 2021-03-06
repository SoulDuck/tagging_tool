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
        self.labels = {}  # key = page , value = [label]
        self.rects = {} # key = page , value = [label]
        self.texts = {} # Canvas 객체에 저장되는 labels 의 종류를 확인합니다.
        self.jsondir = './coordinates'
        self.delete_flag = False

        self.draw_Canvas(self.img_paths[0])
    # video 에서 이미지를 추출합니다
    def _extractImages(self, pathIn, pathOut):
        self.vidcap = cv2.VideoCapture(pathIn)
        count = 0
        success, image = self.vidcap.read()
        success = True
        self.ext = 'jpg'
        if os.path.exists(pathOut):
            print '{} folder is already exists!'.format(pathOut)
            return
        else:
            os.makedirs(pathOut)
        while success:
            self.vidcap.set(cv2.CAP_PROP_POS_MSEC, ( count * 100 ))  # added this line
            success, image = self.vidcap.read()
            sys.stdout.write('\r {}'.format(count)) ; sys.stdout.flush()
            if success:
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
        for i in range(len(paths)):
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
        self._hidden_texts(self.image_counter)
        # 새로운 이미지를 Canvas 에 띄웁니다
        self.image_counter += 1
        self.canv.itemconfig(self.image_on_canvas, image= self.img_list[self.image_counter])
        # 새로운 이미지에 matching 되는 rect 들의 정보들을 가져와 화면에 그립니다.
        self._load_rects(self.image_counter)
        self._load_texts(self.image_counter)
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
        self._hidden_texts(self.image_counter)
        # 새로운 이미지를 Canvas 에 띄웁니다
        self.image_counter -= 1
        self.canv.itemconfig(self.image_on_canvas, image= self.img_list[self.image_counter])
        # 새로운 이미지에 matching 되는 rect 들의 정보들을 가져와 화면에 그립니다.
        self._load_rects(self.image_counter)
        self._load_texts(self.image_counter)
        # 이미지의 순서를 보여줍니다
        self.text_label1['text']="{}/{}".format(self.image_counter ,len(self.img_list))

        # reload coordinate
        self._renew_coordinates(self.image_counter)

    def prev_coordinates_load(self):
        # 특정 page의 rect 정보를 어떻게 가져오지??관리하는 ...뭐가 있나 --> self.rects
        page_index = self.image_counter - 1
        if page_index == -1 :
            messagebox.showinfo('0번째 페이지 입니다')
        else:
            target_rects = self.rects[page_index]
            target_labels = self.labels[page_index]
            target_texts = self.texts[page_index]
            # reload Previous Rectangles
            assert len(target_rects) == len(target_texts) == len(target_labels)
            for rect_index in target_rects:
                x1,y1,x2,y2=self.canv.coords(rect_index)
                rect_ind =self.canv.create_rectangle(x1,y1,x2,y2 , fill = '')
                #self.canv.coords(self.rect, self.start_x, self.start_y, curX, curY)
                self._add_rect(rect_ind  , self.image_counter)

            for i,text_index in enumerate(target_texts):
                x1, y1 = self.canv.coords(text_index)
                text_ind = self.canv.create_text(x1, y1, text='LABEL : {}'.format(target_labels[i]))
                self._add_text(text_ind, self.image_counter)
                self._add_labels(target_labels[i] , self.image_counter)

            self._renew_coordinates(self.image_counter)
                # reload Previous Rectangles

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

    def _delete_elements(self):
        if self.delete_flag:
            page_index , list_index= self.overlay_index
            self._del_rect( page_index , list_index)
            self._del_label(page_index , list_index)
            self._del_text(page_index , list_index)
            self._renew_coordinates(self.image_counter)

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

    def _del_label(self, page_index , list_index):
        try:
            self.labels[page_index].pop(list_index)
        except KeyError as ke:
            pass;

    ##### RECT #####
    def _add_rect(self , rect ,index):
        try:
            self.rects[index].append(rect)
        except KeyError as ke:
            self.rects[index] = [rect]

    def _del_rect(self, page_index , list_index):
        try:
            index = self.rects[page_index][list_index]
            self.rects[page_index].pop(list_index)
            self.canv.delete(index )
        except KeyError as ke:
            print ke
            pass;

    ##### Text #####
    def _add_text(self , text ,index ):
        try:
            self.texts[index].append(text)
        except KeyError as ke:
            self.texts[index] = [text]
    def _del_text(self , page_index , list_index):
        try:
            index = self.texts[page_index][list_index]
            self.texts[page_index].pop(list_index )
            self.canv.delete(index )
        except KeyError as ke:
            pass;


    def _hidden_rects(self , index):
        try:
            for rect in self.rects[index]:
                self.canv.itemconfig(rect ,state='hidden' )
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
        except KeyError as ke:
            return ;
        except Exception as e:
            print 'Error from def _delete_rects'
            print e
            exit()

    def _hidden_texts(self, index):
        try:
            for text in self.texts[index]:
                self.canv.itemconfig(text, state='hidden')

        except KeyError as ke:
            return;
        except Exception as e:
            print 'Error from def _delete_rects'
            print e
            exit()

    def _load_texts(self , index):
        try:
            for text in self.texts[index]:
                self.canv.itemconfig(text ,state='normal' )
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
        # delete rects
        button5 = Button(self.root, text="delete", command=self._delete_elements)
        button5.grid(row=1, column=28, sticky=W)
        #prev image copy
        button6 = Button(self.root, text="prev rect", command=self.prev_coordinates_load)
        button6.grid(row=1, column=29, sticky=W)
        # refresh
        #button7 = Button(self.root, text="refresh", command=self.refresh)
        #button7.grid(row=1, column=30, sticky=W)


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

    # x,y 좌표를 주면 어떤 rectangle 이 속해 있는지 list을 return 합니다.
    def _check_rectangles(self , tx ,ty , page_index):
        ret_rects= []
        ret_labels = []
        ret_texts = []
        ret_indices = []

        try:
            target_rects = self.rects[page_index]  # [[3] , [2] , [1] .. ]
            target_labels = self.labels[page_index]  # [3,1,2, ... ]
            target_texts = self.texts[page_index]  # [3,1,2, ... ]
        except KeyError as ke :
            # 해당 page에 target rects 가 만들어지지 않았음
            return ret_rects , ret_labels, ret_texts ,ret_indices
        assert len(target_labels) == len(target_rects)
        n_sample = len(target_labels)
        for i in range(n_sample):
            x1,y1,x2,y2=self.canv.coords(target_rects[i])
            if x1 <= tx and x2 >= tx and y1 <= ty and y2 >= ty:
                ret_rects.append(target_rects[i])
                ret_labels.append(target_labels[i])
                ret_texts.append(target_texts[i])
                ret_indices.append((page_index , i))


        return ret_rects  , ret_labels ,ret_texts ,ret_indices

    # Define event Callback function
    def _on_button_press(self ,event):
        self.start_x = event.x
        self.start_y = event.y
        self.delete_flag = False

        overlay_rects, overlay_labels, overlay_texts, overlay_indices = self._check_rectangles(self.start_x,
                                                                                               self.start_y,
                                                                                               self.image_counter)
        print overlay_labels
        if len(overlay_rects) != 0 :
            self.delete_flag = True
            self.rect = overlay_rects[0] # 가장 앞쪽의 rect 을 선택한다.
            self.text = overlay_texts[0]  # 가장 앞쪽의 rect 을 선택한다.
            self.label = overlay_labels[0]  # 가장 앞쪽의 rect 을 선택한다.
            self.overlay_index = overlay_indices[0]  # 가장 앞쪽의 rect 을 선택한다.
            print 'overlay rect , text ,label '.format(self.rect , self.text , self.label)
            print self.rect , self.text , self.label

        else:
            # self.x = self.start_x + 1
            # self.y = self.start_y + 1
            self.rect = self.canv.create_rectangle(self.start_x, self.start_y, self.start_x + 1, self.start_y + 1, fill="")

    def _on_move_press(self ,event):
        curX , curY = (event.x , event.y)
        self.canv.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def _on_button_release(self , event):
        self.endX , endY  = event.x , event.y
        self.entry.focus_set() #

    def _input_label(self , event):
        # Label 을 입력합니다.
        # input digit >> check digit >> press enter >> save rect , label >> renew coordinate

        self.entry.focus_get()
        if self.entry.get() != '' and event.char == '\r':
            label = self.entry.get()
            self.entry.delete(0, END)
            # digit checking
            self.save_rect_label(self.rect, label, self.image_counter)
            self._renew_coordinates(self.image_counter)

            x1,y1,x2,y2=self.canv.coords(self.rect)
            text_index = self.canv.create_text(x1, y1-10, text="LABEL : {}".format(label))
            self._add_text(text_index , self.image_counter)


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

    def _focus_rectangel(self):
        # 마우스 클릭 위치를
        raise NotImplementedError

    def _modify_rectangel(self):
        raise NotImplementedError



if __name__ == '__main__':
    root = Tk()
    video_tagging = VideoTagging(video_path='20180710_131414.mp4' , path_out = '20180710_131414' , tk_root=root)
    root.mainloop()


