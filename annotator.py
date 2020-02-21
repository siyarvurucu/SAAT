import sys, os
import asyncio
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

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import Event

from essentia.standard import MonoLoader
import libod
import features
class Annotator:
    def __init__(self,parent):
        self.parent = parent
        parent.title("Sound Annotation/Analyzation Tool")
        self.initUI() 
  
    def initUI(self):
        
        self.labeldict = {}
        self.show = []        
        self.timeValues = []
        self.stamp = -1  
        self.stampHistory = []
        
        self.funclist = {"rms","hfc","complex","complex_phase","flux",
        "superflux","noveltycurve","CNNOnsetDetector","RNNOnsetDetector","modifiedKL",
        "weightedPhaseDev","PhaseDev","rectifiedComplexDomain"}
        
        self.featurelist  = ["Audio","rms","spectralCentroid","spectralRolloff","zcr","spectralEntropy",
        "spectralFlux","CentralMoments","CentroidDecrease","stft"] 
        self.hopsizes = []
        self.calculated_features_dict = {}
        self.calculated_features = []
        
        self.chunk_size=2048
        self.mag = []
        self.phase = []
        self.sem = asyncio.Semaphore()

        # Info text
        self.info = StringVar()
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
        
        # BUTTON TO SET DIRECTORY
        self.directory_button = Button(self.parent, text="Directory", command=self.set_directory)
        self.directory_button.grid(row=1, column=0, sticky=W)
        
        #TEXTBOX TO PRINT PATH OF THE SOUND FILE
        self.filelocation = Entry(self.parent)
        self.filelocation["width"] = 25
        self.filelocation.grid(row=0,column=0, sticky=W, padx=10)
        self.filelocation.delete(0, END)
        self.filename = '' # initial file
        self.filelocation.insert(0, self.file_opt['initialdir']+self.filename)
        
        
        #BUTTON TO BROWSE SOUND FILE
        self.open_file = Button(self.parent, text="Browse...", command=self.browse_file)
        self.open_file.grid(row=0, column=0, sticky=W, padx=(220,6)) 
       
        
        #BUTTON TO PLOT SOUND FILE
        self.preview = Button(self.parent, text="Plot", command=self.plot, bg="gray30", fg="white")
        self.preview.grid(row=0, column=0, sticky=W,padx=(300,6))
		
        
        #BUTTON TO draw  stamps
        self.draw = Button(self.parent, text="Draw", command=self.drawAllStamps, bg="gray30", fg="white")
        self.draw.grid(row=1, column=3, sticky=W, padx=(300,6))
        
		# Dropdown Function Select
        self.funcname = StringVar()
        self.funcname.set("Select a function")
        self.fselect = OptionMenu(self.parent,self.funcname,*self.funclist)
        self.fselect.grid(row=1, column=1, sticky=W,padx=(0,6))
		
		# Button to Apply function
        self.afuncbtn = Button(self.parent, text="Apply", command=self.applyfunction) 
        self.afuncbtn.grid(row=1, column=1,padx=(0,6))
        
        # Dropdown SHOW FEATURE
        self.featurename = StringVar()
        self.featurename.set("Audio")
        self.ftselect = OptionMenu(self.parent,self.featurename,*self.featurelist)
        self.ftselect.grid(row=0, column=1, sticky=W)
        
        # Button to show  feature
        self.afuncbtn = Button(self.parent, text="Show Feature", command=self.showfeature) 
        self.afuncbtn.grid(row=0, column=1, sticky=W,padx=(100,6))
        
        #BUTTON TO PLAY/STOP , shortcut: spacebar
        self.play_mode = tk.BooleanVar(self.parent, False)
        self.new_sound =tk.BooleanVar(self.parent, False)
        self.playbutton = Button(self.parent, text="Play", command=self.playsound)
        self.playbutton.grid(row=0, column=2, sticky=W)#, padx=(800, 6))
        self.parent.bind("<space>",self.playsound)
        
        #BUTTON TO SAVE AND LOAD NEXT SOUND FILE 
        self.saveload = Button(self.parent, text="Save& Load Next", command=self.saveAndNext) 
        self.saveload.grid(row=0, column=3, sticky=W)
        
        #BUTTON TO ADD LABELS 
        self.addlabel_button = Button(self.parent, text="Add Labels", command=self.addlabel_gui) 
        self.addlabel_button.grid(row=0, column=3, sticky=W, padx=(300,6)) 
        
        # BUTTON TO DISCARD CURRENT ANNOTATIONS 
        self.discardbutton = Button(self.parent, text="Discard", command=self.discard)
        self.discardbutton.grid(row=0,column=4, sticky=W)
        
        #BUTTON TO get next
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
        
        # tickbox to convert time to samples
        self.isTime = IntVar()
        self.timeorsamples = Checkbutton(master=self.parent, 
                                                text = "time?", variable=self.isTime, onvalue = 1, offvalue = 0)
        self.timeorsamples.grid(row=1, column=3, sticky=W,padx=(220,6))
            
        # tickbox to enable discarding labels  
        self.DLabels = IntVar()
        self.discardlabels_check = Checkbutton(master=self.parent, 
                                                text = "Discard Labels?", variable=self.DLabels, onvalue = 1, offvalue = 0)
        self.discardlabels_check.grid(row=1, column=4, sticky=W)
		
        # init figure for plotting
        self.currentplot = 0
        
        fig = plt.figure(figsize=(18,3), dpi=100)
        self.a = fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(fig, self.parent)
        self.canvaswidget = self.canvas.get_tk_widget()
        self.canvaswidget.grid(row=2,column=0,columnspan=5, sticky=W)
        
        toolbarFrame = Frame(master=self.parent)
        toolbarFrame.grid(row=3,column=0, columnspan=5)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
        self.toolbar.update()

        self.canvas._tkcanvas.grid(row=2,column=0, columnspan = 5, sticky=W)
        self.background = self.canvas.copy_from_bbox(self.a.bbox)
        self.cursor = self.a.axvline(color="k", animated=True)
        self.cursor.set_xdata(0)
        
        self.colors = ['r','g','c','m','y','#FFBD33','#924A03','#D00000','#D000D0','#6800D0','#095549','b','r','r']
        
        # modification to original handler of 'release_zoom', "release_pan" and "_update_view" from NavigationToolbar2
        # latest one is for forward, backward and home buttons
        self.release_zoom_orig = self.toolbar.release_zoom
        self.toolbar.release_zoom = self.new_release_zoom
        self.release_pan_orig = self.toolbar.release_pan
        self.toolbar.release_pan = self.new_release_pan
        self._update_view_orig = self.toolbar._update_view
        self.toolbar._update_view = self.new_update_view
        
        self.canvas.mpl_connect('toolbar_event', self.handle_toolbar)
        cid1 = self.canvas.mpl_connect("button_press_event", self.onclick)
        self.parent.bind("<Escape>", self.release_stamp)
        self.parent.bind("x", self.discard_last)
        
        self.p = pyaudio.PyAudio()
        
        self.parent.bind("<<playbackmove>>",self.playbackMove)
        
        def callbackstream(in_data, frame_count, time_info, status):
            self.sem.acquire()
            data = self.wf.readframes(frame_count)
            self.parent.event_generate("<<playbackmove>>",when="now")
            self.sem.release()
            return (data, pyaudio.paContinue)
        
        self._callbackstream = callbackstream
     

    def applyfunction(self):
        values = getattr(libod,self.funcname.get())(self.filelocation.get())
        if len(values) ==0:
            self.info.set("No detections")
        else:		 
            self.labeldict[len(self.labeldict)] = self.funcname.get()
            var = IntVar()
            var.set(1)
            self.show.append(var)
            self.timeValues.append([i * 44100 for i in values])
            self.drawAllStamps()
    def set_directory(self):
        directory = tkFileDialog.askdirectory() + '/'
        self.file_opt['initialdir'] = directory        
        
    def release_stamp(self,event=None):
        self.stamp = -1
        self.info.set("Cursor")
        
    def discard_last(self,event=None):  # discard last annotation for current sound. button: X
        self.a.lines.pop()
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.a.bbox)
        self.timeValues[self.stampHistory[-1]].pop()
        self.stampHistory.pop()
        
    def discard(self):  # discard all annotations
        self.timeValues = []
        if (self.DLabels.get() == True or self.ALoad.get()==True):
            self.labeldict = {}
            self.show = []
        else:
            for i in range (len(self.labeldict)):
                self.timeValues.append([])
        self.stamp = -1
        self.stampHistory = []
        self.mag = []
        self.phase = []
        self.hopsizes = []
        self.calculated_features_dict = {}
        self.calculated_features = []
        self.currentplot = 0
        
    def label(self,event):
        self.info.set(self.labeldict[int(event.char)-1] + " is selected")
        self.stamp = int(event.char)-1
        
    def addlabel(self):
        self.labeldict[len(self.labeldict)] = self.newlabel_entry.get()
        var = IntVar()
        var.set(1)
        self.show.append(var)
        self.parent.bind("%d" % len(self.labeldict), self.label)
        self.timeValues.append([])
     
    def deselect(self):
         for cb in self.checkbuttons:
            cb.deselect()
            
    def addlabel_gui(self):
        frame_addlabel = Toplevel(master=self.parent)
        frame_addlabel.geometry("%dx%d%+d%+d" % (300, 33*len(self.labeldict), 200, 200))
        frame_addlabel.title("Add Labels")
        self.newlabel_entry = Entry(frame_addlabel)
        self.newlabel_entry.grid(row = 0, column = 0)
        labels_text = "Current Labels:"
        w = Message(frame_addlabel, text=labels_text, width=150)
        w.grid(row=1,column = 0)
        
        labels_text = "Display?"
        w = Message(frame_addlabel, text=labels_text, width=150)
        w.grid(row=1,column = 1)
        
        self.checkbuttons = []
        for i in range (len(self.labeldict)):
            labels_text = '%d' % (i+1) + '. ' + self.labeldict[i]
            w = Message(frame_addlabel, text=labels_text, width=150)
            w.grid(row=i+2,column = 0)          
            check = Checkbutton(master=frame_addlabel,
                                                text = "", variable=self.show[i], onvalue = 1, offvalue = 0)
            check.grid(row=i+2, column=1, sticky=W) 
            self.checkbuttons.append(check)
            
        addbutton = Button(frame_addlabel, text="Add", command=self.addlabel)
        addbutton.grid(row=0, column=1, sticky=W)
        
        togglebutton = Button(frame_addlabel, text="Deselect", command=self.deselect)
        togglebutton.grid(row=1, column=2, sticky=W)
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
        self.stream = self.p.open(format=8,
                        channels=1,
                        rate=44100,
                        output=True,
                        stream_callback=self._callbackstream,
                        start = True,
                        frames_per_buffer = self.chunk_size)
  
    def playsound(self,event=None):
        if self.sem.locked():
            return
        if self.play_mode.get() == True:
            try:
	            self.playbutton.config(text="Play")
	            self.stream.close()
	            self.stream.close()
	            self.play_mode.set(False)
            except:
                print("stop failed")
        else:
                try:
                    self.initStream()
                    self.play_mode.set(True)
                    self.playbutton.config(text="Stop")
                except:
                    print("stop failed")
        
    
    def playbackMove(self,event=None): # move cursor by audio chunk size
        incr = (self.chunk_size)//self.hopsizes[self.currentplot]
        self.cursor.set_xdata(self.cursor.get_xdata()+incr)
        self.updateCursor()
        
    def new_release_zoom(self, *args, **kwargs):
        self.release_zoom_orig(*args, **kwargs)
        s = 'toolbar_event'    # TODO: define this event seperately
        event = Event(s, self)
        self.canvas.callbacks.process(s, Event('toolbar_event', self))
        
    def new_release_pan(self, *args, **kwargs):
        self.release_pan_orig(*args, **kwargs)
        s = 'toolbar_event'    # TODO: define this event seperately
        event = Event(s, self)
        self.canvas.callbacks.process(s, Event('toolbar_event', self))
        
    def new_update_view(self, *args, **kwargs):
        self._update_view_orig(*args, **kwargs)
        s = 'toolbar_event'    # TODO: define this event seperately
        event = Event(s, self)
        self.canvas.callbacks.process(s, Event('toolbar_event', self)) 
        
    def handle_toolbar(self,event):
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.a.bbox)          
            
    def onclick(self,event):
        if (self.toolbar._active == 'ZOOM' or self.toolbar._active == 'PAN'):
            pass
        
        elif (self.stamp > -1):  ## Create a function for this part, Add_new_line
            self.stampHistory.append(self.stamp)
            self.timeValues[self.stamp].append(event.xdata*self.hopsizes[self.currentplot])
            self.a.draw_artist(self.a.axvline(x=event.xdata,color=self.colors[self.stamp]))
            self.canvas.draw()
            self.background = self.canvas.copy_from_bbox(self.a.bbox)
            self.info.set("Cursor")
            self.stamp = -1
        else:
            self.cursor.set_xdata(event.xdata)
            self.wf.setpos(int(event.xdata*self.hopsizes[self.currentplot]))
            self.updateCursor()
            
    def updateCursor(self):
        self.canvas.restore_region(self.background)
        self.a.draw_artist(self.cursor)
        self.canvas.blit(self.a.bbox)
        
    def browse_file(self):
        self.filename = os.path.basename(tkFileDialog.askopenfilename(**self.file_opt))
        self.filelocation.delete(0, END)
        self.filelocation.insert(0,self.file_opt['initialdir']+self.filename)

    def showfeature(self):
        self.a.clear()
        featureName = self.featurename.get()
        if featureName in self.calculated_features_dict:
            self.currentplot = self.calculated_features_dict[featureName]
            if len(self.calculated_features[self.currentplot].shape) == 2:
                ylim = 5000
                binToFreq = np.arange(0,ylim,43.066)  # Fs/N
                self.a.pcolormesh(np.arange(self.calculated_features[self.currentplot].shape[0]),binToFreq , 
                                                self.calculated_features[self.currentplot].T[:binToFreq.size,:])
            else:
                self.a.plot(self.calculated_features[self.currentplot])
            self.canvas.draw()
            self.background = self.canvas.copy_from_bbox(self.a.bbox) 
            hopSize = self.hopsizes[self.calculated_features_dict[featureName]]
        else:
            self.currentplot = len(self.calculated_features)
            self.calculated_features_dict[featureName] = self.currentplot
            result, hopSize = getattr(features,featureName)(self.audio)
            if len(result.shape) == 2:
                ylim = 5000
                binToFreq = np.arange(0,ylim,43.066)  # Fs/N
                self.a.pcolormesh(np.arange(result.shape[0]),binToFreq , 
                                                result.T[:binToFreq.size,:])
            else:
                self.a.plot(result)
            self.canvas.draw()
            self.background = self.canvas.copy_from_bbox(self.a.bbox) 
            self.calculated_features.append(result)
            self.hopsizes.append(hopSize)
        self.drawAllStamps()

    def plot(self):
        self.discard()
        inputFile = self.filelocation.get()
        self.wf = wave.open(inputFile,'rb')
        self.featurename.set("Audio")
        self.audio = MonoLoader(filename=inputFile, sampleRate=44100)()
        self.showfeature()   
        self.cursor.set_xdata(0)        
        self.canvaswidget.focus_set()
        if (self.ALoad.get() == 1): 
            self.loadAnnotations()
                              
    def saveAnnotations(self):
        directory = self.file_opt['initialdir'] + "Annotations/" + self.filename.split('.')[0] # deleting .wav
        if not os.path.exists(directory):
            os.makedirs(directory)
        for i in self.labeldict:
            with open(directory + '/%s.txt' % self.labeldict[i], 'w') as filehandle:
                json.dump(self.timeValues[i], filehandle)
    
    def loadAnnotations(self):
        directory = self.file_opt['initialdir'] + "Annotations/" + self.filename.split('.')[0] + "/"
        if not os.path.exists(directory):
            print("No annotations")   # TODO: message pop-up
        else:
            for x in sorted(os.listdir(directory)):
                with open(directory + x, 'r') as filehandle:
                    values = json.load(filehandle)
                    if self.isTime.get() == 1:
                        values = [v*44100 for v in values]
                    self.labeldict[len(self.labeldict)] = x.split('.')[0]
                    var = IntVar()
                    var.set(1)
                    self.show.append(var)
                    self.timeValues.append(values)
        
    def getNext(self):
        self.discard()    # deleting annotations previous sound
        fileList = sorted(os.listdir(self.file_opt['initialdir']))
        nextIndex = fileList.index(self.filename) + 1
        if nextIndex == 0 or nextIndex == len(fileList):
            print("No more files") # TODO: message pop-up
        else:
            self.filename = fileList[nextIndex]
            self.filelocation.delete(0,END)
            self.filelocation.insert(0,self.file_opt['initialdir']+fileList[nextIndex])                      
        self.plot()
    def drawAllStamps(self):
        hs = self.hopsizes[self.currentplot]
        try:    
            del self.a.lines[1:]
        except:
            pass
        for i in self.labeldict:
            if self.show[i] .get()== 1:
                for j in self.timeValues[i]:
                    self.a.draw_artist(self.a.axvline(x=j//hs,color=self.colors[i]))
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.a.bbox)

    def saveAndNext(self):
        self.saveAnnotations()
        self.getNext()
        self.plot()                     
        
    
