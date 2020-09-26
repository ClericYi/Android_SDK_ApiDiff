# coding=utf-8
from file import File
from surf import Surf
import sys, argparse
import threadpool
import time

switch = {
    "add": Surf.surfURIFindAddedData,
    "deprecate": Surf.surfURIFindDeprecateData,
    "remove": Surf.surfURIFindRemoveData
}


def work(version, status, url):
    if version < 19:
        return
    surfer = Surf(version)

    filer = File(version, status)

    surfer.findAllHyperLink(url).selectHyperLinkWhichIsNeeded()
    filer.outputFile(switch[status](surfer))


def find(status):
    if status.__contains__("add"):
        return "alldiffs_index_additions"
    elif status.__contains__("remove"):
        return "alldiffs_index_removals"
    else:
        return "alldiffs_index_changes"


def main(args):
    needData = []
    url = find(args.s)
    if args.v.__contains__("-"):
        versions = args.v.split("-")
        for version in range(int(versions[0]), int(versions[1]) + 1):
            needData.append((None, {"version": int(version), "status": args.s, "url": url}))
    elif args.v.__contains__("/"):
        versions = args.v.split("/")
        for version in versions:
            needData.append((None, {"version": int(version), "status": args.s, "url": url}))
    else:
        needData.append((None, {"version": int(args.v), "status": args.s, "url": url}))

    start = time.time()
    size = 5 if len(needData) > 5 else len(needData)
    pool = threadpool.ThreadPool(size)
    requests = threadpool.makeRequests(work, needData)
    [pool.putRequest(request) for request in requests]
    pool.wait()
    print("查找总耗时：", (time.time() - start), " s")


if __name__ == '__main__':
    if sys.argv.__len__() < 2:
        print("请输入指定参数 -v -s")
    else:
        try:
            parser = argparse.ArgumentParser(usage="python run.py [-v version] [-s status]")
            parser.add_argument("-v", "-version", type=str, required=True,
                                help="请指定抓取的SDK版本(Google所支持的Diff在线预览最低到19)，输入的样例存在三种：19, 19-20, 19/20/22")
            parser.add_argument("-s", "-status", type=str, required=True,
                                help="add 对应增加的方法；deprecate 对应废弃的方法；remove 对应移除的方法")
            main(parser.parse_args())
        except Exception:
            print("请输入必要参数-v -s")
