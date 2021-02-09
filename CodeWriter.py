from Parser import C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL
from Parser import Parser
class CodeWriter():

    def __init__(self, outputFile, isDirectory):
        self.f = open(outputFile, "a")
        self.currentFunction = ''
        self.labelCounter = 0
        self.callCounter = {}
        if isDirectory == True:
            self.writeInit()

    def writeInit(self):
        # instructions to be stored at start of ROM - set up stack pointer and call Sys.init
        self.fileName = 'sys'
        self.currentFunction = 'bootstrap'
        self.currentCommand = "call sys.init 0"
        output = '@256\n'
        output += 'D=A\n'
        output += '@SP\n'
        output += 'M=D\n'
        output += self.writeCall('Sys.init', '0')
        self.f.write(output)

    def setFileName(self, inputFile):
        # set filename to current .vm file being processed
        self.fileName = inputFile[0:(len(inputFile)-3)].split('/')[-1]

    def close(self):
        # close output file at end of processing
        self.f.close()

    def writeCode(self, parser):
        # store current vm command
        self.currentCommand = parser.currentCommand

        # based on commandType, translate .vm instruction into assembly using class methods and write into output file
        commandType = parser.commandType()
        code = ""
        if commandType == C_ARITHMETIC:
            code = self.writeArithmetic(commandType, parser.arg1())
        elif commandType == C_PUSH or commandType == C_POP:
            code = self.writePushPop(commandType, parser.arg1(), parser.arg2())
        elif commandType == C_LABEL:
            code = self.writeLabel(parser.arg1())
        elif commandType == C_GOTO:
            code = self.writeGoto(parser.arg1())
        elif commandType == C_IF:
            code = self.writeIf(parser.arg1())
        elif commandType == C_FUNCTION:
            code = self.writeFunction(parser.arg1(), parser.arg2())
        elif commandType == C_CALL:
            code = self.writeCall(parser.arg1(), parser.arg2())
            self.currentFunction = parser.arg1()
        elif commandType == C_RETURN:
            code = self.writeReturn()
        self.f.write(code)

    def writeArithmetic(self, commandType, arg1):
        # translate arithmetic vm instructions into assembly

        # helper function to push D register value onto stack
        def push():
            nonlocal output
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'
        # helper function to pop value at top of stack into D register
        def pop():
            nonlocal output
            output += '@SP\n'
            output += 'AM=M-1\n'
            output += 'D=M\n' 
            
        # initialize output with comment containing current vm command 
        output = '//' + self.currentCommand + '\n'
               
        if arg1 == 'add' or arg1 == 'sub':  # addition/subtraction instructions
            pop()
            output += '@R13\n'
            output += 'M=D\n'
            pop()
            output += '@R13\n'
            if arg1 == 'add':
                output += 'D=D+M\n'
            if arg1 == 'sub':
                output += 'D=D-M\n'
            push() 

        elif arg1 == 'neg':  # negation instruction
            pop()
            output += 'D=-D\n'
            push()
        
        elif arg1 == 'eq' or arg1 == 'lt' or arg1 == 'gt': # equal to/less than/greater than instructions
            pop()
            output += '@R13\n'
            output += 'M=D\n'
            pop()
            output += '@R13\n'
            output += 'D=D-M\n'
            # if true, then jump to true
            output += '@true' + str(self.labelCounter) + '\n'
            if arg1 == 'eq':
                output += 'D;JEQ\n'
            if arg1 == 'lt':
                output += 'D;JLT\n'
            if arg1 == 'gt':
                output += 'D;JGT\n'
            # if false, then jump to end
            output += 'D=0\n'
            push()
            output += '@end' + str(self.labelCounter) +'\n'
            output += '0;JMP\n'
            # true
            output += '(true' + str(self.labelCounter) + ')\n'
            output += 'D=-1\n'
            push()
            # end
            output += '(end' + str(self.labelCounter) + ')\n'
            self.labelCounter += 1 

        elif arg1 == 'and' or arg1 == 'or': # and/or instruction
            pop()
            output += '@R13\n'
            output += 'M=D\n'
            pop()
            output += '@R13\n'
            if arg1 == 'and':
                output += 'D=D&M\n'
            if arg1 == 'or':
                output += 'D=D|M\n'          
            push()

        elif arg1 == 'not': # not instruction
            pop()
            output += 'D=!D\n'
            push()

        # return generated code to be written into output file
        return output 
  

    def writePushPop(self, commandType, arg1, arg2):
        # translate push and pop vm instructions into assembly
        memoryDict = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT', 'temp': '5'}
        
        # initialize output with comment containing current vm command 
        output = '// ' + self.currentCommand +'\n'

        # local, argument, this, that, and temp memory segment push operation
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

        # local, argument, this, that, and temp memory segment pop operation
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

        # constant push operation
        elif arg1 == 'constant':
            output += '@' + arg2 +'\n'
            output += 'D=A\n'
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'

        # static memory segment push operation
        elif arg1 == 'static' and commandType == C_PUSH:
            output += '@' + self.fileName + '.' + arg2 + '\n'
            output += 'D=M\n'
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'

        # static memory segment pop operation
        elif arg1 == 'static' and commandType == C_POP:
            output += '@SP\n'
            output += 'AM=M-1\n' 
            output += 'D=M\n' 
            output += '@' + self.fileName + '.' + arg2 + '\n'
            output += 'M=D\n'

        # push THIS or THAT pointer onto stack
        elif arg1 == 'pointer' and commandType == C_PUSH:
            if arg2 == '0':
                output += '@THIS\n'
            elif arg2 == '1':
                output += '@THAT\n'
            output += 'D=M\n'
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'

        # pop value at top of stack into THIS or THAT pointer
        elif arg1 == 'pointer' and commandType == C_POP:
            output += '@SP\n'
            output += 'AM=M-1\n'
            output += 'D=M\n'
            if arg2 == '0':
                output += '@THIS\n'
            elif arg2 == '1':
                output += '@THAT\n'
            output += 'M=D\n'

        # return generated code to be written into output file
        return output
    
    def writeLabel(self, arg1):
        # write label in format: fileName.functionName$labelName
        output = '//' + self.currentCommand + '\n'
        output += "(" + self.fileName + "." + self.currentFunction + "$" + arg1 + ")\n"
        return output

    def writeGoto(self, arg1):
        # write jump instruction to goto passed label 
        output = '//' + self.currentCommand + '\n'
        output += "@" + self.fileName + "." + self.currentFunction + "$" + arg1 + "\n"
        output += "0;JMP\n"
        return output
    
    def writeIf(self, arg1):
        # write conditional jump instruction to goto passed label
        output = '//' + self.currentCommand + '\n'
        output += '@SP\n'
        output += 'AM=M-1\n'
        output += 'D=M\n'
        output += "@" + self.fileName + "." + self.currentFunction + "$" + arg1 + "\n"
        output += "D;JNE\n"
        return output
    
    def writeFunction(self, functionName, numVars):
        # get function name without file context
        if "." in functionName:
            self.currentFunction = functionName.split(".")[1]
        else:
            self.currentFunction = functionName

        # helper function for pushing D register value onto stack
        def push():
            nonlocal output
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'

        # initialize output with comment containing current vm command 
        output = '//' + self.currentCommand + '\n'

        # create label for function with format fileName.functionName
        output += '(' + self.fileName + '.' + self.currentFunction + ')\n' 
        # initialize function local variables at top of stack to 0  
        for _ in range(int(numVars)):
            output += 'D=0\n'
            push()
        return output

    def writeCall(self, calledFunction, numArgs):
        # handle vm function call instructions

        # helper function to push D register value onto stack
        def push():
            nonlocal output
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'
        # helper function to pop value at top of stack into D register
        def pop():
            nonlocal output
            output += '@SP\n'
            output += 'AM=M-1\n'
            output += 'D=M\n' 

        # get full function name in format fileName.functionName 
        fullFunctionName = self.fileName + "." + self.currentFunction
        
        # if full function name is in call counter dictionary, then get call number and increment call counter
        if fullFunctionName in self.callCounter.keys():
            callNumber = self.callCounter[fullFunctionName]
            self.callCounter[fullFunctionName] += 1
        # if full function name is not in call counter, then set call number to 0 and initialize function in call counter
        else:
            callNumber = 0
            self.callCounter[fullFunctionName] = 1

        # initialize output with comment containing current vm command 
        output = '//' + self.currentCommand + '\n'
        # push return address onto stack to save caller's return address
        output += "@" + self.fileName + "." + self.currentFunction + "$ret." + str(callNumber) + "\n"
        output += 'D=A\n'
        push()
        # push LCL pointer onto stack to save caller's LCL pointer
        output += '@LCL\n'
        output += 'D=M\n'
        push()
        # push ARG pointer onto stack to save caller's ARG pointer
        output += '@ARG\n'
        output += 'D=M\n'
        push()
        # push THIS pointer onto stack to save caller's THIS pointer
        output += '@THIS\n'
        output += 'D=M\n'
        push()
        # push THAT pointer onto stack to save caller's THAT pointer
        output += '@THAT\n'
        output += 'D=M\n'
        push()
        # set ARG pointer
        output += '@SP\n'
        output += 'D=M\n'
        output += '@5\n'
        output += 'D=D-A\n'
        output += '@' + numArgs + '\n'
        output += 'D=D-A\n'
        output += '@ARG\n'
        output += 'M=D\n'
        # set LCL pointer to point to top of stack
        output += '@SP\n'
        output += 'D=M\n'
        output += '@LCL\n'
        output += 'M=D\n'
        # jump to called function
        output += '@' + calledFunction +'\n'
        output += '0;JMP\n'
        # add label for where to return when callee returns
        output += '(' + self.fileName + '.' + self.currentFunction + '$ret.' + str(callNumber) + ')\n'
        return output
    
    def writeReturn(self):
        # handle vm function return instruction

        # helper function to push D register value onto stack
        def push():
            nonlocal output
            output += '@SP\n'
            output += 'A=M\n'
            output += 'M=D\n'
            output += '@SP\n'
            output += 'M=M+1\n'
        # helper function to pop value at top of stack into D register
        def pop():
            nonlocal output
            output += '@SP\n'
            output += 'AM=M-1\n'
            output += 'D=M\n' 

        # initialize output with comment containing current vm command  
        output = '//' + self.currentCommand + '\n'
        # store address of end of frame in R13
        output += '@LCL\n'
        output += 'D=M\n'
        output += '@R13\n'
        output += 'M=D\n'
        # place return address in R14
        output += '@LCL\n'
        output += 'D=M\n'
        output += '@5\n'
        output += 'A=D-A\n'
        output += 'D=M\n' 
        output += '@R14\n'
        output += 'M=D\n'
        # place return value in ARG on stack
        pop()
        output += '@ARG\n'
        output += 'A=M\n'
        output += 'M=D\n'
        # place SP at ARG + 1
        output += '@ARG\n'
        output += 'D=M+1\n'
        output += '@SP\n'
        output += 'M=D\n'
        # recover LCL pointer
        output += '@4\n'
        output += 'D=A\n'
        output += '@R13\n'
        output += 'A=M-D\n'
        output += 'D=M\n'
        output += '@LCL\n'
        output += 'M=D\n'
        # recover ARG pointer
        output += '@3\n'
        output += 'D=A\n'
        output += '@R13\n'
        output += 'A=M-D\n'
        output += 'D=M\n'
        output += '@ARG\n'
        output += 'M=D\n'
        # recover THIS pointer
        output += '@2\n'
        output += 'D=A\n'
        output += '@R13\n'
        output += 'A=M-D\n'
        output += 'D=M\n'
        output += '@THIS\n'
        output += 'M=D\n'
        # recover THAT pointer
        output += '@R13\n'
        output += 'A=M-1\n'
        output += 'D=M\n'
        output += '@THAT\n'
        output += 'M=D\n'
        # jump to caller
        output += '@R14\n'
        output += 'A=M\n'
        output += '0;JMP\n'
        return output