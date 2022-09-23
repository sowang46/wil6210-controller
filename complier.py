import os
import py_compile
from subprocess import call
from shutil import copyfile
from src import version
import zipfile

dir_path = 'src'
compiled_path = '../build'
#airfide_buildtool = '~/tool/buildroot-2018.02/output/host'
airfide_buildtool = '/home/song/tool/output/host'

os.chdir(dir_path)

if not os.path.isdir(compiled_path):
    os.makedirs(compiled_path)

for root, directories, filenames in os.walk('./'):
    cur_path = compiled_path+"/"+root
    for directory in directories:
        if not os.path.isdir(os.path.join(cur_path, directory)):
            os.makedirs(os.path.join(cur_path, directory))
    for filename in filenames:
        if os.path.splitext(filename)[-1] == '.py':
            py_compile.compile(os.path.join(root, filename), 
                               cfile=os.path.join(cur_path, filename+"c"))
        elif os.path.splitext(filename)[-1] == '.c':
            target_file = os.path.splitext(filename)[0]+'_x86_64.so'
            
            call(["gcc", "-pthread", "-fPIC", "-shared",
                  "-I/usr/include/python2.7", 
                  os.path.join(root, filename),
                  "-o",
                  os.path.join(cur_path, target_file)])
            
            target_file = os.path.splitext(filename)[0]+'_armv7l.so'
            # https://launchpad.net/ubuntu/xenial/armhf/libpython2.7-dev/2.7.11-7ubuntu1
            
            call([airfide_buildtool+"/bin/arm-buildroot-linux-uclibcgnueabihf-gcc", 
                  "-pthread", "-fPIC", "-shared", "-mfloat-abi=hard",
                  "-I./includes", 
                  "-I./include/python2.7", 
                  "-I"+airfide_buildtool+"/include",
                  "-L"+airfide_buildtool+"/lib",
                  os.path.join(root, filename),
                  "-o",
                  os.path.join(cur_path, target_file)])
        else:
            copyfile(os.path.join(root, filename), os.path.join(cur_path, filename))

call(["mv", compiled_path+"/server.pyc", compiled_path+"/__main__.pyc"])

inpwd = os.getcwd()
os.chdir(compiled_path)
call(["zip", "-rq0", "../server_standalone.zip", "./"])
os.chdir(inpwd)
            
with open("../server_standalone.zip", 'r+') as f:
    content = f.read()
    f.seek(0, 0)
    f.write("#!/usr/bin/env python\n"+content)
call(["mv", "../server_standalone.zip", "../bin/wil6210_server-"+version.version])
call(["rm", "-rf", compiled_path])
    
