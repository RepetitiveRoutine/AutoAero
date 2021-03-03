import os
from os import path
import glob
import shutil
import asyncio
import time
import multiprocessing
from pathlib import Path
import sys

current_version = "Version 1.5"

#### PATH TO ALL THE GENERIC FILES AND THE STUDY FOLDERS LOCATION ####
STRAIGHT_JRNL_PATH = "lib\\SS-GEN.jou"
YAW_JRNL_PATH = "lib\\yaw.JOU"
GEN_ENS_PATH = "lib\\SS-POST.py"
FILE_CONTAINING_STUDY = "study"
threads = 0

#### WORDS THAT MUST BE REPLACED IN THE JOURNAL FILE ####
J_SEARCH = ("SIM_NUM", "SCDOC")

#### WORDS THAT MUST BE REPLACED IN THE ENSIGHT SCRIPT ####
E_SEARCH = ("PATHTODAT", "PATHTOCAS", "SIM_NUM_SPEED", "SIM_DIRECTORY")

#### USED IN GENERATING EACH PYTHON SCRIPT FROM THE GENERIC ONE
GZ_LIST = [["\\solved-11.11MS.cdat", "\\solved-11.11MS.cas", "-11.11MS"],
           ["\\solved-16.67MS.cdat", "\\solved-16.67MS.cas", "-16.67MS"],
           ["\\solved-22.22MS.cdat", "\\solved-22.22MS.cas", "-22.22MS"]]

SPEEDS = ["\\40KmH", "\\60KmH", "\\80KmH"]
NUM_CASES = 3

#### STORES THE PATH TO EACH GENERATED ENSIGHT SCRIPT
E_SCRIPTS = ["","",""]


#### MULTIPLE SIM ARRAY ####
SIMULATION_QUEUE = []


################################################################################

def main():
    launcher()


################################################################################

def launcher():
    global threads
    threads = multiprocessing.cpu_count()
    init_title()
    menu()

    choice = input()

    if(choice == '1'):
        initialize_sim()
    elif(choice == '2'):
        multiple_sim()
    elif(choice == '3'):
        exit()
    else:
        print("what?")
    #testing

################################################################################

def multiple_sim():
    while(check_space_file() == True):
        for file in os.listdir('.'):
            if file.endswith(".scdoc"):
                ui_multiple_sim(file)
                create_sims(file)
                execute_sims()


def check_space_file():
    scdocs = []
    for file in os.listdir('.'):
        if file.endswith(".scdoc"):
            return True
    return False

################################################################################

def create_sims(file):
    sim_num = file.replace(".scdoc","")
    filepath = sim_directory_setup(sim_num, file)
    choice = input()

    if (choice == 'S'):
        sim = Simulation(sim_num, filepath, 'S')
        path_to_journal = gen_SSJ(sim_num, filepath)
        init_ensight(sim_num, filepath)
        SIMULATION_QUEUE.append(sim)

    elif (choice == 'Y'):
        sim = Simulation(sim_num, filepath, 'Y')
        path_to_journal = gen_SSJ(sim_num, filepath)
        init_ensight(sim_num, filepath)
        SIMULATION_QUEUE.append(sim)

def ui_multiple_sim(file):
    title()
    print("Current queue = [", end = "")

    for i in range(len(SIMULATION_QUEUE)):
        print(SIMULATION_QUEUE[i].get_name(),  end = ",")
        i += 1
    print("]")
    print("\nFILE FOUND: " + file)
    print("            ", end = "")
    for character in file:
        print("¯", end ="")
    print("\nIs this file Straight Line or Yaw? [S/Y]")



################################################################################

def straight_dir():
    print()

def yaw_dir():
    print()

def init_ensight(sim_num, filepath):
    counter = 0
    for gz in GZ_LIST:
        E_SCRIPTS[counter] = ensight_file_setup(sim_num, filepath, gz[0], gz[1], gz[2])
        counter += 1

################################################################################

# sim_directory_setup
# Creates a root directory for the simulation you are going to run.
# Returns the filepath.
def multiple_directory_setup(sim_num, scdoc):
    filepath = os.path.join(FILE_CONTAINING_STUDY, sim_num)
    #If file is not already created
    #TODO: Make program exit if file exists [Avoid overwrites]
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    for speed in SPEEDS:
        os.makedirs(filepath + "\\PostProcessing" + speed)

    Path(scdoc).rename(filepath + "\\" + scdoc)
    return filepath

################################################################################

def initialize_sim():

    scdoc = select_space_file()
    if(scdoc != None):
        sim_num = scdoc.replace(".scdoc","")
        path = sim_directory_setup(sim_num, scdoc)
        path_to_journal = gen_SSJ(sim_num, path)

        ## THIS IS DONE BEFORE OS.CHDIR SO THAT THE PROGRAM DOES NOT
        ## LOSE TRACK OF THE GENERIC PYTHON SCRIPT
        counter = 0
        for gz in GZ_LIST:
            E_SCRIPTS[counter] = ensight_file_setup(sim_num, path, gz[0], gz[1], gz[2])
            counter += 1

        #CD into the new directory
        os.chdir(path)
        print(os.listdir("."))
        run_fluent(sim_num)
        run_ensight_scripts()

        #Print finish after the simulation
        print("FINISHED!")
        input()

    else:
        launcher()

################################################################################

def execute_sims():
    root = os.getcwd()
    for simulation in SIMULATION_QUEUE:
        counter = 0
        for gz in GZ_LIST:
            E_SCRIPTS[counter] = ensight_file_setup(simulation.get_name(),
                                     simulation.get_filepath(), gz[0], gz[1], gz[2])
            counter += 1

        os.chdir(simulation.get_filepath())
        run_fluent(simulation.get_name())
        run_ensight_scripts()
        os.chdir(root)

################################################################################

def run_ensight_scripts():
    try:
        ## FOR EVERY SCRIPT WE JUST MADE, USE IT
        for i in range(NUM_CASES):
            ensight_pp(E_SCRIPTS[i])
            mvFiles(SPEEDS[i])
    except:
        print("Aight, the Ensight post process has failed. This may be\n"
        + "caused by the program pointing to the wrong directory\n"
        + "when accessing Fluent/Ensight. Please check the path.")


def mvFiles(speed):
    try:
        shutil.move(os.getcwd() + "\\db.sqlite3", os.getcwd() + "\\PostProcessing" + speed)
        shutil.move(os.getcwd() + "\\view_report.nexdb", os.getcwd() + "\\PostProcessing" + speed)
        shutil.move(os.getcwd() + "\\media", os.getcwd() + "\\PostProcessing" + speed + "\\")
    except FileNotFoundException:
        print("Could not find one of the Ensight files.")

################################################################################

# sim_directory_setup
# Creates a root directory for the simulation you are going to run.
# Returns the filepath.
def sim_directory_setup(sim_num, scdoc):
    filepath = os.path.join(FILE_CONTAINING_STUDY, sim_num)
    #If file is not already created
    #TODO: Make program exit if file exists [Avoid overwrites]
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    for speed in SPEEDS:
        os.makedirs(filepath + "\\PostProcessing" + speed)

    Path(scdoc).rename(filepath + "\\" + scdoc)
    return filepath

################################################################################

def gen_SSJ(sim_num, file_path):
    replace = (("CAM-"+sim_num), sim_num)
    #Store the path of the journal file
    jrnl_path = file_path + "\\" + sim_num + ".JOU"
    ## FILE CREATION ##
    sim_jrnl = open(jrnl_path, "w+")
    #Open the generic journal
    gen_jrnl = open(STRAIGHT_JRNL_PATH)
    #SEARCH AND REPLACE#
    search_and_replace(J_SEARCH, replace, gen_jrnl, sim_jrnl)
    gen_jrnl.close()
    sim_jrnl.close()



################################################################################

def select_space_file():
    scdocs = []
    for file in os.listdir('.'):
        if file.endswith(".scdoc"):
            scdocs.append(file)

    if(len(scdocs) == 0):
        print("There is no SCDOC file in the fluent directory." +
               " Fluent cant run without a SCDOC." +
                "\nPlease place one in the FluentSim directory.")
        input()
    else:
        space_printer(scdocs, "What scdoc do you wanna use?")
        while True:
            try:
                choice = int(input()) -1
                if (choice >= 0 and choice < len(scdocs)):
                    return scdocs[choice]
                else:
                    space_printer(scdocs, "your input was out of bounds")

            except ValueError:
                space_printer(scdocs,"enter a valid input idiot")
    return None

################################################################################

# space_printer
# This is a ui thing
# I cant remember but it does something
# I remember now its for printing the list of SCDOCS in the local dir
def space_printer(scdocs, print_text):
    title()
    counter = 1
    print(print_text)
    for word in scdocs:
        print("  [" + str(counter) + "] " + word)
        counter += 1

################################################################################

# ensightFileSetup
# IMPORTS: The simulation number, path to root directory, dat and cas locations
# EXPORTS: The location of the new ensight script
# Creates the files required for ensight,
# Does a search and replace on the gen script
def ensight_file_setup(sim_num, path, dat, cas, speed):
    script_path = path + "\\PPScript" + speed + ".py"
    gen_script = open(GEN_ENS_PATH)
    ens_script = open(script_path,"w+")
    root_path = os.getcwd()

    ## REMOVED; REPLACE THE %s with the sim num
    dat_file = dat
    cas_file = cas

    ### location of the sims directory (i.e,"C://Computer/Desktop/Fluent/Study/SS20-5010")
    executable_path = root_path + "\\" + path
    ### dat file relative to its location
    dat_path = executable_path + dat_file
    cas_path = executable_path + cas_file
    sim_num_speed = sim_num + speed
    ens_script_path = root_path + "\\" + script_path

    #SEARCH AND REPLACE#
    replace = (dat_path.replace("\\", r"\\"), cas_path.replace("\\", r"\\"), sim_num_speed, executable_path.replace("\\", r"\\"))
    search_and_replace(E_SEARCH, replace, gen_script, ens_script)

    gen_script.close()
    ens_script.close()
    return ens_script_path

################################################################################

def run_fluent(sim_num):
    print("runnning fluent...")
    command = 'cmd /c ""C:\\Program Files\\ANSYS Inc\\v201\\fluent\\ntbin\\win64\\fluent.exe" 3d -t%s -wait -meshing -i %s"' % (threads, sim_num)
    os.system(command)

################################################################################

#  ensight_pp
#  IMPORTS: Ensight script location
#  EXPORTS: none
#  PURPOSE: To execute ensight with the generated script
def ensight_pp(ens_script_path):
    print("runnning ensight...")
    command = 'cmd /c ""C:\\Program Files (x86)\\CEI\\bin\\ensighticon201.bat" -batch -p %s"' % ens_script_path
    os.system(command)

################################################################################

#  search_and_replace
#  IMPORTS: search (Array), replace (Array), generic file and new file
#  EXPORTS: none
#  PURPOSE: Will iterae through the generic file, searching for the terms given
#           in the search[] array, and replace them with the words in the replace[]
#           array. Also writes to a new file as it goes so the original is unchanged.
def search_and_replace(search, replace, gen_file, new_file):
    #Loop through the generic file, replace words, write to new journal
    for line in gen_file:
        for check, rep in zip(search, replace):
            line = line.replace(check, rep)
        new_file.write(line)

################################################################################

def init_title():
    os.system('cls')
    print()
    count = 0
    for line in title_string:
        for char in line:
            sys.stdout.write(color.OKGREEN + char)
            sys.stdout.flush()
            if(count == 5):
                time.sleep(0.01)
                count = 0
            count += 1
        print()
    print()
    text_scroller(color.ENDC + current_version)
    text = ("Number of cores: %d\n───────────────────" % threads)
    text_scroller(text)



## Just the title
def title():
    os.system('cls')
    print()
    for line in title_string:
        print(color.OKGREEN + line)
    print()
    print(color.ENDC + current_version)
    print("Number of cores: %d\n───────────────────" % threads)
    print()

def text_scroller(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.001)
    print()

def menu():
    print("What would you like to do?")
    print("    1) Run a sim")
    print("    2) Run multiple Sims")
    print("    3) Exit")
    print("")

################################################################################

#  getSimInput
#  IMPORTS: none
#  EXPORTS: sim_num
#  PURPOSE: To get the number of the simulation
#def getSimInput():
#
#    while True:
#        title()
#        print("What is the Study Number for the simulation?")
#        sim_num = input()
#        if len(sim_num) <= 0:
#            print("You didn't enter anything")
#            input()
#        else:
#            #Double check
#            print("You entered: %s \n Is this correct?: [Y/n]" % sim_num)
#            ans = input()
#            if ans.lower()[0] == 'y':
#                return sim_num

title_string =  ["   █████  ██    ██ ████████  ██████   █████  ███████ ██████   ██████ ",
          "  ██   ██ ██    ██    ██    ██    ██ ██   ██ ██      ██   ██ ██    ██",
          "  ███████ ██    ██    ██    ██    ██ ███████ █████   ██████  ██    ██",
          "  ██   ██ ██    ██    ██    ██    ██ ██   ██ ██      ██   ██ ██    ██",
          "  ██   ██  ██████     ██     ██████  ██   ██ ███████ ██   ██  ██████"]

class Simulation:

    name = None
    filepath = None
    type = None

    def __init__(self, name, filepath, type):
        self.name = name
        self.filepath = filepath
        self.type = type

    def get_name(self):
        return self.name

    def get_filepath(self):
        return self.filepath

    def get_type(self):
        return self.type

    def inner_display():
        print("wow")

class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

main()
