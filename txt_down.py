import requests
from bs4 import BeautifulSoup

def getHtml(url):
    #获取网页数据
    html = requests.get(url)
    htmlCode = html.text
    #解析网页
    soup = BeautifulSoup(htmlCode,'html.parser')
    #返回解析后的页面内容
    return soup

def getTitle(url):
    soup = getHtml(url)
    title = soup.find('div',class_="book_info").find('h1').string
    return title

#获取各章节目录链接
def getList(url):
    soup = getHtml(url)
    #查找所有章节的链接
    if soup is None:
        return
    listBox = soup.find('div', class_="book_list").find_all('a')
    #新建列表用来储存list的url
    bookLists = []
    for i in listBox:
        listUrl = i['href']
        #放进列表里
        bookLists.append(listUrl)
    return bookLists

#获取各章节正文
def getNovelContent(url):
    soup = getHtml(url)
    #获得需要的正文内容
    content = soup.find('div', class_="contentbox").text
    content = content.strip()
    #这个地方我处理的有点粗糙了，需要根据正式情况来用
    contentCut = content.replace("本章未完，点击[ 下一页 ]继续阅读-->>","").replace("本章有错误，我要提交上一章 返回目录 下一章","").replace("小提示：按 回车[Enter]键 返回书目，按 ←键 返回上一页， 按 →键 进入下一页。","")
    return contentCut

#保存到本地
def saveNovel(url):
    bookLists = getList(url)
    title = getTitle(url)
    num = 1
    with open('%s.txt'%title, 'a' ,encoding='utf-8') as f:
        for listUrl in bookLists:
            #拼接完整的章节链接地址
            chapterUrl = url + listUrl
            chapterContent = getNovelContent(chapterUrl)
            f.write(chapterContent)
            print('***第{}章下载完成***'.format(num))
            num += 1

        f.close()

if __name__ == '__main__':
    url='http://www.moyanxsw.com/binbianbushihaitanghong/'
    saveNovel(url)
