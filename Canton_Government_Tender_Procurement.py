# -*- coding: utf-8 -*-
import urllib
from urllib import request
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

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
    reg1 = r'<span>预算金额.*?\s+?((\d+?,?)+\.\d{2}\s+?万?元?)</span>'
    reg2=r'<div class="zw_c_c_title">(.*?)</div>'
    imgre1 = re.compile(reg1)
    imgre2=re.compile(reg2)
    html=get_html(url)
    if not html is None:
        try:
            budget= re.search(imgre1, str(html)).group(1)
            budget=budget.replace('\r\n','').replace('\t','').replace(' ','')
        except:
            budget=None
        try:
            title= re.search(imgre2, str(html)).group(1)
        except:
            title=None        
        return budget,title
    else:
        return None,None
    
def writeInfile(data_name):
    myfile = open("Canton_Government_Bids.txt","a",encoding='utf-8')
    error_url=open("Error_URL_0.txt","a",encoding='utf-8')
    # date_to_print=datetime.today().strftime('%m-%d')
    # print("%s发布时间|地区|%s汇总标题|详细页标题|预算|网址" %(date_to_print,date_to_print),file=myfile)
    for data in data_name:
        budget,title=RegExpt(data[3])
        if title is None:
            print(data[3],file=error_url)
        print("采购公告",data[0]," ",title,budget,data[3],sep="|", file=myfile)
    myfile.close()
    error_url.close()
    return

def getRow(data_list,str1,browser):
    publish_time=browser.find_elements_by_css_selector('ul.m_m_c_list > li > em')
    district=browser.find_elements_by_css_selector('ul.m_m_c_list > li > span > a')
    projects=browser.find_elements_by_css_selector('ul.m_m_c_list > li > a')
    for T,D,P in zip(publish_time,district,projects):
        pro_href=P.get_attribute("href")
        pro_title=P.get_attribute("title")
        data_list.append([T.text,D.text,pro_title,pro_href])
    return data_list

def getData(url,path,from_date,to_date):
    str1='http://www.gdgpo.gov.cn'
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # 不加载图片,加快访问速度
    browser = webdriver.Chrome(executable_path=path,options=options)
    # browser.set_page_load_timeout(10)
    browser.get(str1)
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"a#m01")))
    print("正在收集汇总标题")
    # browser.maximize_window()
    Purchase_redirect="window.location.href='"+url+"';" #重定向到采购页面
    browser.execute_script(Purchase_redirect)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"ul#regionULId")))    
    region_all="selectSite('-1');" #选中全部地区
    browser.execute_script(region_all)    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[name='operateDateFrom']"))).send_keys(from_date)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[name='operateDateTo']"))).send_keys(to_date)
    searchOn='onSearch();'
    browser.execute_script(searchOn)
    #获取最后页码
    try:
        lastPage=wait.until(EC.presence_of_element_located((By.XPATH,"//form[@name='qPageForm']/a[last()-3]/span"))).text
        lastPage=int(lastPage)
    except:
        lastPage=1
    datalist=[]
    for i in range(lastPage):      
        datalist=getRow(datalist,str1,browser)
        try:
            browser.find_element_by_xpath("//form[@name='qPageForm']/a[last()-2]/span").click()
        except:
            pass
    browser.quit()
    print("正在爬取子页面...")
    writeInfile(datalist)
    return

# 主程序
if __name__=="__main__":
    url = 'http://www.gdgpo.gov.cn/queryMoreInfoList/channelCode/0005.html'
    path=r"D:\Program files\Cent Browser\chromedriver_2.46.exe"
    today_date=datetime.today().strftime('%Y-%m-%d')
    # from_date="2019-04-25"
    # to_date="2019-04-25"
    from_date=today_date
    to_date=today_date
    getData(url,path,from_date,to_date)
    print("爬虫完成")
    