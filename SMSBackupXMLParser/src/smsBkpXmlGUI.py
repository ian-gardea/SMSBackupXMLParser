'''
@author: Ian Gardea
'''

import logging
from datetime import datetime
import xml.etree.ElementTree as et
import tkinter as tk
import os
import re

class smsBkpXmlGUI(object):
     
    '''
    This class will contain the main logic for the program.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # Create and configure logger to auto write the time concatenated with the message.
        logging.basicConfig(filename='debug.log', 
                            format='%(asctime)s %(message)s', 
                            filemode='w') 
        
        # Create a logging object 
        logger = logging.getLogger() 
        
        # Set the threshold of logger to DEBUG 
        logger.setLevel(logging.DEBUG) 
        
        # Add to log.
        logging.info("Init'd GUI.")

    def makeForm(self, root, fields):
        '''
        Create the GUI, using the array of fields provided by the caller.
        '''

        # Add to log.
        logging.info("Invoking routine makeForm.")
        
        entries = []
        for field in fields:
            row = tk.Frame(root)
            lab = tk.Label(row, width=15, text=field, anchor='w')
            ent = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            entries.append((field, ent))
            
            # Add to log.
            logging.info("Successfully added field " + field + " to GUI.")
        return entries 

    def printValues(self, entries):
        '''
        Get the fields and their current values.
        '''
        # Add to log.
        logging.info("Invoking routine printValues.")
        
        for entry in entries:
            field = entry[0]
            text  = entry[1].get()
            logging.info('%s: "%s"' % (field, text))

    def searchXml(self, xmlFields):
        '''
        Parameters:
            self
            xmlFields - The fields in the tkinter GUI.
        
        Purpose:  
            Search XML files in the input directory for a match based on the field values provided.
            Current field order:
                Date
                Name
        '''

        # Add to log.
        logging.info("Invoking routine searchXml.")

        # Get the current, input, and output directories of this program.
        cwd            = os.getcwd()
        inputDir       = cwd  + '\..\input'
        outputFileName = "output.txt"
        tempFileName   = "temp.tmp"
        
        # Read the current values of the XML fields.
        xmlFieldValues = []
        for field in xmlFields:
            xmlFieldValues.append(field[1].get()) 
        
        # Switch to the input directory. This is where we will do our work.
        try:
            os.chdir(inputDir)
        except Exception as e:
            logging.error('Directory ' + inputDir + ' not found. ' + str(e))
        
        # Create the output file
        try:                    
            outputFile = open(outputFileName,"w")
            
            # Add to log.
            logging.info("Created output file in " + inputDir + ".")
        except Exception as e:
            logging.error('Error opening the output file. ' + str(e))
        
        # Loop through all XML files in the target directory
        for i in os.listdir():
            
            if i.endswith('.xml'):
                try:
                    # Add to log.
                    logging.info("Parsing file " + i + ".")
                    
                    # Open target file
                    myxml = open(i, "r", encoding="utf8")
                    contents = myxml.read()
                    
                    # Make a temp file with the cleaned up text to avoid writing over source file.
                    # Do not name it as an XML, or it will be read by the loop and fail!
                    tempFile = open(tempFileName, "w", encoding="utf8")  # Overwrite file
                    # Clean up any non-escaped ampersands.
                    regex = re.compile(r"&(?!amp;|lt;|gt;)")
                    contents = regex.sub("&amp;", contents)
                    # Write temp file.
                    tempFile.write(contents)
                    tempFile.close()
                     
                    # Parse XML contents using temp file.
                    tempFile = open(tempFileName, "r", encoding="utf8")
                    file = et.parse(tempFile)
                    tempFile.close()
                    
                    xPath1 = "./sms[@contact_name='" + xmlFieldValues[1] + "']"
                    
                    for subelem in file.findall(xPath1):
                        
                        # Get the date, and convert it to a datetime object
                        datetime_str = subelem.attrib['readable_date']
                        datetime_object = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
                        
                        # Find messages for the date entered, if it was entered.
                        if xmlFieldValues[0] == datetime_object.strftime("%m/%d/%Y"):
                            outputFile.write(datetime_str + ' ' + subelem.attrib['body'] + '\n')

                    # Add to log.
                    logging.info("Successfully parsed file " + i + ".")

                except Exception as e:
                    logging.error('An error occurred processing file ' + i + '. ' + str(e))
                    
        # Remove temp file.
        os.remove(tempFileName)