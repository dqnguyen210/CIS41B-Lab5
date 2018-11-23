
#lab 5: The program lets the user find all files in a user defined directory that have 
#       a certain filename and contain a certain text string within the file. 
#Name: Quynh Nguyen
#Date: 2/19/18

# FindWin class 

import os.path
import os
import tkinter as tk
import tkinter.filedialog 
import tkinter.messagebox as tkmb
import threading
import queue
import sys
import re
from filesearch import FileSearch

class FindWin(tk.Tk) :
    def __init__(self) :
        ''' Constructor sets up the GUI window
        '''
        super().__init__()      # initialize Tk parent class

        self.title("Search Window") # set title

        # label Current Folder
        curFolder = tk.Label(self, text="Current Folder:") 
        curFolder.grid(row=0, column=0, padx=5, sticky='we')     
        #label for start directory
        self._startDir = tk.StringVar()
        self._startDir.set(os.path.expanduser('~')) # Set the start directory to be user's home directory        
        startDir = tk.Label(self, textvariable=self._startDir) 
        startDir.grid(row=0, column=1, padx=5, sticky='w')        
        
        # Change Folder button
        changeButton = tk.Button(self, text="Change Folder", command=self._selectDir)   
        changeButton.grid(row=1, column=0)
        
        # Regex filter label
        Lfilter = tk.Label(self, text="Regex Filter:") 
        Lfilter.grid(row=2, column=0, padx=(20,0), sticky='we')         
        # Entry widget
        self._reFilter = tk.StringVar() # user's regex filter
        regexEntry = tk.Entry(self, textvariable=self._reFilter)
        regexEntry.grid(row=2, column=1, sticky='we')          
        self.grid_columnconfigure(1, weight=1) # expand column index 1            
        regexEntry.bind("<Return>", self._search) 
        regexEntry.focus_set()
        
        # Search string label
        Lfilter = tk.Label(self, text="Search String:") 
        Lfilter.grid(row=3, column=0, padx=(20,0), sticky='we')         
        # Entry widget
        self._searchStr = tk.StringVar() # user's regex filter
        strEntry = tk.Entry(self, textvariable=self._searchStr)
        strEntry.grid(row=3, column=1, sticky='we')          
        self.grid_columnconfigure(1, weight=1) # expand column index 1            
        strEntry.bind("<Return>", self._search) 
        strEntry.focus_set()
        
        # Results label
        Lresult = tk.Label(self, text="Results:")
        Lresult.grid(row=4, column=0, sticky='nw')   
        # create scrollbar
        sy = tk.Scrollbar(self, orient=tk.VERTICAL)  
        sx = tk.Scrollbar(self, orient=tk.HORIZONTAL)                
        # create a listbox
        self._fileListbox = tk.Listbox(self, height=10, yscrollcommand=sy.set, xscrollcommand=sx.set)        
        self._fileListbox.grid(row=5, column=0, sticky='nswe', columnspan=2) 
        self._fileListbox.grid_columnconfigure(0, weight=1) # expand column index 1            
        self.grid_rowconfigure(5, weight=1) # expand row index 5            
        # connect scrollbar to listbox
        sy.config(command=self._fileListbox.yview)
        sy.grid(row=5, column=2, sticky='nse')                
        sx.config(command=self._fileListbox.xview)            
        sx.grid(row=6, column=0, sticky='nwe', columnspan=2)                
        
        # label for number of files
        self._labelText = tk.StringVar()        
        self._Lcount = tk.Label(self, textvariable=self._labelText)
        self._Lcount.grid(row=7, column=0)
        
        self._id = 0 #search thread ID
        self._resultList = []  #file paths list
        self.update() # show the window on screen
        self.protocol("WM_DELETE_WINDOW", self._exit)       
        
        self.FS = FileSearch(self._startDir.get()) #FileSearch object to search for files       
        self._stopEvent = threading.Event() #event to stop search thread
        self._firstSearch = True
        
        
    def _selectDir(self) :
        '''The callback method for the "Change Folder" button
        '''
        self._startDir.set( tk.filedialog.askdirectory(initialdir= self._startDir))
        
        # update label for start directory
        startDir = tk.Label(self, textvariable=self._startDir) 
        startDir.grid(row=0, column=1, padx=5, sticky='we')        
        
        self.FS = FileSearch(self._startDir.get()) # update the new directory to search
        self._search() # Call the private search method
        
        
    def _search(self, *args) :
        '''The callback for the "Regex filter" and "Search String" entry boxes
        '''
        try:  #Compile the user input regular expression
            regex = re.compile( self._reFilter.get(), re.I)    # case insensitive
        except Exception as e :
            tkmb.showerror("Invalid Regex", "Please enter a valid regex", parent=self)
            return
        if not self._firstSearch :
            self._fileListbox.delete(0, tk.END) #clear previous listbox        
            self._cancelSearch()      #stop the previous search
            self._resultList.clear()  #reset result list
        
        #start a new search thread
        self._searchThread = threading.Thread(target=self.FS.searchName, args=(self._stopEvent, regex, self._searchStr.get(), self._resultList))
        self._searchThread.start()      
        self._firstSearch = False
        self.after(100, self.updateListBox)
        
              
    def _cancelSearch(self) :
        '''Method to cancel the search thread and updateListbox after() thread
        '''
        self.after_cancel(self._id)
        self._stopEvent.set()
        self._searchThread.join()
        self._stopEvent.clear()        
        
        
    def updateListBox(self) :
        '''Method to insert results to listbox or display corresponding messages
        '''
        #update the listbox with the newest file paths
        self._fileListbox.insert(tk.END, *list(map(lambda elem : elem[1], self._resultList[self._fileListbox.size() : ])))
        # update label for number of files
        self._labelText.set("Found "+ str(self._fileListbox.size())+ " files")    
        
        if self._searchThread.isAlive() : #if there is a search thread running
            self._id = self.after(100, self.updateListBox)
            
        else : #if the search thread is done
            if self._fileListbox.size() >= 1000:
                tkmb.showwarning("Files Overload", "There are too many files to show", parent=self)
                self._labelText.set("Found more than 1000 files")
                return
            if self._fileListbox.size() == 0: # if listbox is empty
                tkmb.showinfo("File Not Found", "There is no file match the filter", parent=self)
                   
    
    def _exit(self) :
        '''The callback method that runs when X is clicked
        '''
        if self._searchThread.isAlive() : self._cancelSearch()
        self.destroy()    
        
        
        
def main() :
    win = FindWin()
    win.mainloop()

main()