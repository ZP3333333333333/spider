import requests
import re
import time


# 表名
# panzhuo_thirdpart_test

def stampToTime(stamp):
    datatime = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(float(str(stamp)[0:10])))
    return datatime


def get_tag(str_tag):
    s = str_tag
    begin = 2
    end = len(s) - 2
    return s[begin:end]


def getdetail(lname, _version, _release_time):
    # url ='''https://repo.harmonyos.com/hapmservice/registry/api/bundles/detail/@ohos/sdkmanager-common'''

    url = '''https://repo.harmonyos.com/hapmservice/registry/api/bundles/detail/''' + lname

    # url = '''https://repo.harmonyos.com/hapmservice/registry/api/bundles/detail/@ohos/jsunit'''

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    page_content = resp.text

    # # 内核版本
    # try:
    #     obj_kernel = re.compile(
    #         r'''"kernel":"(?P<kernel_type>.*?)"''')
    #     kernel_type = obj_kernel.search(page_content).group("kernel_type")
    #     print(kernel_type)
    # except AttributeError:
    #     print("无内核信息")
    #
    # # os版本
    #
    # try:
    #     obj_os = re.compile(
    #         r'''"os":"(?P<os_version>.*?)"''')
    #     os_version = obj_os.search(page_content).group("os_version")
    #     print(os_version)
    # except AttributeError:
    #     print("无OS版本信息")

    # 代码仓库
    git_addr = ""
    try:
        obj_gitAddr = re.compile(
            r'''"repository":"(?P<git_addr>.*?)"''')
        git_addr = obj_gitAddr.search(page_content).group("git_addr")

    except AttributeError:
        pass
    #     print("无代码仓库信息")
    # print("git_addr=", git_addr)

    # md_addr
    md_addr = ""
    try:
        obj_md = re.compile(r'''"download":{"addr".*?language.*?"url":"(?P<md_addr>.*?)"''')
        md_addr = obj_md.search(page_content).group("md_addr")
        # print(md_addr)
    except AttributeError:
        # print("无md_addr")
        pass
    name = lname.split("/")[-1]
    longname = lname
    version = _version
    author = ''
    description = ''
    fenlei = ''
    license = ''
    release_time = _release_time
    download_addr = ''

    try:
        obj = re.compile(
            r'''{"name":"(?P<longname>.*?)","version":"(?P<version>.*?)",.*?"description":"(?P<description>.*?)".*?"tags":(?P<tag>.*?),.*?"license":"(?P<license>.*?)".*?download":{"addr":"(?P<download_addr>.*?)".*?"publishTime":(?P<stamp_time>.*?),"''')

        result = obj.search(page_content)

        longname = result.group("longname")
        name = longname.split("/")[-1]
        author = longname.split("/")[0][1:]

        version = result.group("version")
        description = result.group("description")
        str_tag = result.group("tag")
        fenlei = get_tag(str_tag)
        license = result.group("license")
        download_addr = result.group("download_addr")
        stamp_time = result.group("stamp_time")
        release_time = stampToTime(stamp_time)
    except AttributeError:
        pass

    # md_addr = result.group("md_addr")
    # print(description)
    # print(fenlei, license)
    # print(download_addr)
    # print(release_time)
    # print(md_addr)
    # print("-------------------------------------------")
    return [name, version, longname, author, description, fenlei, license, release_time, download_addr, md_addr,
            git_addr]


if __name__ == '__main__':
    longname = ''
    getdetail(longname)
