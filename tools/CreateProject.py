#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
NAME
    CreateProject --

SYNOPSIS
    CreateProject [-h]

    -h show help
    -p package name
    -o output dir
    -l set screen orientation to landscape, default if portrait.
"""

import os
import sys
import getopt
import shutil
import re
import glob

scriptRoot = os.path.split(os.path.realpath(__file__))[0]
engineRoot = os.path.split(scriptRoot)[0]
replacementDict = {}

def joinDir(root, *dirs):
    for item in dirs:
        root = os.path.join(root, item)
    return root

def checkStringValid(string):
    if re.match('^[0-9a-z]+$', string):
        return True
    else:
        return False

def initDict(names, isLandscape):
    packageName = (".").join(names)
    lastName = names[2]

    replacementDict["__PROJECT_PACKAGE_FULL_NAME__"] = packageName
    replacementDict["__PROJECT_COCOS_NAME__"] = lastName
    if isLandscape:
        replacementDict["__SCREEN_ISLANDSCAPE__"] = "true"
        replacementDict["__SCREEN_WIDTH__"] = "960"
        replacementDict["__SCREEN_HEIGHT__"] = "640"
        replacementDict["__SCREEN_ORIENTATION_IOS5__"] = "UIInterfaceOrientationIsLandscape"
        replacementDict["__SCREEN_ORIENTATION_IOS6__"] = "UIInterfaceOrientationMaskLandscape"
        replacementDict["__SCREEN_ORIENTATION_ANDROID__"] = "sensorLandscape"
    else:
        replacementDict["__SCREEN_ISLANDSCAPE__"] = "false"
        replacementDict["__SCREEN_WIDTH__"] = "640"
        replacementDict["__SCREEN_HEIGHT__"] = "960"
        replacementDict["__SCREEN_ORIENTATION_IOS5__"] = "UIInterfaceOrientationIsPortrait"
        replacementDict["__SCREEN_ORIENTATION_IOS6__"] = "UIInterfaceOrientationMaskPortraitUpsideDown"
        replacementDict["__SCREEN_ORIENTATION_ANDROID__"] = "portrait"

def stringReplace(s):
    for key in replacementDict:
        s = re.sub(key, replacementDict[key], s)
    return s

def checkPackageName(packageName):
    print "====> Checking packageName validity."
    packageName = packageName.lower()
    arr =  packageName.split(".")
    if len(arr) != 3:
        print "Error: packageName must be composed of three sections connected by points"
        sys.exit(-2)
    for item in arr:
        if not checkStringValid(item):
            print "Error: %s must be composed of English characters(a~z) and number(0~9)" %(item)
            sys.exit(-2)
    print "====> PackageName is valid."
    return arr

def createRootPath(outputDir):
    if os.path.exists(outputDir):
        print "Error: %s is already exist" %(outputDir)
        sys.exit(-2)
    os.mkdir(outputDir)
    if not os.path.exists(outputDir):
        print "Error: create %s fail" %(outputDir)
        sys.exit(-2)

def copyFile(src, dest):
    buff = ""
    inFp = open(src, 'rb')
    for line in inFp.readlines(): 
        line = stringReplace(line)
        buff += line
    inFp.close()

    outFp = open(dest, 'wb')
    outFp.write(buff)
    outFp.close()

def copyDir(src, dest):
    for item in os.listdir(src):
        if "." == item[0]: # ignore hidden files
            continue

        nSrc = joinDir(src, item)
        item = stringReplace(item)
        nDest = joinDir(dest, item)
        if os.path.isfile(nSrc):
            copyFile(nSrc, nDest)
        else:
            if not os.path.exists(nDest):
                os.mkdir(nDest)
            copyDir(nSrc, nDest)

def replaceFileContent(filePath, replaceItems):
    fileContent = None
    with open(filePath) as f:
        fileContent = f.read()

    for old, new in replaceItems.items():
        fileContent = fileContent.replace(old, new)

    with open(filePath, "w") as f:
        f.write(fileContent)


def createProject(packageName, outputDir, isLandscape, needCopyCocos2d):
    names = checkPackageName(packageName)
    lastName = names[2]
    initDict(names, isLandscape)

    templateRoot = joinDir(engineRoot, "templates", "lua-template-default")
    outputDir = joinDir(outputDir, lastName)

    print "====> Copying template."
    createRootPath(outputDir)
    copyDir(templateRoot, outputDir)
    print "====> Copying cocos."
    shutil.copytree(joinDir(engineRoot, "cocos", "scripting", "lua-bindings", "script"), joinDir(outputDir, "src", "cocos"))

    if needCopyCocos2d:
        print "====> Copying cocos sources."
        os.mkdir(joinDir(outputDir, "frameworks", "cocos2d-x"))
        for dirName in ["cmake", "cocos", "extensions", "external", "licenses"]:
            shutil.copytree(joinDir(engineRoot, dirName), joinDir(outputDir, "frameworks", "cocos2d-x", dirName))
        for fileName in ["CHANGELOG", "CMakeLists.txt", "install-deps-linux.sh", "README.md"]:
            copyFile(joinDir(engineRoot, fileName), joinDir(outputDir, "frameworks", "cocos2d-x", fileName))
        copyFile(joinDir(engineRoot, "cocos", "scripting", "lua-bindings", "manual", "lua_module_register.h"), joinDir(outputDir, "frameworks", "runtime-src", "Classes", "lua_module_register.h"))
    print "====> Done."

if __name__ == "__main__":
    # ===== parse args =====
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:o:l")
    except getopt.GetoptError:
        # print help information and exit:
        print __doc__
        sys.exit(-2)

    packageName = ""
    outputDir = ""
    isLandscape = False
    needCopyCocos2d = True
    for o, a in opts:
        if o == "-h":
            # print help information and exit:
            print __doc__
            sys.exit(0)
        if o == "-p":
            packageName = a
        if o == "-o":
            outputDir = a
        if o == "-l":
            isLandscape = True

    if len(packageName) == 0:
        print "Error: use -p xxx.xxx.xxx to set package name"
        sys.exit(-2)
    if len(outputDir) == 0:
        print "Error: use -o /path/path/ to set output dir"
        sys.exit(-2)

    # info printing
    print "== engineRoot: %s" %(engineRoot)
    createProject(packageName, outputDir, isLandscape, needCopyCocos2d)
