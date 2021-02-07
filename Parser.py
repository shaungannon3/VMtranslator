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
        self.currentLine = ""
        self.currentCommand = ""
        self.parsedCommand = ""

    def hasMoreCommands(self):
        for line in self.f:
            if self.isCommand(line) == True:
                self.currentLine = line
                return True
        return False
    
    def advance(self):
        self.currentCommand  = self.currentLine.strip()
        self.parsedCommand = self.currentCommand.split()

    def commandType(self):
        commandDict = {'push': C_PUSH, 'pop': C_POP, 'label': C_LABEL, 'goto': C_GOTO, 'if-goto': C_IF,
        'function': C_FUNCTION, 'return': C_RETURN, 'call': C_CALL
        }
        if self.parsedCommand[0] in commandDict.keys():
            return commandDict[self.parsedCommand[0]]
        else:
            return C_ARITHMETIC

    def arg1(self):
        if self.commandType() == C_ARITHMETIC:
            return self.parsedCommand[0]
        else:
            return self.parsedCommand[1]
    
    def arg2(self):
        return self.parsedCommand[2]
        
    def isCommand(self, line):
        if line.strip() and line.startswith("//") == False:
            return True
        else:
            return False
            
    

