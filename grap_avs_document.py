import urllib.request as ur
from lxml import etree
import html2text as h2m
import re


testSite="https://developer.amazon.com/docs/alexa-voice-service/api-overview.html"
# testSite="https://developer.amazon.com/docs/alexa-voice-service/speechrecognizer.html"
# testSite="https://developer.amazon.com/docs/alexa-voice-service/complicated/speechrecognizer.html"
# SITE="http://www.baidu.com"




def isAVSLink( url ):
    if re.match( ".*/docs/alexa-voice-service.*\.html", url  ):
        return True
    else:
        return False

def getAVSBaseUrl( url ):
    if url.find( '/docs/alexa-voice-service' ) == 0:
        url = 'https://developer.amazon.com' + url
    matchs = re.match( "(https://developer.amazon.com/docs/alexa-voice-service.*.html).*", url )
    if matchs:
        return matchs.group( 1 )
    else:
        return False

def getFileNameFromUrl( url ):
    match = re.match( '(https://developer.amazon.com/docs/alexa-voice-service)/([\w/-]+).html#?(.*)', url )
    if match :
        if len( match.groups() ) >= 2:
            fileNameOringinStr = match.group(2)
            if fileNameOringinStr != "":
                fileName = fileNameOringinStr.replace( '/', '_' )
                return fileName+'.md'
    return False

def findMainColumn( elem ):
    if len( elem ) == 0 :
        return False
    for i in range( len(elem) ):
        # print( "tag --> ", elem[i].tag, " class --> ", elem[i].get( 'class' ) )
        if elem[i].get( 'class' ) == "mainColumn":
            print( "tag --> ", elem[i].tag, " class --> ", elem[i].get( 'class' ) )
            return elem[i]
        else:
            target = findMainColumn( elem[i] )
            if target != False :
                return target
    return False

def getSiteMainColumnHtmlEtree( url ):
    htmlObj = ur.urlopen( url )
    htmlContent = htmlObj.read().decode( 'utf-8' )
    if not htmlContent:
        return False
    # print( htmlContent )
    htmlTree = etree.HTML( htmlContent )
    # etree.dump( htmlTree )
    # for i in range( len( htmlTree[1] ) ):
    #     print( "--> ", i )
    #     print( htmlTree[1][i].tag )
    #     print( htmlTree[1][i].get( 'class' ) )
    return findMainColumn( htmlTree )

def turnHtml2MarkdownAndSave2File( htmlStrUtf8, fileName ):
    markdownContent = h2m.html2text( htmlStrUtf8 )
    if not markdownContent :
        print( "html trun markdown failed" )
        return False
    f = open( fileName, 'w' )
    if not f :
        print( "file {} cant open" .format( fileName ) )
        return False
    f.write( markdownContent )
    f.close

STD_SEARCH_NONEED = [ 'code', 'pre', 'strong', 'br', 'hr' ]
def grabUrlsFromEtree( elem, grabAVSLinks ):
    if len( elem ) == 0:
        return grabAVSLinks
    for i in range( len(elem) ):
        if elem[i].tag == "a":
            href = elem[i].get("href")
            # print( href )
            if href and isAVSLink( href ):
                url = getAVSBaseUrl( href )
                # print( url )
                if url:
                    grabAVSLinks.append( url )
        else:
            if elem[i].tag not in STD_SEARCH_NONEED:
                grabAVSLinks = grabUrlsFromEtree( elem[i], grabAVSLinks )
    return grabAVSLinks

def grapAVSwebsite( url, grabedList ):
    # 匹配看是否是 AVS 的文档
    print( "--->1" )
    if not isAVSLink( url ):
        return grabedList

    print( "--->2" )
    # 提取文件名
    fileName = getFileNameFromUrl( url )
    if fileName == False:
        return grabedList

    print( "--->3" )
    # 提取 mainColumn 存档
    mainColumnEtree = getSiteMainColumnHtmlEtree( url )
    if mainColumnEtree == False:
        return grabedList

    print( "--->4" )
    # turn html 2 markdown
    mainColumnHtmlStrUtf8 = etree.tostring( mainColumnEtree, pretty_print=True ).decode( 'utf-8' )
    turnHtml2MarkdownAndSave2File( mainColumnHtmlStrUtf8, fileName )
    grabedList.append( url )

    print( "--->5" )
    # 提取 mainColumn 中 AVS url
    grabAVSLinks = grabUrlsFromEtree( mainColumnEtree, grabAVSLinks=[] )

    print( "--->6" )
    # 判断该 Url 是否存在已经抓取的数据表中，如果存在则 pass 如果不存在则抓取
    count = 0
    for u in grabAVSLinks:
        if u not in grabedList:
            print( u )
            grabedList = grapAVSwebsite( u, grabedList )
            count += 1

    return grabedList


grabedList = grapAVSwebsite( testSite, grabedList=[] )
# print( getFileNameFromUrl( testSite ) )
exit()

'''
target = findMainColumn( htmlTree )
if target != False:
    print("find")
    # etree.dump( target )
    mainColumnContentHtmlStr = etree.tostring( target, pretty_print=True ).decode( "utf-8" )
    mainColumnContentMarkdown = h2m.html2text( mainColumnContentHtmlStr )
    f = open( "/tmp/test.html", "w" )
    f.write( mainColumnContentMarkdown )
    f.close()
else:
    print( "not find" )
'''


