# Sound-Annotator
Python sound annotator

Create labels using "Add label" button   
Press numbers on keyboard to select corresponding label    
Generate time stamps for selected label by clicking on soundwave.  
Use "Save&Load Next" button to save annotations to text files. It will also load next sound in the folder if there is any.    
Annotations will be saved in seperate (for each label) .txt files, In JSON string format.  

From the toolbar below, use zoom button only. To zoom back, use right-click + drag  
 
"1, 2, 3, ..." Select label.  
"Esc" : Release label  
Spacebar: Play/Stop  
"X" Discard last annotations  

__Issues:__   
Ugly  
Not-thread safe: Spamming Play/Stop button very quick may freeze program  
Home, Backward, Forward buttons are not working due to blitting. Requires a modification in NavigationToolbar2tk (of matplotlib.backends)    
  
(Done) Loading existing annotations (from folder) is ~~not~~ implemented.  


__Upcoming:__  
Use of arrow keys to fine tune timestamps  
Looping between two time points  
Spectogram  
Support other file formats  
