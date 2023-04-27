import requests
import re
import time


# 表名
# panzhuo_thirdpart_test

# 时间戳转标准时间
def stampToTime(stamp):
    datatime = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(float(str(stamp)[0:10])))
    return datatime


# 匹配tag时，正则中会出“[]"影响正则的语义，故先保留[],后裁剪
# get_tag()用于裁剪tag字符串前后的“[”“]”
def get_tag(str_tag):
    s = str_tag
    begin = 2
    end = len(s) - 2
    return s[begin:end]


def getdetail(lname):
    # url ='''https://repo.harmonyos.com/hapmservice/registry/api/bundles/detail/@ohos/sdkmanager-common'''

    # url = '''https://repo.harmonyos.com/hapmservice/registry/api/bundles/detail/''' + lname

    url = '''https://repo.harmonyos.com/hpm/registry/api/bundles/detail/''' + lname
    # https: // repo.harmonyos.com / hpm / registry / api / bundles / detail / @ ohos / cjson
    # url = '''https://repo.harmonyos.com/hapmservice/registry/api/bundles/detail/@ohos/jsunit'''

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    page_content = resp.text

    # 由于不同组件的详情页的json格式不同，内核版本，os版本，md_addr并不是每个组件都有
    # 为避免报错，故使用try catch

    # 内核版本
    kernel_type = ''
    try:
        obj_kernel = re.compile(
            r'''"kernel":"(?P<kernel_type>.*?)"''')
        kernel_type = obj_kernel.search(page_content).group("kernel_type")
        # print("kernel_type:", kernel_type)
    except AttributeError:
        pass
        # print("无内核信息")

    # os版本

    os_version = ''
    try:
        obj_os = re.compile(
            r'''"os":"(?P<os_version>.*?)"''')
        os_version = obj_os.search(page_content).group("os_version")
        # print("os_version:", os_version)
    except AttributeError:
        # print("无OS版本信息")
        pass

    # md_addr
    md_addr = ""
    try:
        obj_md = re.compile(r'''"download":{"addr".*?language.*?"url":"(?P<md_addr>.*?)"''')
        md_addr = obj_md.search(page_content).group("md_addr")
        # print("md_addr:", md_addr)
    except AttributeError:
        # print("无md_addr")
        pass
    name = lname.split("/")[-1]
    longname = lname
    version = ''
    author = ''
    description = ''
    license = ''
    # release_time = _release_time
    download_addr = ''
    release_time = ''
    stamp_time = ''
    try:
        obj = re.compile(
            r'''{"name":"(?P<longname>.*?)","version":"(?P<version>.*?)",.*?"license":"(?P<license>.*?)".*?download":{"addr":"(?P<download_addr>.*?)".*?"publishTime":(?P<stamp_time>.*?),"''')

        result = obj.search(page_content)

        longname = result.group("longname")
        name = longname.split("/")[-1]
        author = longname.split("/")[0][1:]

        version = result.group("version")
        # description = result.group("description")

        license = result.group("license")
        download_addr = result.group("download_addr")
        stamp_time = result.group("stamp_time")
        release_time = stampToTime(stamp_time)
        # release_time = stamp_time
        # release_time = stamp_time


    except AttributeError:
        pass

    # 代码仓库
    git_addr = ""
    try:
        zhengze = r'''{"code":200,"dat.*?"repository":"(?P<git_addr>.*?)".*?"publishTime":''' + stamp_time
        obj_gitAddr = re.compile(zhengze)

        git_addr = obj_gitAddr.search(page_content).group("git_addr")

    except AttributeError:
        pass
    #     print("无代码仓库信息")
    # print("git_addr=", git_addr)

    # description
    try:
        obj_des = re.compile(r'''"description":"(?P<description>.*?)"''')
        description = obj_des.search(page_content).group("description")
    except AttributeError:
        pass
    # '''
    # "description":"(?P<description>.*?)"
    # '''

    # 分类
    fenlei = ''
    try:
        obj_tag = re.compile(r'''tags":(?P<tag>.*?),''')

        str_tag = obj_tag.search(page_content).group("tag")
        fenlei = get_tag(str_tag)

    except AttributeError:
        pass

    # print("version:", version)
    # print("description:", description)
    # print("license:", license)
    # print(download_addr)
    # print(release_time)
    # print(md_addr)
    # print("fenlei:", fenlei)
    #
    # print("-------------------------------------------")
    return [name, version, longname, author, description, fenlei, license, release_time, download_addr, md_addr,
            git_addr, kernel_type, os_version]


if __name__ == '__main__':
    longname = '@ohos/token'
    getdetail(lname=longname)
    # 正则
    # {"code":200,"dat.*?"repository":"(?P<git_addr>.*?)".*?"publishTime":1648778595362,
