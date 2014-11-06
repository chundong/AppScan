#encoding=utf-8
__author__ = 'chundonghu'

import os
from zipfile  import ZipFile
import json

from biplist import *
import sys
from lxml import etree
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'usage: AppScan directionray %s' %(sys.argv)
        sys.exit(1)

    ipaInfos = []

    applicationPath = sys.argv[1]
    print sys.argv[1]

    for root,foldername, filenames  in os.walk(applicationPath):

        for filename in filenames:

            if filename.endswith('.ipa'):
                ipaInfo = {}
                ipaInfo['nib'] = False
                ipaInfo['storyboard'] = False
                zipPath = '%s/%s' % (root,filename)

                ipaFile =  ZipFile(zipPath)

                for zFileInfo in ipaFile.infolist():
                    if zFileInfo.filename.endswith('.app/Info.plist'):
                        targetPath = '%s' % (ipaFile.extract(zFileInfo,'/tmp'))

                        plistData =readPlist(open(targetPath))
                        exeFile = plistData['CFBundleExecutable']
                        ipaFile.extract(zFileInfo.filename.replace('Info.plist',exeFile),'/tmp')
                        cmd = 'nm /tmp/%s' %(zFileInfo.filename.replace('Info.plist',exeFile))
                        # print cmd
                        cmdResult = os.popen(cmd)
                        # print cmdResult
                        allines = cmdResult.readlines();
                        # todo
                        # for line in allines:

                        # break;
                        if plistData.has_key('CFBundleDisplayName'):
                            ipaInfo["name"] = plistData['CFBundleDisplayName']
                        else:
                            if plistData.has_key('CFBundleName'):
                                ipaInfo["name"] = plistData['CFBundleName']
                            else:
                                print 'no CFBundleName'
                        if plistData.has_key('CFBundleURLTypes') and len (plistData['CFBundleURLTypes']) > 0:
                            if plistData['CFBundleURLTypes'][0].has_key('CFBundleURLSchemes') :
                                if  len(plistData['CFBundleURLTypes'][0]['CFBundleURLSchemes'])  > 0:
                                    ipaInfo['url'] ='%s%s' %('',plistData['CFBundleURLTypes'][0]['CFBundleURLSchemes'][0])
                                else:
                                    ipaInfo['url'] = '%s%s' %('',plistData['CFBundleURLTypes'][0]['CFBundleURLSchemes'])
                    elif zFileInfo.filename.endswith('/InfoPlist.strings'):
                    # print 'info plist strings %s' %(zFileInfo.filename)
                        try:
                            targetPath = '%s' % (ipaFile.extract(zFileInfo,'/tmp'))
                            plistData =readPlist(open(targetPath))
                            if plistData.has_key('CFBundleName'):
                                ipaInfo["name"] = plistData['CFBundleName']
                        except:
                            print 'error : %s  %s path = %s' %(zFileInfo.filename,sys.exc_value,targetPath)
                    elif zFileInfo.filename.endswith('/Main.strings'):
                        try:
                            targetPath = '%s' % (ipaFile.extract(zFileInfo,'/tmp'))
                            plistData =readPlist(open(targetPath))
                        except:
                            print 'error : %s  %s path = %s' %(zFileInfo.filename,sys.exc_value,targetPath)
                    elif zFileInfo.filename.endswith('.nib'):
                        ipaInfo['nib'] = True

                    elif zFileInfo.filename.endswith('.storyboard'):
                        ipaInfo['storyboard'] = True

                ipaInfos.append(ipaInfo)

    # s = '['
    html = etree.Element("html")
    body = etree.Element("body")
    html.append(body)

    for ipaInfo in ipaInfos:
        div = etree.Element('div')
        appName = etree.Element('h1')
        appName.text = u'app name: %s' %(ipaInfo['name'])

        div.append(appName)
        if ipaInfo.has_key('url'):
            schema = etree.Element('div')
            schema.text = 'schema: %s' %(ipaInfo['url'])
            div.append(schema)
        if ipaInfo.has_key('nib'):
            nib = etree.Element('div')
            nib.text = 'use Nib : %s ' %( ipaInfo['nib'])
            div.append(nib)
        if ipaInfo.has_key('storyboard'):
            nib = etree.Element('div')
            nib.text = 'storyboard : %s ' %( ipaInfo['storyboard'])
            div.append(nib)
        body.append(div)

            # s = '%s{"name": "%s","url":"%s"},' %(s,ipaInfo['name'],ipaInfo['url'])
#         print 'name = %s url = huniu://%s' %(ipaInfo['name'],ipaInfo['url'])

    # s = '%s ]' %( s)

    print etree.tostring(html)
