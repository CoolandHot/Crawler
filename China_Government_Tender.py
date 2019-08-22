# -*- coding: utf-8 -*-
# 搜集联通、电信、移动 今天-2018/6/1之间中标项目
import urllib
from urllib import request
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

def get_html(html_url, timeout=5, decode='utf-8'):
    MAX_RETRY = 3
    headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    req = request.Request(html_url, headers=headers)
    
    for tries in range(MAX_RETRY):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode(decode)
        except Exception as e:
            continue
    print('已重链接{0}次 url:{1},失败'.format(MAX_RETRY, html_url))
    return None
                
def RegExpt(url):    
    reg1=r'[：\.]?中标(?:（成交）)?供应商名称(?!、)(?:<u>|：)?(.*?)；?<'
    reg2=r'<span>中标金额.*?\s+?((\d+?,?)+\.\d{2}\s+?万?元?)</span>'
    reg3=r'<tr>.*?>总中标金额<.*?>￥((\d+?,?)+\.\d{2,6}\s+?万?元?).*?</tr>'
    reg4=r'<tr>\s+<td>1<\/td>\s+<td>(.*?公司)<\/td>'
    imgre1 = re.compile(reg1)
    imgre2 = re.compile(reg2)
    imgre3 = re.compile(reg3)
    imgre4 = re.compile(reg4)
    html=get_html(url)
    if not html is None:
        try:
            brand= re.search(imgre1, str(html)).group(1)
            brand=brand.replace('&nbsp;','')
        except:
            try:
                brand= re.search(imgre4, str(html)).group(1)
            except:
                brand=None
        try:
            budget= re.search(imgre2, str(html)).group(1)
            budget=budget.replace('\r','').replace('\n','').replace('\t','').replace(' ','')
        except:
            try:
                budget= re.search(imgre3, str(html)).group(1)
            except:
                budget=None
        return brand,budget
    else:
        return None,None

def writeInfile(read_f_path,error_f_path):
    ChinaTelecom = open("ChinaTelecom.txt","a",encoding='utf-8')
    error_url=open(error_f_path,"a",encoding='utf-8')
    match_error=open("RegError.txt","a",encoding='utf-8')
    with open(read_f_path,"r",encoding='utf-8') as data_name:
        line_data=data_name.readlines()
        for line in line_data:
            regX=r'^(\d{4}\.\d{2}\.\d{2})\d{2}\:\d{2}\:\d{2}\|采购人：(.+)\|代理机构：(.+)\|(.+)\|(http.+)$'
            imgreX = re.compile(regX)
            try:
                match_all=re.search(imgreX, line).groups()
            except:
                print(line,file=match_error)
                continue
            if match_all:
                line_date=match_all[0]
                line_instructor=match_all[1]
                line_agent=match_all[2]
                line_title=match_all[3]
                line_href=match_all[4]
                brand,budget=RegExpt(line_href)
                print(line_date)
                if (brand is None) and (budget is None):
                    print(line,file=error_url)
                else:
                    print(line_date,line_title,brand,budget,line_href,sep="|", file=ChinaTelecom)
    error_url.close()
    ChinaTelecom.close()
    match_error.close()
    return

def getRow(browser):
    data_list=[]
    publish_time=browser.find_elements_by_css_selector('ul.vT-srch-result-list-bid > li > span')
    projects=browser.find_elements_by_css_selector('ul.vT-srch-result-list-bid > li > a')
    for T,P in zip(publish_time,projects):
        pro_href=P.get_attribute("href")
        pro_title=P.text
        data_list.append([T.text.replace('\r','').replace('\n','').replace('\t','').replace(' ','').replace("中标公告|广东|",''),pro_title,pro_href])
    return data_list

def tempfile(all_file,datalist,pagenum,totalpage):
    print("第",pagenum,"/",totalpage,"页")
    for data in datalist:
        if ("废标公告" in data[1]) or ("失败公告" in data[1]) or ("终止公告" in data[1]):
            continue
        print(data[0],data[1],data[2],sep="|", file=all_file)
    return
    
def getData(url,path,start_page=1,lastPage=0):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # 不加载图片,加快访问速度
    browser = webdriver.Chrome(executable_path=path,options=options)
    # browser.set_page_load_timeout(10)
    pre_url='http://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index='
    browser.get(pre_url+str(start_page)+url)
    wait = WebDriverWait(browser, 10)
    #获取最后页码
    if lastPage==0:
        try:
            lastPage=wait.until(EC.presence_of_element_located((By.XPATH,"//p[@class='pager']/a[last()-1]"))).text
            lastPage=int(lastPage)
        except:
            lastPage=1
    all_file = open("China_Government_Bids.txt","a",encoding='utf-8')
    for i in range(start_page,lastPage+1):
        datalist=getRow(browser)
        tempfile(all_file,datalist,i,lastPage)
        try:
            browser.find_element_by_xpath("//p[@class='pager']/a[last()]").click()
        except:
            pass
    browser.quit()
    all_file.close()
    print("汇总页爬虫完毕")
    return

# 主程序
if __name__=="__main__":
    if os.path.exists("China_Government_Bids.txt"):
        read_f_path="China_Government_Bids.txt"
        error_f_path="Error_URL_0.txt"
        writeInfile(read_f_path,error_f_path)
    else:
        path=r"D:\Program files\Cent Browser\chromedriver_2.46.exe"
        # bidType=1
        bidType=7
        start_time="2019:07:31"
        end_time="2019:08:01"
        start_page=1
        keywords="中国联合网络通信"        
        url1='&bidSort=0&buyerName=&projectId=&pinMu=0&bidType='+str(bidType)+'&dbselect=bidx&kw='+keywords+'&start_time='+start_time+'&end_time='+end_time+'&timeType=6&displayZone=广东省&zoneId=44+not+4403&pppStatus=0&agentName='
        keywords="联通系统集成有限公司"        
        url2='&bidSort=0&buyerName=&projectId=&pinMu=0&bidType='+str(bidType)+'&dbselect=bidx&kw='+keywords+'&start_time='+start_time+'&end_time='+end_time+'&timeType=6&displayZone=广东省&zoneId=44+not+4403&pppStatus=0&agentName='
        keywords="中国电信股份有限公司"       
        url3='&bidSort=0&buyerName=&projectId=&pinMu=0&bidType='+str(bidType)+'&dbselect=bidx&kw='+keywords+'&start_time='+start_time+'&end_time='+end_time+'&timeType=6&displayZone=广东省&zoneId=44+not+4403&pppStatus=0&agentName='
        keywords="中国移动通信集团"      
        url4='&bidSort=0&buyerName=&projectId=&pinMu=0&bidType='+str(bidType)+'&dbselect=bidx&kw='+keywords+'&start_time='+start_time+'&end_time='+end_time+'&timeType=6&displayZone=广东省&zoneId=44+not+4403&pppStatus=0&agentName='
        keywords="广东省广播电视网络"        
        url5='&bidSort=0&buyerName=&projectId=&pinMu=0&bidType='+str(bidType)+'&dbselect=bidx&kw='+keywords+'&start_time='+start_time+'&end_time='+end_time+'&timeType=6&displayZone=广东省&zoneId=44+not+4403&pppStatus=0&agentName='
        getData(url1,path,start_page)
        getData(url2,path,start_page)
        getData(url3,path,start_page)
        getData(url4,path,start_page)
        getData(url5,path,start_page)
        
    print("爬虫完成")
    