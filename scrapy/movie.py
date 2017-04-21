# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

movies = []
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent':user_agent}

taobao_url = 'https://dianying.taobao.com/showList.htm'
gewala_url = 'http://www.gewara.com/movie/'
meituan_url = 'http://www.meituan.com/dianying/zuixindianying'
dianping_url = 'http://t.dianping.com/movie/wuhan/'

def get_taobao(taobao_url):
	html  = requests.get(taobao_url,headers = headers).content.decode('utf-8')
	soup = BeautifulSoup(html,'html.parser')
	items = soup.find_all('div',attrs={'class':"tab-movie-list"})
	all_on_items = items[0].find_all('div',{'class':"movie-card-wrap"})
	all_new_items = items[1].find_all('div',{'class':"movie-card-wrap"})

	for item in all_on_items:
		movie = {}
		movie['name'] = item.find('div',{'class':"movie-card-name"}).span.string.lower()
		movie['img'] = item.find('div',{'class':"movie-card-poster"}).img['src']
		link =item.find_all('a')[1]['href']
		movie['taobaoID'] = link.split('=')[1].split('&')[0]
		movie['status'] = 0
		print movie['name'],movie['taobaoID'],movie['img']
		movies.append(movie)
	for item in all_new_items:
		movie = {}
		movie['name']= item.find('div',{'class':"movie-card-name"}).span.string.lower()
		movie['img'] = item.find('div',{'class':"movie-card-poster"}).img['src']
		link =item.find_all('a')[1]['href']
		movie['taobaoID'] = link.split('=')[1].split('&')[0]
		movie['status'] = 1
		movies.append(movie)


def get_meituan(meituan_url):
	on_html  = requests.get(meituan_url,headers = headers).content.decode('utf-8')
	on_soup = BeautifulSoup(on_html,'html.parser')
	on_items = on_soup.find_all('div',attrs={'class':"movie-cell"})

	new_html  = requests.get(meituan_url+'/coming').content
	new_soup = BeautifulSoup(new_html,'html.parser')
	new_items = new_soup.find_all('div',attrs={'class':"movie-cell"})

	for movie in movies:
		if movie['status'] == 0 :
			item = [value.h3.a['href'] for k,value in enumerate(on_items)\
				if value.h3.a.string.lower()==movie['name']]
			if item:
				movie['meituanID'] = item[0][10:]
		elif movie['status'] == 1:
			item = [value.h3.a['href'] for k,value in enumerate(new_items)\
				if value.h3.a.string.lower()==movie['name']]
			if item:
				movie['meituanID'] = item[0][10:]

def get_gewala(gewala_url):
	on_html = requests.get(gewala_url+'searchMovie.xhtml',headers = headers).content.decode('utf-8')
	on_soup = BeautifulSoup(on_html,'html.parser')
	on_pageNum =int(on_soup.find('div',{'id':"page"}).find_all('a')[-2].string)
	all_on_items = []
	for i in range(on_pageNum):
		url = gewala_url+'searchMovie.xhtml?pageNo='+str(i)
		per_html = requests.get(url).content.decode('utf-8')
		per_soup = BeautifulSoup(per_html,'html.parser')
		items = per_soup.find_all('li',{'class':"effectLi"})
		for item in items:
			all_on_items.append(item)

	new_html = requests.get(gewala_url+'futureMovie.xhtml',headers = headers).content.decode('utf-8')
	new_soup = BeautifulSoup(on_html,'html.parser')
	new_pageNum =int(on_soup.find('div',{'id':"page"}).find_all('a')[-2].string)
	all_new_items = []
	for i in range(new_pageNum):
		url = gewala_url+'futureMovie.xhtml?pageNo='+str(i)
		per_html = requests.get(url).content.decode('utf-8')
		per_soup = BeautifulSoup(per_html,'html.parser')
		items = per_soup.find_all('li',{'class':"effectLi"})
		for item in items:
			all_new_items.append(item)	

	for movie in movies:
		if movie['status'] == 0:
			item = [value.find('h2').a['href'] for k,value in enumerate(all_on_items)\
					if value.find('h2').a.string.lower()==movie['name']]
			if item:
				movie['gewalaID'] = item[0][7:]
		elif movie['status'] ==1:
			item = [value.find('h2').a['href'] for k,value in enumerate(all_new_items)\
					if value.find('h2').a.string.lower()==movie['name']]
			if item:
				movie['gewalaID'] = item[0][7:]


def get_dianping(dianping_url):		
	on_html = requests.get(dianping_url+'playing',headers = headers).content
	on_soup =BeautifulSoup(on_html,'html.parser')
	on_pageNum = int (on_soup.find('div',{'class':"Pages"}).find_all('a')[-2].string)
	all_on_items = []
	for i in range(on_pageNum):
		url = dianping_url+'playing?pageno='+str(i+1)
		per_html = requests.get(url,headers=headers).content.decode('utf-8')
		per_soup = BeautifulSoup(per_html,'html.parser')
		items = per_soup.find_all('dl',{'class':"list-item"})
		for item in items:
			all_on_items.append(item)

	new_html = requests.get(dianping_url+'comingsoon',headers = headers).content
	new_soup = BeautifulSoup(new_html,'html.parser')
	new_pageNum = int (new_soup.find('div',{'class':"Pages"}).find_all('a')[-2].string)
	all_new_items = []
	for i in range(new_pageNum):
		url = dianping_url+'comingsoon?pageno='+str(i+1)
		per_html = requests.get(url,headers = headers).content.decode('utf-8')
		per_soup =BeautifulSoup(new_html,'html.parser')
		items = per_soup.find_all('dl',{'class':"list-item"})
		for item in items:
			all_new_items.append(item)
	
	for movie in movies:
		if movie['status'] == 0:
			item = [value.dd.a['href'] for k,value in enumerate(all_on_items)\
					if value.dd.a.string.lower()==movie['name']]
			if item:
				movie['dianpingID'] = item[0][7:]
		elif movie['status'] == 1:
			item = [value.dd.a['href'] for k,value in enumerate(all_new_items)\
					if value.dd.a.string.lower()==movie['name']]
			if item:
				movie['dianpingID'] = item[0][7:]


def get_movie(db):
	table_movie = db.table_movie
	table_movie.remove()
	get_taobao(taobao_url)
	get_meituan(meituan_url)
	get_gewala(gewala_url)
	get_dianping(dianping_url)
	for movie in movies:
		table_movie.insert(movie)
	return movies


