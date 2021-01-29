import Parser
import CodeWriter

class Main:
    def __init__(self, fileName):
        self.inputFile = fileName
        self.outputFile = fileName[0:len(fileName)-2] + "asm"
        self.processFile()
    
    def processFile(self):
        parser = Parser(self.inputFile)
        code = CodeWriter(self.outputFile)

        while parser.hasMoreCommands() == True:
            parser.advance()
            CodeWriter(parser.currentCommand)            
                
