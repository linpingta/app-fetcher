#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

''' App Crawler'''
__author__='linpingta@163.com'

import os,sys
import logging
import ConfigParser

import time
import re
import requests
import simplejson as json


class AppCrawler(object):
	''' App Info Fetcher, 
	maybe not crawler, but used for itunes store or google play store info fetch
	'''
	def __init__(self, conf):
		# app_url list
		self.app_urls = []
		# app_id as key, app_info (list) as value
		self.app_info_dict = {}

		self.country = conf.get('app_crawler','country')
		self.lang = conf.get('app_crawler','lang')

		self.requests = requests.Session()

	def _extract_unique_id(self, app_url, logger):
		return ''

	def _request(self, app_unique_id, logger):
		return []

	def load_file(self, app_url_file, logger):
		with open(app_url_file, 'r') as fp_r:
			while 1:
				line = fp_r.readline()
				line = line.strip()
				if not line:
					break
				self.app_urls.append(line)

	def save_file_for_human(self, app_url_file_output, logger):
		with open(app_url_file_output, 'w') as fp_w:
			for app_id, app_info in self.app_info_dict.iteritems():
				t = []
				if not app_info:
					continue
				[ t.append(str(item)) for item in app_info ]
				t_s = '::'.join(t)
				t_f = ','.join([str(app_id), t_s])
				fp_w.write("%s" % t_s)

	def save_file(self, app_url_file_output, logger):
		with open(app_url_file_output, 'w') as fp_w:
			json.dump(self.app_info_dict, fp_w)

	def run(self, logger):
		for idx, app_url in enumerate(self.app_urls):
			logger.info('%s : %s fetch app_info' % (self.__class__.__name__, app_url))
			app_unique_id = self._extract_unique_id(app_url, logger)
			if not app_unique_id:
				logger.warning('no info extracted from app_url %s' % app_url)
			else:
				app_info = self._request(app_unique_id, logger)
				self.app_info_dict[app_unique_id] = app_info

			time.sleep(2)


class AndroidAppCrawler(AppCrawler):
	''' Android Info
	'''
	def __init__(self, conf):
		self.prefix_url = 'https://data.42matters.com/api/v2.0/android/apps/lookup.json'
		self.android_access_token = conf.get('app_crawler','android_access_token')

		super(AndroidAppCrawler, self).__init__(conf)

	def _extract_unique_id(self, app_url, logger):
		info = re.findall('id=(.*)', app_url, 0)
		return info[0] if info else ''

	def _request(self, app_unique_id, logger):

		method = 'GET'
		path = "/".join((self.prefix_url,
			'lookup',
		))
		params = {'p': app_unique_id,
			'access_token': self.android_access_token
		}
		response = self.requests.request(
			method,
			path,
			params=params
		)
		if response.status_code == 200:
			content = response.json()
			for key, item in content.iteritems():
				print key, item
			if 'cat_keys' in content:
				return content['cat_keys']
			elif 'cat_key' in content:
				return [ content['cat_key'] ]
			else:
				return []
		return []


class IosAppCrawler(AppCrawler):
	''' Ios Info
	'''
	def __init__(self, conf):
		self.prefix_url = 'https://itunes.apple.com'
		super(IosAppCrawler, self).__init__(conf)

	def _extract_unique_id(self, app_url, logger):
		info = re.findall('id(.*)', app_url, 0)
		return info[0] if info else ''

	def _request(self, app_unique_id, logger):

		method = 'GET'
		path = "/".join((self.prefix_url,
			self.country,
			'lookup',
		))
		params = {'id': app_unique_id}
		response = self.requests.request(
			method,
			path,
			params=params
		)
		if response.status_code == 200:
			content = response.json()
			if 'results' in content:
				results = content['results']
				if results:
					return results[0]['genres']
			return []
		return []


if __name__ == '__main__':

	basepath = os.path.abspath(os.getcwd())
	confpath = os.path.join(basepath, 'conf/app_crawler.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)

	logging.basicConfig(filename=os.path.join(basepath, 'logs/app_crawler.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('AdManager')

	try:
		# android crawl
		app_url_file = os.path.join(basepath, 'data/android_url.csv')
		app_url_file_output = os.path.join(basepath, 'data/android_urls_output')
		android_crawler = AndroidAppCrawler(conf)
		android_crawler.load_file(app_url_file, logger)
		android_crawler.run(logger)
		android_crawler.save_file(app_url_file_output, logger)

		# ios crawl
		app_url_file = os.path.join(basepath, 'data/ios_url.csv')
		app_url_file_output = os.path.join(basepath, 'data/ios_urls_output')
		ios_crawler = IosAppCrawler(conf)
		ios_crawler.load_file(app_url_file, logger)
		ios_crawler.run(logger)
		ios_crawler.save_file(app_url_file_output, logger)
	except Exception,e:
		logging.exception(e)
