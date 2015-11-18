import sqlite3, os, sys
from analysis_config import *
from binaryParser import *



def init(db, LLVMPath, trialPath, customFuncs = None):
    """Sets up the fault injection campaign visualization database
    by reading log files generated by FlipIt and run output files
    containing injection information.
    Parameters
    ----------
    db : str
        Path to an existing sqlite3 database or the name of a database to
        create.
    LLVMPath : str
        Path to where the LLVM log files (*.LLVM.txt) generated by FlipIt exist.
    trialPath : str
        Path to where the output files of the run(s) are stored. Each output file
        should a seperate fault injection run of the application.
    customFuncs : tuple of function pointers
        Tuple of customs parsing functions (initcustomparsing(), customparser())
    
    Return
    ---------
    sqlite3 database connection handle that is open
    
    Notes
    ----------
    Searched recursively in LLVMPath for log files.
    customFuncs can be None. In that case, no user parseing is done.
    """
    
    if rebuild_database:
        os.system("rm -rf " + db)
    exists = os.path.isfile(db)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    if customFuncs == None:
        customFuncs = (None, None)
    if not exists:
        createTables(c)
        if customFuncs[0] != None:
            customFuncs[0](c)
        readLLVM(c, LLVMPath)
        if customFuncs != None and len(customFuncs) == 2:
            readTrials(c, trialPath, customFuncs[1])
        else:
            readTrials(c, trialPath)
    
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    conn.commit()
    return c

def createTables(c):
    """Add tables into the database need when parsing run output files
    Parameters
    ----------
    c : object
        sqlite3 database handle that is open to a valid filled database
    """
    c.execute("CREATE TABLE sites (site int, type text, comment text, file text, function text, line int, opcode text)")
    c.execute("CREATE TABLE trials (trial int, numInj int, crashed int, detection int, path text, signal int)")
    c.execute("CREATE TABLE injections (trial int, site int, rank int, prob double, bit int, cycle int, notes text)")
    c.execute("CREATE TABLE signals (trial int, num int)")
    c.execute("CREATE TABLE detections (trial int, latency int, detector text)")
    #c.execute("CREATE TABLE ()")


def readLLVM(c, LLVMPath):
    """Searches through the directory structure and collect
    fault injection site information and add it to the database
    
    Parameters
    ----------
    c : object
        sqlite3 database handle that is open to a valid filled database
    LLVMPath : str
        Path to where the LLVM log files (*.LLVM.bin) generated by FlipIt exist.
    """
    print "\n\nReading LLVM log files:"
    end = "LLVM.bin"
    if LLVM_log_type == "ASCII":
        end = "LLVM.txt"
    for path, subdirs, files in os.walk(LLVMPath):
        for name in files:
            if str(name).endswith(end):
                print "\t", name
                if LLVM_log_type == "Binary":
                    parseBinaryLogFile(c, os.path.join(path, name))
                else:
                    parseInjLog(c, path, name)
    

def parseInjLog(c, path,  file):
    """Reads FLipIt LLVM log file and adds fault injection site
    information into the database.
    Parameters
    ----------
    c : object
        sqlite3 database handle that is open to a valid filled database
    path : str
        path to where the LLVM log file resides
    file : str
        name of the LLVM log file to read
    """

    fullPath = os.path.join(path, file)
    rawlog = open(fullPath).readlines()
    funcName = ""   

    for i in range(0, len(rawlog)):
        if "Function Name: " in rawlog[i]:
            funcName = rawlog[i].split(" ")[-1].strip()
        
        if rawlog[i][0] == "#":
            # break line: "#NUM TYPE TXT TXT" to grab NUM  
            split = rawlog[i].split("\t")
            site = int( split[0][1:] )
            type = split[1]
            comment = split[-2]
            line = split[-1]
            srcLine = 0
        
            # compiled with -g and we know the src line number
            if ":" in line:
                split = line.split(":")
                srcLine = int(split[-1])
                file = split[0]
            c.execute("INSERT INTO sites VALUES (?,?,?,?,?,?,?)", (site, type, comment, file, funcName, srcLine, "Unknown"))


def readTrials(c, filePrefix, customParser = None):
    """Parses an output file of a fault injection trial for injections,
    detections, and system level events such as raised signals. 
    
    Parameters
    ----------
    c : object
        sqlite3 database handle that is open to a valid filled database
    filePrefix : str
        path to a fault injection run output file including the first
        part of the file name
    customParser : function pointer
        function the user defines to allow for custom parsing of
        run output file
    """
    print "\n\nReading trials with file prefix:  ", filePrefix
    for trial in range(0, int(numTrials)):

        # determine if trial exists
        path = filePrefix + "_" + str(trial)#".txt"

        if not os.path.exists(path):
            path += ".txt"
            if not os.path.exists(path):
                continue
        print "\t", path
        
        # grab information about the injection(s)
        t = open(path).readlines()
        llvmInj = injCount = crashed = detected = signal = arithFP = 0
       
        c.execute("INSERT INTO trials(trial,path) VALUES (?,?)", (trial, path))
        # look at certain lines in output
        i = 0
        while i < len(t):
            l = t[i]
            if siteMessage in l:
                injCount += 1
                inj = []
                i += 1
                l = t[i]
                while siteEndMessage not in l:
                    if l != "\n":
                        inj.append(l.split(" "))
                    i += 1
                    l = t[i]
 
                # grab info stored in  'inj'
                if "IEEE" in inj[0]:
                    arithFP = 1
                rank = int(inj[1][-1])
                bit = int(inj[3][-1])
                site = int(inj[4][-1])
                prob = float(inj[5][-1])
                c.execute("SELECT * FROM sites WHERE site=?", (site,))
                result = c.fetchone()
                if result == None:
                    print "Unable to locate site #", site, " in database"
                    sys.exit(1)
                type = result[1]
                if "Arithmetic" in type:
                    if arithFP:
                        type = "Arith-FP"
                    else:
                        type = "Arith-Fix"
                    c.execute("UPDATE sites SET type = ? WHERE site=?",(type,site))
                llvmInj = int(inj[7][-1])
                dynCycle = llvmInj
                c.execute("INSERT INTO injections VALUES (?,?,?,?,?,?,?)", (trial, site, rank, prob, bit, dynCycle, 'NULL'))
               
                for j in range(8, len(inj)): 
                    customParser(c, inj[j], trial)


            if detectMessage in l:
                detected = True
                c.execute("INSERT INTO detections VALUES (?,?,?)", (trial, -1, "---"))

            if assertMessage in l:
                signal = True
                crashed = True
                c.execute("INSERT INTO signals VALUES (?,?)", (trial, 6))
            
            if busError in l:
                signal = True
                crashed = True
                c.execute("INSERT INTO signals VALUES (?,?)", (trial, 10))

            if segError in l:
                signal = True
                crashed = True
                c.execute("INSERT INTO signals VALUES (?,?)", (trial, 11))
             
            if customParser != None:
                customParser(c, l, trial)

            i += 1
        c.execute("UPDATE trials SET numInj=? WHERE trials.trial=?", (injCount, trial))
        c.execute("UPDATE trials SET crashed=? WHERE trials.trial=?", (crashed, trial))
        c.execute("UPDATE trials SET detection=? WHERE trials.trial=?", (detected, trial))
        c.execute("UPDATE trials SET signal=? WHERE trials.trial=?", (signal, trial))

def finalize():
    """Cleans up fault injection visualization
    """
    print "Finalizing fault injection visualization..."
    #conn.commit()
    #conn.close()
