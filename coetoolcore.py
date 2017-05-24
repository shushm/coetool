# -*- coding: utf-8 -*-

"""
Doc...

"""

from PyQt5 import QtCore, QtGui
from PIL import Image
import tempfile


class CoeConverter:
    
    def __init__(self, in_file):
        
        self.in_file = in_file
        self.in_file_ext = in_file.rsplit('.',maxsplit=1)[1].lower()
        

        #RGB palette generation: Red(3bits) Green(3bits) Blue(2bits)/1pixel = 256 colors (as used in .coe VGA mem files). NECESSARY
        self.Qtrgb332_palette=[] 
        
        for i in range(256):
            # & 224 means a bit mask for the MSB and >> 5 is a bitwise to strip LSB bits
            self.Qtrgb332_palette.append(QtGui.qRgb( int(((i & 224) >> 5)*(255/7)), int(((i & 28) >> 2)*(255/7)), int((i & 3)*(255/3)))) 
        
        self.dataInit()
        
        
    def dataInit(self):
        
        if self.in_file_ext == 'coe':   
            self.imgbytes = bytes.fromhex(self.coe_parse('memory_initialization_vector=', ';', '=').replace(',', '').replace('\n',''))
            self.height=int(self.coe_parse('Height:',',',' '))
            self.width=int(self.coe_parse('Width:','\n',' ')) #end char = new line!
            self.img = QtGui.QImage(self.imgbytes, self.width, self.height, QtGui.QImage.Format_Indexed8)
            self.img.setColorTable(self.Qtrgb332_palette) #NECESSARY
            
        else:
            img = QtGui.QImage(self.in_file)
            self.height = str(img.height())
            self.width = str(img.width())
            #img2 = img.convertToFormat(QtGui.QImage.Format_Indexed8, self.Qtrgb332_palette) #create 8 bits img with QImage Qtrgb332_palette necessary.
            img2 = img.convertToFormat(QtGui.QImage.Format_RGB888) #create 24 bits img with QImage Qtrgb888
            tmpfileimg2 = tempfile.NamedTemporaryFile(suffix='.bmp', delete=False)
            tmpfileimg2.close()
            img2.save(tmpfileimg2.name,'BMP',-1) #save 8 bits img with QImage  try via buffer TO-DO create _tmp_ file
            img3 = Image.open(tmpfileimg2.name) #open image with PIL
            #self.imgbytes =[format(i, '02x').upper() for i in list(img3.getdata())] #extract data with PIL
            self.imgbytes =tuple(list(img3.getdata())) #extract data with PIL
            
               
    def coe_parse(self, key_name, key_end_char, separator):
        with open(self.in_file, encoding='utf-8', mode='r') as coefile:
            coefile_data = coefile.read()   
            key=key_name
            key_offset=coefile_data.find(key)
            key_end=coefile_data.find(key_end_char,key_offset) 
            key_value=coefile_data[key_offset:key_end].split(separator)[1] 

            return key_value


    def createCoe(self, out_file):
        with open(out_file, encoding='utf-8', mode='wt') as out_coe_file:
            #out_coe_file.write('; VGA Memory Map\n; .COE file with hex coefficients\n; Height: '+self.height+', Width: '+self.width+'\n\nmemory_initialization_radix=16;\n')
            #out_coe_file.write('memory_initialization_vector=\n')
            out_coe_file.write('; Image Memory Map\n; .COE file with hex coefficients\n; Height: '+self.height+', Width: '+self.width+'\n\nmemory_initialization_radix=10;\n')
            out_coe_file.write('memory_initialization_vector=\n')
           
            for i,b in enumerate(self.imgbytes):
                if i > 0 and i % 16 == 0:           #TO-DO check if necessary, check in FPGA
                    out_coe_file.write('\n')
                if i == len(self.imgbytes)-1:
                    out_coe_file.write("%s,%s,%s" %(b[0],b[1],b[2]))
                else: 
                    #out_coe_file.write(b+',')
                    out_coe_file.write("%s,%s,%s" %(b[0],b[1],b[2])+',')

            out_coe_file.write(';')
            
            
    def exportImg(self, out_file, imgformat):
        self.img.save(out_file, imgformat, -1)
        print('file ' + out_file + ' written to disk')
    
