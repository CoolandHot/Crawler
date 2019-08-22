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
# import pdb

def get_html(html_url, timeout=20, decode='utf-8'):
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
    reg1=r'：?(?:中标|成交)供应商名称：?(?:<u>)?(.*?)<'
    reg2=r'<span>中标金额.*?\s+?((\d+?,?)+\.\d{2}\s+?万?元?)</span>'
    reg3=r'<tr>\s+<td>1</td>\s+<td>(.*?公司)</td>'
    reg4=r'&gt;废标/终止公告</div>'
    reg5=r'中标、成交(?:社会资本|标的)名称：(.*?公司)'
    imgre4 = re.compile(reg4)
    imgre1 = re.compile(reg1)
    imgre2 = re.compile(reg2)    
    imgre3 = re.compile(reg3)
    imgre5 = re.compile(reg5)
    html=get_html(url)
    if not html is None:
        try:
            brand= re.search(imgre1, str(html)).group(1)
            brand=brand.replace('&nbsp;','')
        except:
            try:
                brand= re.search(imgre3, str(html)).group(1)
            except:
                try:
                    brand= re.search(imgre5, str(html)).group(1)
                except:
                    try:
                        brand= re.search(imgre4, html).group()
                        brand="Abandon"
                    except:
                        brand=None
        try:
            budget= re.search(imgre2, str(html)).group(1)
            budget=budget.replace('\r\n','').replace('\t','').replace(' ','')
        except:
            budget=None
        return brand,budget
    else:
        return None,None
def tempfile(all_file,datalist,pagenum,totalpage):
    print("第",pagenum,"/",totalpage,"页")
    for data in datalist:
        if ("废标公告" in data[2]) or ("失败公告" in data[2]) or ("终止招标公告" in data[2]) or ("终止公告" in data[2]) or ("中止公告" in data[2]) or ("调整公告" in data[2]):
            continue
        print(data[0],data[1],data[2],data[3],sep="|", file=all_file)
    return
def writeInfile(read_f_path,error_f_path):
    Non_Telecom = open("Non_Telecom.txt","a",encoding='utf-8')
    ChinaTelecom = open("ChinaTelecom.txt","a",encoding='utf-8')
    error_url=open(error_f_path,"a",encoding='utf-8')
    match_error=open("RegError.txt","a",encoding='utf-8')
    with open(read_f_path,"r",encoding='utf-8') as data_name:
        line_data=data_name.readlines()
        for line in line_data:
            regX=r'^(\d+.*?)\|(\S+?)\|(\S+?)\|(http\S+)$'
            imgreX = re.compile(regX)
            try:
                match_all=re.search(imgreX, line).groups()
            except:
                print(line,file=match_error)
                continue
            if match_all:
                line_date=match_all[0]
                line_district=match_all[1]
                line_title=match_all[2]
                line_href=match_all[3]
                brand,budget=RegExpt(line_href)
                print(line_date)
                if brand is None:
                    print(line,file=error_url)
                elif brand=="Abandon":
                    continue
                elif ("中国联合网络通信" in brand) or ("中国电信股份有限公司" in brand) or ("中国移动通信集团" in brand) or ("中国广播电视网络" in brand) or ("联通系统集成有限公司" in brand):
                    print(line_date,line_title,brand,budget,line_href,sep="|", file=ChinaTelecom)
                else:
                    print(line_date,line_title,brand,budget,line_href,sep="|", file=Non_Telecom)
    error_url.close()
    ChinaTelecom.close()
    Non_Telecom.close()
    match_error.close()
    return

def getRow(browser):
    data_list=[]
    publish_time=browser.find_elements_by_css_selector('ul.m_m_c_list > li > em')
    district=browser.find_elements_by_css_selector('ul.m_m_c_list > li > span > a')
    projects=browser.find_elements_by_css_selector('ul.m_m_c_list > li > a')
    for T,D,P in zip(publish_time,district,projects):
        pro_href=P.get_attribute("href")
        pro_title=P.get_attribute("title")
        data_list.append([T.text,D.text,pro_title.replace('\t','').replace(' ',''),pro_href])
    return data_list
    
def checksite(wait,browser,url,run=0):
    count_get=0
    while True:
        if run==1:
            time.sleep(2)
            browser.get(url)
            region_all="selectSite('-1');" #选中全部地区
            browser.execute_script(region_all)
            date_range=wait.until(EC.presence_of_element_located((By.XPATH,"//input[@name='operateDateFrom']")))
            date_range.clear()
            date_range.send_keys(start_date)
            date_range=wait.until(EC.presence_of_element_located((By.XPATH,"//input[@name='operateDateTo']")))
            date_range.clear()
            date_range.send_keys(end_date)
            onSearch="onSearch();"
            browser.execute_script(onSearch)
            run=1
            count_get+=1
        try:
            infobar=browser.find_elements_by_css_selector('div.n_m_wei > span')[0].text
            if infobar=="信息公告":
                break
        except:
            pass            
    if count_get>0:
        return True
    else:
        return False
def getData(url,path,start_date,end_date,start_page=1,lastPage=0):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # 不加载图片,加快访问速度
    browser = webdriver.Chrome(executable_path=path,options=options)
    # browser.set_page_load_timeout(10)
    browser.get(url)
    wait = WebDriverWait(browser, 10)
    checksite(wait,browser,url,1)
    #获取最后页码
    if lastPage==0:
        try:
            lastPage=wait.until(EC.presence_of_element_located((By.XPATH,"//form[@name='qPageForm']/a[last()-3]/span"))).text
            lastPage=int(lastPage)
        except:
            lastPage=1
    all_file = open("Canton_Government_Bids.txt","a",encoding='utf-8')
    if start_page!=1:
        textbox=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#pointPageIndexId")))
        textbox.clear()
        textbox.send_keys(start_page)
        browser.find_element_by_xpath("//form[@name='qPageForm']/a[last()]/span").click()
    for i in range(start_page,lastPage+1):
        if checksite(wait,browser,url):
            textbox=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#pointPageIndexId")))
            textbox.clear()
            textbox.send_keys(i)
            browser.find_element_by_xpath("//form[@name='qPageForm']/a[last()]/span").click()
        datalist=getRow(browser)
        tempfile(all_file,datalist,i,lastPage)
        try:
            browser.find_element_by_xpath("//form[@name='qPageForm']/a[last()-2]/span").click()
        except:
            pass
    browser.quit()
    all_file.close()
    return

# 主程序
if __name__=="__main__":
    if not os.path.exists("Canton_Government_Bids.txt"):
        url = 'http://www.gdgpo.gov.cn/queryMoreInfoList/channelCode/0008.html'
        path=r"D:\Program files\Cent Browser\chromedriver_2.46.exe"
        start_page=1        
        start_date="2019-07-11"
        end_date="2019-08-01"
        getData(url,path,start_date,end_date,start_page)
    read_f_path="Canton_Government_Bids.txt"
    error_f_path="Error_URL_0.txt"
    writeInfile(read_f_path,error_f_path)
    print("爬虫完成")
    