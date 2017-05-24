# -*- coding: utf-8 -*-

"""


"""

import sys
import argparse
from coetoolcore import *
from coetoolgui import *


def main():
    
    parser = argparse.ArgumentParser(description='coetool: convert from .coe file (VGA mem) to image file and vice versa', epilog='Example: coetool --convert rom_vga.coe outimage.jpg')
    parser.add_argument('-c', '--convert', metavar='FILE', nargs=2, help='convert from IN_FILE to OUT_FILE (supported output formats: bmp, jpg, png, and coe )' )
    args = parser.parse_args()
    if args.convert: 
        convert(args.convert[0], args.convert[1])
    else:
        run_gui()
    
def run_gui():
    print('run gui')
    
    app = QApplication(sys.argv)
    coetoolgui = CoetoolGui()
    coetoolgui.show()
    sys.exit(app.exec_())
    
        
def convert(in_file, out_file): #转换
    
    in_file_ext = in_file.rsplit('.',maxsplit=1)[1].lower()
    out_file_ext = out_file.rsplit('.',maxsplit=1)[1].lower()
    
    conversion = CoeConverter(in_file)
    
    if in_file_ext != 'coe' and out_file_ext != 'coe' :
        print('No .coe file')
    
    elif in_file_ext == 'coe':
            
        if out_file_ext not in ['bmp', 'jpg', 'png']:
            print('img extension unknown')
        else:
            conversion.exportImg(out_file, out_file_ext)
    
    else:
        if in_file_ext not in ['bmp', 'jpg', 'png']:
            print('img format not supported')
        else:
            conversion.createCoe(out_file)
            print('file ' + out_file + ' written to disk')


if __name__ == '__main__':
    main()