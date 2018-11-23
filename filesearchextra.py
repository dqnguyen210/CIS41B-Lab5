#lab 5: The program lets the user find all files in a user defined directory that have 
#       a certain filename and contain a certain text string within the file. 
#Name: Quynh Nguyen
#Date: 2/19/18

# FileSearch class
import os.path
import os
from collections import defaultdict
from re import search
from strsearch import strIsInFile

class FileSearch() :
    def __init__(self, startDir) :
        '''Constructor 
           Recursively walk down all subdirectories of the start directory
           and caches the abs paths of all files in a dictionary
        '''
        self._filePath = [] 
        for (path, dirlist, filelist) in os.walk(startDir) :
            for file in filelist :
                self._filePath.append( (path, file))  
                       

        
    def searchName(self, stopEvent, regex, searchStr, queue) :
        '''Searche through the dictionary for all file names that match the filters
           and return the corresponding paths in a sorted list
        '''      
        resultList = []
        for (filePath, filename) in self._filePath :
            #if the flag to stop searching is set or there are more than 1000 results
            if stopEvent.isSet() or len(resultList) > 1000 : 
                return
            #if filename match the regex and searchStr is in the file
            if search(regex, filename) and ( len(searchStr) == 0 or strIsInFile(searchStr, os.path.join(filePath,filename)) ):
                resultList.append( (filePath, filename) )
        # sort list by paths
        queue.put(sorted( resultList, key=lambda  elem : elem[0]) )