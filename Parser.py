from itertools import islice
import re
C_ARITHMETIC = 1
C_PUSH = 2
C_POP = 3
C_LABEL = 4
C_GOTO = 5
C_IF = 6
C_FUNCTION = 7
C_RETURN = 8
C_CALL = 9
class Parser():
    def __init__(self, inputFile):
        self.f = open(inputFile, "r")
        self.lineNumber = 0
        self.currentCommand = ""

    def hasMoreCommands(self):
        remainingFile = islice(self.f, self.lineNumber, None)  
        for line in remainingFile:
            if isCommand(line) == True:
                return True
        return False
    
    def advance(self):
        line = self.f.readline()
        while isCommand(line) == False:
            line = self.f.readline()
            self.lineNumber += 1
        self.currentCommand = line.strip()

    def commandType(self):
        self.parsedCommand = currentCommand.split()
        if len(parsedCommand) == 1 and parsedCommand[0] != "return":
            return C_ARITHMETIC
        elif parsedCommand[0] == 'push':
            return C_PUSH
        elif parsedCommand[0] == 'pop':
            return C_POP

    def arg1(self):
        return self.parsedCommand[0]
    
    def arg2(self):
        return self.parsedCommand[1]
        
    def isCommand(self, line):
        if line != "\n" and line.startswith("\\") == False:
            return True
        else:
            return False
            
    

