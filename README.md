# app-fetcher
Visit of app info in "iTunes" and "Google Play" store

###背景

对于游戏类广告投放，获取游戏类别，对兴趣、受众的选择有很大的帮助。我们目前简单处理，只抓取指定游戏在app store上面的游戏类别标签来获取相关信息。

###ios类游戏
itunes提供了对外的API，可以访问指定国家的应用描述。
完整的API支持文档在[这里](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)，如果只关心我背景里提到的内容，那么可以直接用如下调用：

	https://itunes.apple.com/{$country}/lookup?id={$itunesId}
其中country可以不填，如是美国，则是US，这里要填country的主要原因是有些应用只在指定国家上架。

返回格式中包含results列表，其中每个result都是对应用信息的描述。

###android类游戏
相比ios的宽松而言，google play并没有提供访问应用信息的API (存在一些用户发布应用的API)。如果自己抓取页面，可能会面临的问题是动态页面，更重要的是页面变化需要长期维护，因此在市场上调研了一些工具：

	 https://github.com/chadrem/market_bot    ruby开源，语法相对不熟悉
     https://www.apptweak.io/ 收费产品，100 free API per month，次数太少
     https://github.com/MarcelloLins/GooglePlayAppsCrawler 也是收费，但没来得及细看，可能也还行

最终选择了[42matters](https://42matters.com/launchpad)的试用版本，1000 per month可以满足我的需求。另外，它的数据准确度是很不错的，还是建议大量使用的朋友购买收费版本。

调用方法见[文档](https://42matters.com/docs/app-market-data/android/apps/lookup)，举个例子：

	https://data.42matters.com/api/v2.0/android/apps/lookup.json?p=com.eyougame.fbhx&access_token=YOUR_TOKEN

另外要说的是，免费用户每天的调用上限是100次。

###程序相关
依赖

	安装request
	输入文件在data对应目录，按url格式排列

配置

	如果是Android应用，在配置文件里填写access_token
	如果是非US，请替换成对应国家 （Android没有做）
	
调用 

	python app_crawler.py

###后续补充

因为只是一个临时性的应用，有很多地方考虑的很简单，也不够完善，比如脚本里只获取app的类型，而API实际返回的信息很多。总体来说，只当是一个方向的简单探索吧。
