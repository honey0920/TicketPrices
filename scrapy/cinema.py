# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import time

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent':user_agent}

taobao_url = 'https://dianying.taobao.com/cinemaList.htm?regionName=洪山区'
meituan_url= 'http://m.maoyan.com/cinemas.json'
dianping_url = 'http://www.dianping.com/search/category/16/25/g136r116'
gewala_url = 'http://www.gewara.com/movie/searchCinema.xhtml?countycode=420111'
cinemas = []

def get_taobao(taobao_url):
	html  = requests.get(taobao_url,headers = headers).content.decode('utf-8')
	soup = BeautifulSoup(html,'html.parser')
	c_pageNum = int(soup.find('div',{'class':"list-sort M-sort"}).span.string)/10+1
	for i in range(c_pageNum):
		url = 'https://dianying.taobao.com/ajaxCinemaList.htm?regionName=洪山区&page=' + str(i+1)
		c_html = requests.get(url,headers = headers).content.decode('utf-8')
		c_soup = BeautifulSoup(c_html,'html.parser')
		c_items = c_soup.find_all('div',{'class':"detail-middle"})
		for item in c_items:
			cinema = {}
			cinema['name'] = item.div.h4.string.lower()
			cinema['taobaoID'] = item.div.h4.a['href'].split('=')[1].split('&')[0]
			cinema['address'] = item.find('span',{'class':'limit-address'}).string
			cinemas.append(cinema)
			print cinema['name'],cinema['taobaoID'],cinema['address']

def get_meituan(meituan_url):
	content = requests.get(meituan_url,headers = headers).content.decode('utf-8')
	cinema_data = json.loads(content)['data']
	c_items = cinema_data[u'洪山区']
	#html = requests.get(meituan_url,headers = headers).content.decode('utf-8')
	#soup = BeautifulSoup(html,'html.parser')
	#c_items = soup.find_all('div',{'class':"cinema-item__block cinema-item__block--detail"})
	for cinema in cinemas :
		item = [value['id'] for k,value in enumerate(c_items)\
				if value['addr'][0:10]==cinema['address'][0:10]]
		if item:
			cinema['meituanID']=item[0]
			print cinema['name']
			time.sleep(1)

		if cinema['name']==u'cgv星聚汇影城（武汉光谷店）':
			cinema['meituanID']='5846'
		elif cinema['name']==u'巨幕影城（武汉光谷广场资本大厦店）':
			cinema['meituanID']='5520'
		elif cinema['name']==u'武汉华夏国际影城-鲁广店':
			cinema['meituanID']='7753'
		elif cinema['name'] == u'武汉耀莱成龙国际影城（光谷店）':
			cinema['meituanID'] = '13565'
		elif cinema['name']==u'银兴菲林国际影城佰港城店':
			cinema['meituanID'] = '10967'
		elif cinema['name']==u'银兴国际影城光谷时尚城店':
			cinema['dianpingID'] = '17024'

	#for item in c_items:
	#	print item
	#	print item.dl.dd.string.strip()[0:10]

def get_dianping(dianping_url):
	html = requests.get(dianping_url,headers = headers).content.decode('utf-8')
	soup = BeautifulSoup(html,'html.parser')
	c_pageNum = int (soup.find('div',{'class':"page"}).find_all('a')[-2].string)
	c_items = []
	addr_items = []
	for i in range(c_pageNum):
		url = dianping_url +'p' + str(i+1)
		per_html = requests.get(url,headers = headers).content
		per_soup = BeautifulSoup(per_html,'html.parser')
		title_items = per_soup.find_all('div',{'class':"tit"})
		a_items=per_soup.find_all('span',{'class':"addr"})

		for item in a_items:
			addr_items.append(item)
		for item in title_items:
			c_items.append(item)

	for cinema in cinemas :
		item = [value.a['href'] for k,value in enumerate(c_items)\
				if addr_items[k].string.strip()[0:8]==cinema['address'][3:11]]
		if item:
			cinema['dianpingID']=item[0][6:]

		if cinema['name']==u'cgv星聚汇影城（武汉光谷店）':
			cinema['dianpingID']='18531515'
		elif cinema['name']==u'巨幕影城（武汉光谷广场资本大厦店）':
			cinema['dianpingID']='8838036'
		elif cinema['name']==u'武汉华夏国际影城-鲁广店':
			cinema['dianpingID']='14749788'
		elif cinema['name'] == u'武汉耀莱成龙国际影城（光谷店）':
			cinema['dianpingID'] = '19283233'
		elif cinema['name']==u'银兴菲林国际影城佰港城店':
			cinema['dianpingID'] = '19828714'
		elif cinema['name']==u'银兴国际影城光谷时尚城店':
			cinema['dianpingID'] = '77562138'

		#c_items = c_soup.find_all()
def get_gewala(gewala_url):
	html = requests.get(gewala_url,headers = headers).content.decode('utf-8')
	soup = BeautifulSoup(html,'html.parser')
	c_pageNum = int(soup.find('div',{'id':"page"}).find_all('a')[-2].string)
	c_items = []
	addr_items=[]
	for i in range(c_pageNum):
		url = gewala_url + '&pageNo='+str(i)
		per_html = requests.get(url,headers = headers).content 
		per_soup = BeautifulSoup(per_html,'html.parser').find('div',{'class':"movieList"})
		items_1 = per_soup.find_all('h2')
		items_2 = per_soup.find_all('p',{'class':"mt10"})
		for item in items_1:
			c_items.append(item)
		for item in items_2:
			addr_items.append(item.get_text(strip=True).split(']')[1][:-3])
			
	for cinema in cinemas:
		item = [value.a['href'] for k,value in enumerate(c_items)\
				if addr_items[k][0:8] == cinema['address'][3:11]]
		if item:
			cinema['gewalaID']=item[0][8:]
		if cinema['name']==u'cgv星聚汇影城（武汉光谷店）':
			cinema['gewalaID']='216065937'
		elif cinema['name']==u'巨幕影城（武汉光谷广场资本大厦店）':
			cinema['gewalaID']='102287206'
		elif cinema['name']==u'武汉华夏国际影城-鲁广店':
			cinema['gewalaID']='144768355'
		elif cinema['name'] == u'武汉耀莱成龙国际影城（光谷店）':
			cinema['gewalaID'] = '264439068'
		elif cinema['name']==u'银兴菲林国际影城佰港城店':
			cinema['gewalaID'] = '225333969'


def get_cinema(db):
	table_cinema = db.table_cinema
	table_cinema.remove()
	get_taobao(taobao_url)
	get_meituan(meituan_url)
	get_dianping(dianping_url)
	get_gewala(gewala_url)
	for cinema in cinemas:
		table_cinema.insert(cinema)
	return cinemas
#cinemas = []
#get_taobao(taobao_url)
#get_meituan(meituan_url)