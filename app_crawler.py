#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

''' App Crawler'''
__author__='linpingta@163.com'

import os
import sys
import logging
try:
	import ConfigParser
except ImportError:
	import configparser as ConfigParser
import time
import re
import requests
import simplejson as json
from abc import ABCMeta, abstractmethod


class AppCrawler(object):
	""" App Info Fetcher,
	maybe not crawler, but used for itunes store or google play store info fetch
	"""
	__metaclass__ = ABCMeta

	def __init__(self, conf):
		self._country = conf.get('app_crawler','country')
		self._lang = conf.get('app_crawler','lang')

		# app_url list
		self._app_urls = []

		# app_id as key, app_info (list) as value
		self._app_info_dict = {}

		self._requests = requests.Session()

	@abstractmethod
	def _extract_unique_id(self, app_url, logger):
		pass

	@abstractmethod
	def _request(self, app_unique_id, logger):
		pass

	def load_file(self, app_url_file, logger):
		with open(app_url_file, 'r') as fp_r:
			while 1:
				line = fp_r.readline()
				line = line.strip()
				if not line:
					break
				self._app_urls.append(line)

	def save_file(self, app_url_file_output, logger):
		with open(app_url_file_output, 'w') as fp_w:
			json.dump(self._app_info_dict, fp_w)

	def save_file_for_human(self, app_url_file_output, logger):
		with open(app_url_file_output, 'w') as fp_w:
			for app_id, app_info in self._app_info_dict.iteritems():
				if not app_info:
					continue
				t = []
				[ t.append(str(item)) for item in app_info ]
				t_s = '::'.join(t)
				t_f = ','.join([str(app_id), t_s])
				fp_w.write("%s" % t_s)

	def run(self, logger):
		for idx, app_url in enumerate(self._app_urls):
			logger.info('%s : %s fetch app_info' % (self.__class__.__name__, app_url))
			app_unique_id = self._extract_unique_id(app_url, logger)
			if not app_unique_id:
				logger.warning('no info extracted from app_url %s' % app_url)
			else:
				app_info = self._request(app_unique_id, logger)
				self._app_info_dict[app_unique_id] = app_info
			time.sleep(1)


class AndroidAppCrawler(AppCrawler):
	""" Android Info Read, with 42 masters
	"""
	def __init__(self, conf):
		super(AndroidAppCrawler, self).__init__(conf)

		self._prefix_url = conf.get('android_app_crawler', 'prefix_url')
		self._android_access_token = conf.get('android_app_crawler','android_access_token')

	def _extract_unique_id(self, app_url, logger):
		info = re.findall('id=(.*)', app_url, 0)
		return info[0] if info else ''

	def _request(self, app_unique_id, logger):

		method = 'GET'
		path = "/".join((self._prefix_url,
			'lookup',
		))
		params = {'p': app_unique_id,
			'access_token': self._android_access_token
		}
		response = self._requests.request(
			method,
			path,
			params=params
		)
		if response.status_code == 200:
			content = response.json()
			#for key, item in content.iteritems():
			#	print key, item
			if 'cat_keys' in content:
				return content['cat_keys']
			elif 'cat_key' in content:
				return [ content['cat_key'] ]
			else:
				return []
		return []


class IosAppCrawler(AppCrawler):
	""" Ios Info
	"""
	def __init__(self, conf):
		super(IosAppCrawler, self).__init__(conf)

		self._prefix_url = conf.get('ios_app_crawler', 'prefix_url')

	def _extract_unique_id(self, app_url, logger):
		info = re.findall('id(.*)', app_url, 0)
		return info[0] if info else ''

	def _request(self, app_unique_id, logger):

		method = 'GET'
		path = "/".join((self._prefix_url,
			self._country,
			'lookup',
		))
		params = {'id': app_unique_id}
		response = self._requests.request(
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
	logger = logging.getLogger('AppCrawler')

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
