import os
import sys
import filecmp
import re
import subprocess
import hashlib
import random
from subprocess import CalledProcessError, TimeoutExpired

STATUS_CODES = {
    200: 'OK',
    201: 'ACCEPTED',
    400: 'WRONG ANSWER',
    401: 'COMPILATION ERROR',
    402: 'RUNTIME ERROR',
    403: 'INVALID FILE',
    404: 'FILE NOT FOUND',
    408: 'TIME LIMIT EXCEEDED'
}

def write_data(file_name, data):
    """
    Write the data into the file
    """
    f = open(file_name, 'w')
    f.write(data)
    f.close()

def get_data(file_name):
    """
    Get the data from the file
    """
    f = open(file_name, 'r')
    data = f.read()
    f.close()
    return data

class Program:

    def __init__(self, filename, inputfile, timelimit, actualoutputfile):
        self.fileName = filename
        self.language = None
        self.name = None
        self.inputFile = inputfile
        self.actualOutputFile = actualoutputfile
        self.timeLimit = timelimit

    def isvalidfile(self):
        """
        Check if the extension of the file is one
        of the supported extensions
        """
        validfile = re.compile("^(\S+)\.(java|cpp|c|py)$")
        matches = validfile.match(self.fileName)
        if matches:
            self.name, self.language = matches.groups()
            return True
        return False

    def compile(self):
        """
        Check the code for compilation errors
        """
        if os.path.isfile(self.name):
            os.remove(self.name)

        if not os.path.isfile(self.fileName):
            return 404, 'Missing file'

        cmd = None
        if self.language == 'java':
            cmd = 'javac {}'.format(self.fileName)
        elif self.language == 'c':
            cmd = 'gcc -o {0} {1}'.format(self.name, self.fileName)
        elif self.language == 'cpp':
            cmd = 'g++ -o {0} {1}'.format(self.name, self.fileName)
        elif self.language == 'py':
            cmd = 'python -m py_compile {}'.format(self.fileName)

        if cmd is None:
            return 403, 'File is of invalid type'

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=True
            )

            if proc.returncode != 0:
                return 401, proc.stderr
            else:
                return 200, None
        except CalledProcessError as e:
            print(e.output)

    def run(self):
        """
        Run the code and find the output
        """

        if not os.path.isfile(self.fileName) :
            return 404, 'Missing executable file'

        cmd = None
        if self.language == 'java':
            cmd = 'java {}'.format(self.name)
        elif self.language in ['c', 'cpp']:
            cmd = './{}'.format(self.name)
        elif self.language == 'py':
            cmd = 'python {}'.format(self.fileName)

        if cmd is None:
            return 403, 'File is of invalid type'

        try:
            with open(self.actualOutputFile, 'w') as fout:
                fin = None
                if self.inputFile and os.path.isfile(self.inputFile):
                    fin = open(self.inputFile, 'r')
                proc = subprocess.run(
                    cmd,
                    stdin=fin,
                    stdout=fout,
                    stderr=subprocess.PIPE,
                    timeout=self.timeLimit,
                    universal_newlines=True,
                    shell=True
                )

            if proc.returncode != 0:
                return 402, proc.stderr
            else:
                return 200, None
        except TimeoutExpired as tle:
            write_data(self.actualOutputFile, 'time limit exceeded')
            return 408, tle
        except CalledProcessError as e:
            print(e.output)

        if self.language == 'java':
            os.remove('{}.class'.format(self.name))
        elif self.language in ['c', 'cpp']:
            os.remove(self.name)



def codechecker(filename, inputfile=None, actualoutput=None, timeout=1, check=True):
    """
    Create an instance of the Program class
    and compile and run the code
    """
    newprogram = Program(
        filename=filename,
        inputfile=inputfile,
        timelimit=timeout,
        actualoutputfile=actualoutput
    )
    if newprogram.isvalidfile():
        compileResult, compileErrors = newprogram.compile()
        if compileErrors is not None:
            sys.stdout.flush()
            write_data(actualoutput, 'compilation error')
            return

        runtimeResult, runtimeErrors = newprogram.run()
        if runtimeResult == 408:
            return
        if runtimeErrors is not None:
            sys.stdout.flush()
            write_data(actualoutput, 'runtime error')
            return

    else:
        write_data(actualoutput, 'Invalid File')
        return

def execute(code, language, input_text):
    """
    Create files for code, input and output
    Run the code to find the output
    Delete the created files
    """
    file_name = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
    alias_name = file_name
    input_name = '{}.txt'.format(hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest())
    if language == 'java':
        file_name += '.java'
    elif language == 'c':
        file_name += '.c'
    elif language == 'cpp':
        file_name += '.cpp'
    elif language == 'py':
        file_name += '.py'
    output_name = '{}.txt'.format(hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest())

    write_data(file_name, code)
    write_data(input_name, input_text)
    write_data(output_name, '')

    codechecker(
        filename=file_name,
        inputfile=input_name,
        actualoutput=output_name,
        timeout=10,
        check=False
    )

    output_text = get_data(output_name)

    try:
        os.remove(file_name)
        os.remove(input_name)
        os.remove(output_name)
        os.remove(alias_name)
    except Exception as e:
        pass

    return output_text
