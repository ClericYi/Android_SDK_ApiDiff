import pandas as pd


class File:

    def __init__(self, version, status):
        self.writeToFilePath = status + "_SDK_" + str(version) + ".xlsx"

    def outputFile(self, datas):
        # output file format is excel
        fileData = pd.DataFrame(index=datas)
        writer = pd.ExcelWriter(self.writeToFilePath)
        fileData.to_excel(writer)
        writer.save()
        print("**********************************************")
        print("Scratch is Over,the file name is  %s" % self.writeToFilePath)
        print("**********************************************")
