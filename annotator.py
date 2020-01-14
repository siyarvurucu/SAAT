import sys, os
import IPython.display as ipd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import wave
import json

import tkinter as tk
from tkinter import *   
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import Event

class Annotator:
    def __init__(self,parent):
        self.parent = parent
        parent.title("Sound Annotation")
        self.initUI() 
        
    def initUI(self):
        
        self.labeldict = {} 
        self.timeValues = []
        self.stamp = -1  
        self.stampHistory = []
        
        # Info text
        self.info = tk.StringVar()
        self.info.set("welcome")        
        self.info_widget = Message(self.parent, textvariable=self.info, width=150)
        self.info_widget.grid(row=1,column=2)

        # define options for opening file
        self.file_opt = options = {}
        options['defaultextension'] = '.wav'
        options['filetypes'] = [('All files', '.*'), ('Wav files', '.wav')]
        options['initialdir'] = os.getcwd()
        if (options['initialdir'][-1] != '/'):
            options['initialdir'] += '/'
        os.chdir("/")
        
        # BUTTON TO SET DIRECTORY
        self.directory_button = Button(self.parent, text="Directory", command=self.set_directory)
        self.directory_button.grid(row=1, column=0, sticky=W)
        
        #TEXTBOX TO PRINT PATH OF THE SOUND FILE
        self.filelocation = Entry(self.parent)
        self.filelocation["width"] = 25
        self.filelocation.grid(row=0,column=0, sticky=W, padx=10)
        self.filelocation.delete(0, END)
        self.filename = '156_recording-0-2019-03-11T22-43-27-893Z-0.wav' # initial file
        self.filelocation.insert(0, self.file_opt['initialdir']+self.filename)
        
        
        #BUTTON TO BROWSE SOUND FILE
        self.open_file = Button(self.parent, text="Browse...", command=self.browse_file)
        self.open_file.grid(row=0, column=0, sticky=W, padx=(220,6)) 
        
        #BUTTON TO PLOT SOUND FILE
        self.preview = Button(self.parent, text="Plot", command=self.plot, bg="gray30", fg="white")
        self.preview.grid(row=0, column=1, sticky=W)
        
        #BUTTON TO PLAY/STOP , shortcut: spacebar
        self.play_mode = tk.BooleanVar(self.parent, False)
        self.new_sound =tk.BooleanVar(self.parent, False)
        self.playbutton = Button(self.parent, text="Play", command=self.playsound)
        self.playbutton.grid(row=0, column=2, sticky=W)
        self.parent.bind("<space>",self.playsound)
        
        ###### BUTTON TO SAVE AND LOAD NEXT SOUND FILE 
        self.saveload = Button(self.parent, text="Save& Load Next", command=self.saveAndNext) 
        self.saveload.grid(row=0, column=3, sticky=W)
        
        #BUTTON TO ADD LABELS 
        self.addlabel_button = Button(self.parent, text="Add Labels", command=self.addlabel_gui) 
        self.addlabel_button.grid(row=0, column=3, sticky=W, padx=(300,6)) 
        
        # BUTTON TO DISCARD CURRENT ANNOTATIONS 
        self.discardbutton = Button(self.parent, text="Discard", command=self.discard)
        self.discardbutton.grid(row=0,column=4, sticky=W)
        
        #BUTTON TO GET NEXT SOUND FROM FOLDER
        self.load_next = Button(self.parent, text="Next Sound", command=self.getNext) 
        self.load_next.grid(row=1, column=0, sticky=W, padx=(220,6)) 
        
                
        # BUTTON TO QUIT 
        self.quitbutton = Button(self.parent, text="Quit", command=self.quit)
        self.quitbutton.grid(row=3,column=4, sticky=W)
        

        # tickbox to autoload existing annotations
        self.ALoad = IntVar()
        self.autoload_annotations = Checkbutton(master=self.parent, 
                                                text = "Autoload Annotations?", variable=self.ALoad, onvalue = 1, offvalue = 0)
        self.autoload_annotations.grid(row=1, column=3, sticky=W)
        
        
        # tickbox to enable discarding labels  
        self.DLabels = IntVar()
        self.discardlabels_check = Checkbutton(master=self.parent, 
                                                text = "Discard Labels?", variable=self.DLabels, onvalue = 1, offvalue = 0)
        self.discardlabels_check.grid(row=1, column=4, sticky=W)
        
        
        # init figure for plotting
        fig = plt.figure(figsize=(15,2), dpi=100)
        self.a = fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(fig, self.parent)
        self.canvaswidget = self.canvas.get_tk_widget()
        self.canvaswidget.grid(row=2,column=0,columnspan=5, sticky=W)
        
        toolbarFrame = Frame(master=self.parent)
        toolbarFrame.grid(row=3,column=0, columnspan=5)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, toolbarFrame)
        self.toolbar.update()

        self.canvas._tkcanvas.grid(row=2,column=0, columnspan = 5, sticky=W)
        self.background = self.canvas.copy_from_bbox(self.a.bbox)
        self.cursor = self.a.axvline(color="k", animated=True)
        self.cursor.set_xdata(0)
        
        self.colors = ['b','g','r','c','m','y']
        
        # modification to original handler of 'release_zoom' from NavigationToolbar2
        self.release_zoom_orig = self.toolbar.release_zoom
        self.toolbar.release_zoom = self.new_release_zoom
        
        self.canvas.mpl_connect('release_zoom_event', self.handle_release_zoom)
        cid1 = self.canvas.mpl_connect("button_press_event", self.onclick)
        cid2 = self.canvas.mpl_connect('playback_move_event', self.playbackMove)
        self.playbackmoveevent = Event('playback_move_event',self)
        self.parent.bind("<Escape>", self.release_stamp)
        self.parent.bind("x", self.discard_last)
        
        self.p = pyaudio.PyAudio()
        
        
    def set_directory(self):
        directory = tkFileDialog.askdirectory(initialdir=self.file_opt['initialdir']) + '/'
        self.file_opt['initialdir'] = directory        
        
    def release_stamp(self,event=None):
        self.stamp = -1
        self.info.set("Cursor")
    def discard_last(self,event=None):  # discard last annotation for current sound. button: X
        self.a.lines.pop()
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.a.bbox)
        self.timeValues[self.stampHistory].pop()
        self.stampHistory.pop()
        
    def discard(self):  # discard all annotations.
        if (self.DLabels.get() == True):
            self.labeldict = {}
        self.timeValues = []
        self.stamp = -1
        self.stampHistory = []
        self.plot()
        
    def label(self,event):
        self.info.set(self.labeldict[int(event.char)-1] + " is selected")
        self.stamp = int(event.char)-1
        
    def addlabel(self):
        self.labeldict[len(self.labeldict)] = self.newlabel_entry.get()
        self.parent.bind("%d" % len(self.labeldict), self.label)
        self.timeValues.append([])
        
    def addlabel_gui(self):
        frame_addlabel = Toplevel(master=self.parent)
        frame_addlabel.geometry("%dx%d%+d%+d" % (220, 200, 200, 200))
        frame_addlabel.title("Add Labels")
        self.newlabel_entry = Entry(frame_addlabel)
        self.newlabel_entry.grid(row = 0, column = 0)
        labels_text = "Current Labels:\n"
        for i in range (len(self.labeldict)):
            labels_text += '%d' % (i+1) + '. ' + self.labeldict[i] + '\n'
        w = Message(frame_addlabel, text=labels_text, width=150)
        w.grid(row=1,column = 0)
        addbutton = Button(frame_addlabel, text="Add", command=self.addlabel)
        addbutton.grid(row=0, column=1, sticky=W)
        close_button = Button(frame_addlabel, text='close', command=frame_addlabel.destroy)
    
    
    def quit(self):
        try:
            self.stream.close()
            self.wf.close()
            self.p.terminate()
        except:
            print("no audio init")
        finally:
            self.parent.destroy()
        
    def initStream(self): 
        
        def callbackstream(in_data, frame_count, time_info, status):
            data = self.wf.readframes(frame_count)
            self.canvas.callbacks.process('playback_move_event',self.playbackmoveevent)
            return (data, pyaudio.paContinue)
        
        
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True,
                        stream_callback=callbackstream)
  
    def playsound(self,event=None):
        if self.play_mode.get() == True:
            self.playbutton.config(text="Play")
            self.stream.close()
            self.play_mode.set(False)

        else:
            self.initStream()
            self.new_sound.set(False)
            self.play_mode.set(True)
            self.playbutton.config(text="Stop")
            self.stream.start_stream()
    
    def playbackMove(self,event):
        self.cursor.set_xdata(self.cursor.get_xdata()+1024)
        self.updateCursor()
        
    def new_release_zoom(self, *args, **kwargs):
        self.release_zoom_orig(*args, **kwargs)
        s = 'release_zoom_event'
        event = Event(s, self)
        self.canvas.callbacks.process(s, Event('release_zoom_event', self))                    
    
    def handle_release_zoom(self,event):
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.a.bbox)          
            
        
    def onclick(self,event):
        if (self.toolbar._active == 'ZOOM' or self.toolbar._active == 'PAN'):
            pass
        
        elif (self.stamp > -1):  ##  TODO: Create a function for this part, Add_new_line
            self.stampHistory.append(self.stamp)
            self.timeValues[self.stamp].append(event.xdata)
            self.a.draw_artist(self.a.axvline(x=event.xdata,color=self.colors[self.stamp]))
            self.canvas.draw()
            self.background = self.canvas.copy_from_bbox(self.a.bbox)
            self.info.set("Cursor")
            self.stamp = -1
        else:
            self.cursor.set_xdata(event.xdata)
            self.wf.setpos(int(event.xdata))
            self.updateCursor()
    
    def updateCursor(self):
        self.canvas.restore_region(self.background)
        self.a.draw_artist(self.cursor)
        self.canvas.blit(self.a.bbox)
        
    def browse_file(self):
        self.filename = os.path.basename(tkFileDialog.askopenfilename(**self.file_opt))
        self.filelocation.delete(0, END)
        self.filelocation.insert(0,self.file_opt['initialdir']+self.filename)
    
    def plot(self):
        inputFile = self.filelocation.get()
        self.wf = wave.open(inputFile,'rb')
        self.x = np.fromstring(self.wf.readframes(self.wf.getnframes()), dtype=np.int16)
        self.wf.rewind()
        self.a.clear()
        self.a.plot(self.x)
        self.cursor.set_xdata(0)
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.a.bbox)
        self.canvaswidget.focus_set()
        if (self.ALoad.get() == 1): 
            self.loadAnnotations
                              
    def saveAnnotations(self):
        directory = self.file_opt['initialdir'] + self.filename.split('.')[0]  # deleting .wav
        if not os.path.exists(directory):
            os.makedirs(directory)
        for i in self.labeldict:
            with open(directory + '/%s.txt' % self.labeldict[i], 'w') as filehandle:
                json.dump(self.timeValues[i], filehandle)
    
    def loadAnnotations(self):
        directory = self.file_opt['initialdir'] + self.filename.split('.')[0]
        if not os.path.exists(directory):
            print("No annotations to load")  # TODO: Pop-up message
        else:
            for x in os.listdir(directory):
                with open('%s' % x, 'r') as filehandle:
                    values = json.load(filehandle)
                    self.labeldict[len(self.labeldict)] = x.split('.')[0]
                    self.timeValues.append(values)
                
        self.drawAllStamps
        
    def getNext(self):
        self.discard    # delete annotations from previous sound
        fileList = sorted(os.listdir(self.file_opt['initialdir']))
        nextIndex = fileList.index(self.filename) + 1
        if nextIndex == 0 or nextIndex == len(fileList):
            print("No more files") # TODO: Pop-up message
        else:
            self.filename = fileList[nextIndex]
            self.filelocation.delete(0,END)
            self.filelocation.insert(0,self.file_opt['initialdir']+fileList[nextIndex])                      
        self.plot()
    
    def drawAllStamps(self): # TODO
        pass

    def saveAndNext(self):
        self.saveAnnotations()
        self.getNext()
        self.plot()  
