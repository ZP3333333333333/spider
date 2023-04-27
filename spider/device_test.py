import requests
import re
import pymysql
import time


# import json

# 将时间戳转换为常用的时间格式
def stampToTime(stamp):
    datatime = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(float(str(stamp)[0:10])))
    return datatime


# 获取组件详情页面的数据
def getdetail(longname):
    # 拼接url
    url = '''https://repo.harmonyos.com/hpm/registry/api/bundles/detail/''' + longname

    # 伪装http请求头
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
    }

    # 得到网页数据
    resp = requests.get(url, headers=headers)
    page_content = resp.text

    # 由于详情页面某些组件的json文本格式存在差异
    # 故开源许可license、markdown文件md_addr、组件依赖的库package需单独写正则表达式去匹配

    # get_license
    license = ''
    obj_license = re.compile(r'''"license":"(?P<license>.*?)"''')
    re_license = obj_license.search(page_content)
    license = re_license.group("license")
    # print(license)

    # get_md_addr
    md_addr = ''
    obj_md = re.compile(r'''"url":"https(?P<md_addr>.*?)md''')
    re_md_addr_cut = obj_md.search(page_content)
    md_addr_cut = re_md_addr_cut.group("md_addr")

    md_addr = "https" + md_addr_cut + "md"
    # print("md_addr:", md_addr)

    # get_json
    # json正则
    # "dependencies":{.*?}
    obj_json = re.compile(r'''"dependencies":(?P<json>.*?)}''')
    re_json = obj_json.search(page_content)
    json_package = re_json.group("json")
    json_package += "}"
    # package = json.loads(json_package)
    # print(json_package)

    # 版本、os版本、内核等信息可同时匹配，分别通过正则中的分组提取
    obj_kernel = re.compile(
        r'''"version":"(?P<version>.*?)".*?".*?"os":"(?P<os_version>.*?)","board":"(?P<board>.*?)","kernel":"(?P<kernel>.*?)".*?"repository":"(?P<git_addr>.*?)"''')
    res = obj_kernel.search(page_content)
    version = res.group("version")
    os_version = res.group("os_version")
    board = res.group("board")
    kernel = res.group("kernel")
    git_addr = res.group("git_addr")
    return [license, md_addr, version, os_version, board, kernel, git_addr, json_package]


def getPackageName(pageSize, curPage):  # pageSize, curPage用于拼接url
    db = pymysql.connect(host='47.97.5.196',
                         user='root',
                         password='Zhouhao123.',
                         database='LowCode')
    print("数据库连接成功")
    cur = db.cursor()
    url = '''https://repo.harmonyos.com/hpm/registry/api/solutions?condition=%7B%22orderBy%22:[%7B%22field%22:%22publishTime%22,%22orderType%22:%22DESC%22%7D],%22matchBy%22:[%7B%22field%22:%22name%22,%22opt%22:%22CONTAIN%22,%22value%22:%22%22%7D]%7D''' + f'''&pageSize={pageSize}&curPage={curPage}'''

    # http请求头，将python爬虫伪装成浏览器请求
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
    }

    resp = requests.get(url, headers=headers)  # 请求网页内容
    page_content = resp.text  # 获取json文本

    # 创建正则表达式匹配网页的json文本
    obj = re.compile(
        r'''{"bundleName":"(?P<longname>.*?)","name":"(?P<name>.*?)".*?"category":"(?P<category>.*?)".*?"remark":"(?P<remark>.*?)".*?"imgUrl":"(?P<imgUrl>.*?)".*?"createTime":(?P<createTime_stamp>.*?),"modifyTime":(?P<modifyTime_stamp>.*?)}''')
    result = obj.finditer(page_content)  # 返回匹配成功的迭代器

    # 遍历迭代器，通过正则中的分组得到相应的数据
    for it in result:
        bundleName = it.group("longname")
        name = it.group("name")
        category = it.group("category")
        remark = it.group("remark")
        imgUrl = it.group("imgUrl")
        createTime = stampToTime(it.group("createTime_stamp"))
        modifyTime = stampToTime(it.group("modifyTime_stamp"))
        # print(bundleName, name, category, remark, imgUrl, createTime, modifyTime)

        # 调用getdetail()获取组件详情页的数据,返回一包含数据的数组
        # 参数bundleName用于拼接url
        res = getdetail(bundleName)

        # print(name)

        # 向表中插入数据的sql语句
        sql2 = '''
                insert into device_new_test(license,md_addr,version,os_version,board,kernel,git_addr,package,name,bundleName,category,remark,imgUrl,createTime, modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                '''
        # cur.execute(sql2, (name,))
        # print(longname)
        cur.execute(sql2, (
            res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], name, bundleName, category, remark, imgUrl,
            createTime, modifyTime))

    print("get one page success\n")
    # 提交执行的aql语句
    db.commit()
    db.close()


if __name__ == '__main__':
    # for循环遍历页号1-5(如有数据更新，可根据页号修改)
    for i in range(1, 6):
        getPackageName(15, i)
