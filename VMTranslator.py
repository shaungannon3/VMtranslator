from Parser import Parser
from CodeWriter import CodeWriter
import sys
import os

#!/usr/bin/env python3
class Main:
    def __init__(self, inputPath):
        if inputPath.endswith(".vm"):
            inputFile = inputPath
            outputFile = inputPath[0:len(inputPath)-2] + "asm"
            # remove output .asm file if already exists
            if os.path.exists(outputFile):
                os.remove(outputFile)
            # create new codewriter
            self.code = CodeWriter(outputFile, isDirectory = False)
            # parse input .vm file
            self.parseFile(inputFile)
            # close output file
            self.code.close()
        else:
            if os.path.isdir(inputPath):
                directoryName = inputPath.split("/")[-1]
                outputFile = inputPath + "/" + directoryName + ".asm"
                # remove output .asm file if already exists
                if os.path.exists(outputFile):
                    os.remove(outputFile)
                # create new codewriter    
                self.code = CodeWriter(outputFile, isDirectory = True)
                # loop through files in directory and parse all .vm files
                for entry in os.scandir(inputPath):
                    if entry.path.endswith(".vm"):
                        inputFile = entry.path
                        self.parseFile(inputFile)
                # close output file
                self.code.close()
    
    def parseFile(self, inputFile):
        parser = Parser(inputFile)
        self.code.setFileName(inputFile)
        while parser.hasMoreCommands() == True:
            parser.advance()
            self.code.writeCode(parser)

if __name__ == '__main__':
    main = Main(str(sys.argv[1]))

                
