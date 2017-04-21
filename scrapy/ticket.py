import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
import time
import json

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent':user_agent}


def get_taobao(movieID , cinemaID):
    taobaoPrices = {}
    url = 'https://dianying.taobao.com/showDetailSchedule.htm?showId='+str(movieID)+'&cinemaId='+str(cinemaID)
    html = requests.get(url,headers = headers).content.decode('utf-8')
    soup = BeautifulSoup(html,'html.parser')
    dateItems = soup.find_all('div',{'class':"select-tags"})[2].find_all('a')

    if soup.find('div',{'class':"error-wrap"}) and len(dateItems)==1:
        return taobaoPrices
    else:
        for item in dateItems:
            #n_days = now + datetime.timedelta(days=i)
            #date =  n_days.strftime('%Y-%m-%d')
            date = item['data-param'].split('&')[1].split('=')[1]
            per_url = 'https://dianying.taobao.com/showDetailSchedule.htm?showId='+movieID+'&cinemaId='+cinemaID+'&date='+date
            per_html = requests.get(per_url,headers = headers).content.decode('utf-8')
            per_soup  = BeautifulSoup(per_html,'html.parser')
            if not per_soup.find('div',{'class':"error-wrap"}):
                date_list = per_soup.find('tbody').find_all('tr')
                for per_date in date_list:
                    date_str = per_date.td.em.string
                    price = float(per_date.find('td',{'class':"hall-price"}).em.string)
                    #fdate = datetime.datetime.strptime(date+' '+date_str,'%Y-%m-%d %H:%M')
                    taobaoPrices[date+' '+date_str] = price
                    print 'taobao',price,date+' '+date_str
                    time.sleep(1)
    return taobaoPrices

def get_meituan(movieID,cinemaID):
    #url='http://wh.meituan.com/shop/51041148?movieid=248700'
    #url = 'http://m.maoyan.com/shows/'+cinemaID+'?_v_=yes&movieid='+movieID+'&date='
    meituanPrices = {}
    url = 'http://m.maoyan.com/showtime/wrap.json?cinemaid=' + str(cinemaID) + '&movieid=' + str(movieID)
    content = requests.get(url,headers = headers).content.decode('utf-8')
    movie_data = json.loads(content)['data']
    if movie_data.has_key('DateShow'):
        for date in  movie_data['DateShow']:
            #n_days = now+datetime.timedelta(days=i)
            #date = n_days.strftime('%Y-%m-%d')
            for show in movie_data['DateShow'][date]:
                meituan_price = {}
                date_str = show['tm']
                price = show['sellPrStr'].split('>')[2].split('<')[0][2:4]
                meituanPrices[date+' '+date_str] = float(price)
                print 'meituan',price,date+' '+date_str
                time.sleep(1)
    return meituanPrices


def get_dianping(movieID,cinemaID):
    dianpingPrices = {}
    url = 'https://www.dianping.com/shop/'+cinemaID
    driver = webdriver.PhantomJS()  
    driver.get(url)
    time.sleep(1)
    dateItems = driver.find_elements_by_xpath("//div[@class='dates clearfix J-dates']/a")
    for item in dateItems:
        #n_days = now+datetime.timedelta(days=i)
        date = item.get_attribute("data-date")
        item.click()
        time.sleep(1)
        movie_ele = driver.find_elements_by_xpath("//li[@data-id='"+movieID+"']")
        if movie_ele != []:
            movie_ele[0].click()
            time.sleep(1)
            time_trs = driver.find_elements_by_xpath("//div[@class='booking-body']/table/tbody/tr")
            for tr in time_trs:
                items =  tr.text.split(' ')
                date_str = items[0]
                price = items[4][1:]
                dianpingPrices[date+' '+date_str] = float(price)
                print 'dianping',price,date+' '+date_str,dianpingPrices[date+' '+date_str] 
    
    driver.quit()
    return dianpingPrices


def get_gewala(movieID,cinemaID):
    print movieID,cinemaID
    gewalaPrices = {}
    driver = webdriver.PhantomJS()  
    url = 'http://www.gewara.com/cinema/'+cinemaID
    driver = webdriver.PhantomJS()
    driver.get(url)
    time.sleep(1)

    dateItems = driver.find_elements_by_xpath("//dd[@id='timeOutside']/a")
    for item in dateItems:
        date = item.get_attribute('id')
        item.click()
        time.sleep(2)
        movie_ele = driver.find_elements_by_xpath("//a[@id='"+movieID+"']")
        if movie_ele != []:
            #driver.quit()
            #return gewalaPrices
            movie_ele[0].click()
            time.sleep(2)
            js='document.getElementsByClassName("chooseOpi_body ")[0].scrollTop='
            time_trs = driver.find_elements_by_xpath("//div[@class='chooseOpi_body ']/ul/li")
            i= 0
            for tr in time_trs:
                date_str =  tr.find_element_by_xpath(".//span[@class='opitime']/b").text.strip()
                print date_str
                price =  tr.find_element_by_xpath(".//span[@class='opiPrice']/b").text.strip()
                if date_str!='' and price!='' and not tr.find_elements_by_xpath(".//label[@class='ui_nextDay']"):
                    driver.execute_script(js+str(60*i))
                    gewalaPrices[date+' '+date_str] = float(price)
                    print 'gewala',price,date+' '+date_str
                    i=i+1
                    time.sleep(1)
    driver.quit()
    return gewalaPrices

def get_ticket(db,movieID,cinemaID):
    movie = db.table_movie.find_one({'taobaoID':movieID})
    cinema = db.table_cinema.find_one({'taobaoID':cinemaID})
    taobao_dic = get_taobao(movie['taobaoID'],cinema['taobaoID'])
    if movie.has_key('meituanID') and cinema.has_key('meituanID'): 
        meituan_dic = get_meituan(movie['meituanID'],cinema['meituanID'])
    else:
        meituan_dic ={}
    if movie.has_key('dianpingID') and cinema.has_key('dianpingID'): 
        dianping_dic = get_dianping(movie['dianpingID'],cinema['dianpingID'])
    else :
        dianping_dic = {}
    if movie.has_key('gewalaID') and cinema.has_key('gewalaID'):
        gewala_dic = get_gewala(movie['gewalaID'],cinema['gewalaID'])
    else:
        gewala_dic = {}
    
    tickets= []
    if taobao_dic =={}:
        return tickets
    for key in taobao_dic:
        ticket = {}
        ticket['Date'] = datetime.datetime.strptime(key,'%Y-%m-%d %H:%M')
        #ticket['Date'] = key
        ticket['taobaoPrice'] = taobao_dic[key]
        if meituan_dic and meituan_dic.has_key(key):
            ticket['meituanPrice'] = meituan_dic[key]
        if dianping_dic and dianping_dic.has_key(key):
            ticket['dianpingPrice'] = dianping_dic[key]
            print 'aaaaaaaaaaaa'
        if gewala_dic and gewala_dic.has_key(key):
            ticket['gewalaPrice'] = gewala_dic[key]
        tickets.append(ticket)
    return tickets


#get_taobao('163989' , '28672')'''
#get_meituan('248700','13565')
#get_dianping('751317','18531515')
#get_gewala('248584531','216065937')
'''
db = MongoClient('localhost', 27017).test_database
movieID = '163989'
cinemaID = '28672'
movie = db.table_movie.find_one({'taobaoID':movieID})
cinema = db.table_cinema.find_one({'taobaoID':cinemaID})
taobao_dic = get_taobao(movie['taobaoID'],cinema['taobaoID'])
meituan_dic = get_meituan(movie['meituanID'],cinema['meituanID'])
dianping_dic = get_dianping(movie['dianpingID'],cinema['dianpingID'])
gewala_dic = get_gewala(movie['gewalaID'],cinema['gewalaID'])
'''