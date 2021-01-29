from Parser import C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL

class CodeWriter():

    def __init__(self, outputFile):
        self.fileName = outputFile[0:(len(outputFile)-4)]
        self.f = open(outputFile, "w")


    def writeCode(self, currentCommand):
        self.currentCommand = currentCommand
        commandType = currentCommand.commandType()
        if commandType == C_ARITHMETIC:
            code = writeArithmetic(commandType, currentCommand.arg1())
        elif commandType == C_PUSH or commandType == C_POP:
            code = writePushPop(commandType, currentCommand.arg1(), currentCommand.arg2())
        f.write(code)

    def writeArithmetic(self, commandType, arg1):
        # TO DO
    
    def writePushPop(self, commandType, arg1, arg2):
        memoryDict = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT', 'temp': 5}
        
        output = '//' + self.currentCommand +'\n'
        if arg1 in memoryDict.keys() and commandType == C_PUSH:
            output += '@' + arg2 +'\n'
            output += 'D=A\n'
            if arg1 == 'temp': # temp does not have pointer so must save arg2 in register 13 instead of D register
                output += '@R13\n'
                output += 'M=D\n'
                output += '@' + memoryDict[arg1] +'\n'
                output += 'D=A\n'
                output += '@R13\n'
            else:
                output += '@' + memoryDict[arg1] +'\n'
            output += 'A=D+M\n'
            output += 'D=M\n'
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'
        elif arg1 in memoryDict.keys() and commandType == C_POP:
            output += '@SP\n'
            output += 'AM=M-1\n' # decrement stack pointer and go to address
            output += 'D=M\n' 
            output += '@R13\n'
            output += 'M=D\n' # store value at top of stack in register 13                      
            output += '@' + arg2 +'\n'
            output += 'D=A\n'
            if arg1 == 'temp':
                output += '@R14\n'
                output += 'M=D\n' # store address of destination in register 14
                output += '@' + memoryDict[arg1] +'\n'
                output += 'D=A\n'
                output += '@R14\n'
                output += 'M=D+M\n'
            else:    
                output += '@' + memoryDict[arg1] +'\n'
                output += 'D=D+M\n'
                output += '@R14\n'
                output += 'M=D\n' # store address of destination in register 14
            output += '@R13\n'
            output += 'D=M\n' # place value at top of stack in data register
            output += '@R14\n'
            output += 'A=M\n' # go to address of destination
            output += 'M=D\n'

        elif arg1 == 'constant':
            output += '@' + arg2 +'\n'
            output += 'D=A\n'
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'

        elif arg1 == 'static' and commandType == C_PUSH:
            output += '@' + self.fileName + '.' + arg2 + '\n'
            output += 'D=M\n'
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'
    
        elif arg1 == 'static' and commandType == C_POP:
            output += '@SP\n'
            output += 'AM=M-1\n' 
            output += 'D=M\n' 
            output += '@' + self.fileName + '.' + arg2 + '\n'
            output += 'M=D\n'

        elif arg1 == 'pointer' and commandType = C_PUSH:
            if arg2 = '0':
                output += '@THIS\n'
            elif arg2 = '1':
                output += '@THAT\n'
            output += 'D=M\n'
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'

        elif arg1 == 'pointer' and commandType = C_POP:
            output += '@SP\n'
            output += 'AM=M-1\n'
            output += 'D=M\n'
            if arg2 = '0':
                output += '@THIS\n'
            elif arg2 = '1':
                output += '@THAT\n'
            output += 'M=D\n'
        
        return output

                            

            

