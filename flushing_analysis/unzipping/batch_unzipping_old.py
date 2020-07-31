#batch unzipping
import zipfile, os, datetime, shutil, platform
from zipfile import ZipFile

#global variables
path = os.getcwd()  #finds path to current directory
now = str(datetime.datetime.now())#gets the current date and time
#slash control for windows(\\) vs linux(/)
slash = ''
if platform.system() == "Linux":
    slash = '/'
elif platform.system() == "Windows":
    slash = '\\'

#creates a new folder - this folder is temporary
def new_folder():
    #makes new directory for unzipped files
    try:
        os.mkdir(path + slash + now)
    except OSError:
        print ("Creation of the directory %s failed" % path)

#creates the final folder
def final_folder():
    #makes new directory for unzipped files
    try:
        os.mkdir(path + slash + now +'_final')
    except OSError:
        print ("Creation of the directory %s failed" % path)

#unzips folder
def unzip_folders():
    folders = os.listdir(path)
    folders.sort()
    for folder_name in folders:
        if folder_name.endswith('.zip'):
            zip_ref = zipfile.ZipFile(path + slash + folder_name, 'r')
            zip_ref.extractall(path + slash + now)
            unzip_files()

#unzip files
def unzip_files():
    new_folders = os.listdir(path + slash + now)
    new_folders.sort()
    for new_folder in new_folders:
        files = os.listdir(path + slash + now)
        files.sort()
        for one_file in files:
            if one_file.endswith("Playback.zip"):
                zip_ref = zipfile.ZipFile(path + slash + now + slash + one_file, 'r')
                zip_ref.extractall(path + slash + now +'_final')
                zip_ref.close()

#controls the run capabilities of r.bat
def run_controller():
    new_plbs = os.listdir(path + slash + now +'_final')
    new_plbs.sort()
    for new_plb in new_plbs:
        if new_plb.endswith(".plb"):
            print(path)
            cmd1 = "cd " + path
            cmd2 = 'r ' + new_plb
            os.system(cmd1)
            os.system(cmd2)

#deletes in-between folder
def delete_folder():
    shutil.rmtree(path + slash + now)

#runs the program in proper order
def unzip():
    #unzips all the zipped files
    new_folder()#creates a new, empty folder
    unzip_folders()#unzips the currently zipped folders into the empty folder AND unzips the files into the final folder
    final_folder()#creates the final folder named : date + "final"
    delete_folder()#deletes the in-between folder
    run_controller()#runs the r.bat for conversion

#main run
unzip()

#new_folder()#creates a new, empty folder
#unzip_folders()#unzips the currently zipped folders into the empty folder
#final_folder()#creates the final folder named : date + "final"
#unzip_files()#unzips the files into the final folder
#delete_folder()#deletes the in-between folder
#run_controller()#runs the r.bat for conversion
