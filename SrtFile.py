import os
from srt import *


class SrtFile(object):

    def __init__(self, path):
        self.__str__()
        self.path = os.path.splitext(path)[0]
        self.allsubs = []
        self.index = 0

    def addsub(self, start, end, content, orgtext="", proprietary=""):
        start = timedelta(milliseconds=start)
        end = timedelta(milliseconds=end)
        newsub = Subtitle(self.index, start, end, content, proprietary)
        newsub.orgtext = orgtext
        self.allsubs.append(newsub)
        self.index += 1

    def addsub_timedelta(self, start, end, content, orgtext="", proprietary=""):
        newsub = Subtitle(self.index, start, end, content, proprietary)
        newsub.orgtext = orgtext
        self.allsubs.append(newsub)
        self.index += 1

    def getsrt(self):
        text = ""
        for sub in self.allsubs:
            text += sub.to_srt()
        return make_legal_content(text)

    def get_subs(self):
        self.sort_subs()
        return self.allsubs

    def save(self):
        if len(self.allsubs) > 0:
            self.sort_subs()
            with open(self.path + ".srt", "w", encoding="utf-8") as f:
                f.write(self.getsrt())
            print("SRT File Has Been Saved ")

    def sort_subs(self):
        def getstart(elem):
            return elem.start

        self.allsubs.sort(key=getstart)

        for index, sub in enumerate(self.allsubs):
            sub.index = index

    def get_at(self, pos):
        pos_time = timedelta(milliseconds=pos)
        for sub in self.allsubs:
            if sub.start < pos_time < sub.end:
                return sub.content
                break
        return ""

    def get_sub_at(self, pos):
        pos_time = timedelta(milliseconds=pos)
        for sub in self.allsubs:
            if sub.start < pos_time < sub.end:
                return sub
                break

        return None

    def clear(self):
        self.allsubs.clear()

    def updata(self, srtfile, dur):
        i = 0
        while i < dur:
            sub = srtfile.get_sub_at(i * 1000)
            if sub:
                start = int(sub.start.total_seconds())
                end = int(sub.end.total_seconds())
                newsub = ""
                for j in range(start, end):
                    newsub += self.get_at(j * 1000)
                if newsub == "":
                    self.allsubs.append(sub)
                i = end + 1
            else:
                i += 1
