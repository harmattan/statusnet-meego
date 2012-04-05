import os, urllib2, base64

def getAvatar(url, cacheDir):
	filename = url.split("/")[-1]
	imagePath = os.path.join(cacheDir, base64.b64encode(filename))
	if not os.path.exists(imagePath):
		try:   
			out = open(imagePath, 'wb')
			out.write(urllib2.urlopen(url).read())
			out.close()
		except Exception, err:
			return "/usr/share/statusnet-meego/images/statusnet.png"
	return imagePath
