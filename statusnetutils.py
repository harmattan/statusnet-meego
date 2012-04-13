import os, urllib2, base64, datetime


class TimeZone(datetime.tzinfo):


        def setOffsetStr(self, offset):
                hours = int(offset[:3])
                minutes = int(offset[3:5])
                self.offset = datetime.timedelta(hours=hours, minutes=minutes)


        def utcoffset(self, dt):
                return self.offset


def getTime(timestr):
        offset = timestr[-10:-5]
	timestr = timestr[:-10] + timestr[-4:]
        dt = datetime.datetime.strptime(timestr, "%a %b %d %H:%M:%S %Y")
        tz = TimeZone()
        tz.setOffsetStr(offset)
        dt.replace(tzinfo=tz)
	return dt


def getAvatar(url, cacheDir):
	filename = url.split("/")[-1]
	imagePath = os.path.join(cacheDir, filename)
	imagePath = imagePath.replace("?", "")
	if not os.path.exists(imagePath):
		try:   
			out = open(imagePath, 'wb')
			out.write(urllib2.urlopen(url).read())
			out.close()
		except Exception, err:
			return "/opt/statusnet-meego/images/statusnet.png"
	return imagePath
