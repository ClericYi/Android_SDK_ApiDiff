# coding=utf-8
import requests
from bs4 import BeautifulSoup


class Surf:

    def __init__(self, version):
        self.baseURL = "https://developer.android.com/sdk/api_diff/%d/changes/" % (version)
        print("**********************************************")
        print("* Notice: Now Scratch Api_Diff Version is %d *" % version)
        print("**********************************************")
        self.aAllTags = None
        self.noRepeatTags = set()
        self.index = 0
        self.total = 0

    def findAllHyperLink(self, diffURL):
        # find all HyperLink in BaseURL Index
        indexHtml = requests.get(self.baseURL + diffURL)
        # all html information save in Attribute text
        self.aAllTags = BeautifulSoup(indexHtml.text, "lxml").find_all("a")
        return self

    def selectHyperLinkWhichIsNeeded(self):
        '''
        a rule to delete useless data
        1. in aAllTags, value 0,1,2,3 is useless, because the href they have i list below, we need delete them firstly
            <a name="topheader"></a>
            <a href="/sdk/api_diff/22/changes/alldiffs_index_removals" xclass="hiddenlink">Removals</a>
            <a href="/sdk/api_diff/22/changes/alldiffs_index_additions" xclass="hiddenlink">Additions</a>
            <a href="/sdk/api_diff/22/changes/alldiffs_index_changes" xclass="hiddenlink">Changes</a>
        2. in documents has some label hyperlink <a name="A"></a>, we only use it to locate.
            <a href="#B"><font size="-2">B</font></a>
        3. like top label：<a href="#topheader"></a>
        4. need to delete package, beacause all Classes are listed
            if save it, the work will be more difficult
        '''

        # 1
        del self.aAllTags[0]
        del self.aAllTags[0]
        del self.aAllTags[0]
        del self.aAllTags[0]
        # 2 use set to save data, because they may repeat
        for tag in self.aAllTags:
            # first check use to delete rule 2 and 3
            # second check use to delete rule 4
            if len(tag.text) > 14:
                self.noRepeatTags.add(tag.get('href'))
        self.total = len(self.noRepeatTags)
        print("Total HyperLink Count: %d" % self.total)
        return self

    def findDeprecate(self, bs):
        if bs.find(id="mainBodyFluid").find('p').text.__contains__("Now deprecated."):
            return True
        else:
            return False

    def findBySummary(self, bs, summary, datas):
        index = 0
        change = bs.find(summary=summary)
        if change != None:
            changeTDs = change.find_all("td")
            for data in changeTDs:
                if index % 2 == 0:
                    datas.append(data.find("a")["name"])
                index += 1

    def count(self):
        self.index += 1
        print(self.index, "/", self.total)

    def surfURIFindDeprecateData(self):
        # use known useful hyperlink to complete data acquisition
        needBeOutputData = []

        while len(self.noRepeatTags) != 0:
            self.count()
            hasDiffClass = self.noRepeatTags.pop().split("/")[-1]
            needCheckHtml = requests.get(self.baseURL + hasDiffClass)
            bsSingleHtml = BeautifulSoup(needCheckHtml.text, "lxml")
            '''
            som methods which mark Deprecated label
            1. 
            Class org.apache.http.impl.conn.IdleConnectionHandler
            Now deprecated.
            2.
            in Change Method、Fields、Constructors
            '''
            # rule 1 priority is  over rule 2
            isAdded = False

            if bsSingleHtml.find(id="mainBodyFluid").find('p').text.__contains__("Now deprecated."):
                needBeOutputData.append(hasDiffClass)
                isAdded = True

            # find Deprecated method in Changed Methods table
            if not isAdded:
                index = 0
                changMethod = bsSingleHtml.find(summary="Changed Methods")
                if changMethod != None:
                    changMethodTDs = changMethod.find_all("td")
                    for data in changMethodTDs:
                        if data.text.__contains__("Now deprecated"):
                            needBeOutputData.append(changMethodTDs[index - 1].find("a")["name"])
                        index += 1

            # find Deprecated method in Changed Fields table
            if not isAdded:
                index = 0
                changField = bsSingleHtml.find(summary="Changed Fields")
                if changField != None:
                    changFieldTDs = changField.find_all("td")
                    for data in changFieldTDs:
                        if data.text.__contains__("Now deprecated"):
                            needBeOutputData.append(changFieldTDs[index - 1].find("a")["name"])
                        index += 1

            # find Deprecated method in Changed Constructors table
            if not isAdded:
                index = 0
                changField = bsSingleHtml.find(summary="Changed Constructors")
                if changField != None:
                    changFieldTDs = changField.find_all("td")
                    for data in changFieldTDs:
                        if data.text.__contains__("Now deprecated"):
                            needBeOutputData.append(changFieldTDs[index - 1].find("a")["name"])
                        index += 1

        return needBeOutputData

    def surfURIFindAddedData(self):
        # use known useful hyperlink to complete data acquisition
        needBeOutputData = []

        while len(self.noRepeatTags) != 0:
            self.count()
            hasDiffClass = self.noRepeatTags.pop().split("/")[-1]
            needCheckHtml = requests.get(self.baseURL + hasDiffClass)
            bsSingleHtml = BeautifulSoup(needCheckHtml.text, "lxml")
            '''
            som methods which mark Deprecated label
            1. 
            Class org.apache.http.impl.conn.IdleConnectionHandler
            Now deprecated.
            2.
            in Change Method、Fields、Constructors、Classes
            '''
            # rule 1 priority is  over rule 2
            if not self.findDeprecate(bsSingleHtml):
                # find Added method in Changed Methods table
                self.findBySummary(bsSingleHtml, "Added Methods", needBeOutputData)
                # find Added method in Changed Fields table
                self.findBySummary(bsSingleHtml, "Added Fields", needBeOutputData)
                # find Added method in Changed Constructors table
                self.findBySummary(bsSingleHtml, "Added Constructors", needBeOutputData)
                # find Added method in Changed Constructors table
                self.findBySummary(bsSingleHtml, "Added Classes", needBeOutputData)
        return needBeOutputData

    def surfURIFindRemoveData(self):
        # use known useful hyperlink to complete data acquisition
        needBeOutputData = []

        while len(self.noRepeatTags) != 0:
            self.count()
            hasDiffClass = self.noRepeatTags.pop().split("/")[-1]
            needCheckHtml = requests.get(self.baseURL + hasDiffClass)
            bsSingleHtml = BeautifulSoup(needCheckHtml.text, "lxml")
            '''
            som methods which mark Removal label
            1. 
            Class org.apache.http.impl.conn.IdleConnectionHandler
            Now deprecated.
            this is time you can skip it to speedup
            2.
            in Removal Method、Fields、Constructors、Classes
            '''
            # rule 1 priority is  over rule 2
            if not self.findDeprecate(bsSingleHtml):
                # find Removed method in Changed Methods table
                self.findBySummary(bsSingleHtml, "Removed Methods", needBeOutputData)
                # find Removed method in Changed Fields table
                self.findBySummary(bsSingleHtml, "Removed Fields", needBeOutputData)
                # find Removed method in Changed Constructors table
                self.findBySummary(bsSingleHtml, "Removed Constructors", needBeOutputData)
                # find Removed method in Removed Classes table
                self.findBySummary(bsSingleHtml, "Removed Classes", needBeOutputData)
        return needBeOutputData
