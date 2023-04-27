import requests
import re
import pymysql
import time
import system_part_additional_info


# 将时间戳转换为标准时间格式
def stampToTime(stamp):
    datatime = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(float(str(stamp)[0:10])))
    return datatime


def getPackageName(pageSize, curPage):
    # 连接数据库
    db = pymysql.connect(host='47.97.5.196',
                         user='root',
                         password='Zhouhao123.',
                         database='LowCode')
    print("数据库连接成功")
    cur = db.cursor()

    # 拼接url
    url = '''https://repo.harmonyos.com/hpm/registry/api/bundles?condition=%7B%22orderBy%22:[%7B%22field%22:%22downloads%22,%22orderType%22:%22DESC%22%7D],%22matchBy%22:[%7B%22field%22:%22name%22,%22opt%22:%22CONTAIN%22,%22value%22:%22%22%7D]%7D''' + \
          f'''&pageSize={pageSize}&curPage={curPage}'''
    # 伪装http请求头
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
    }
    # 伪装网络cookie(实测不加cookie也行)
    cookie = {
        "cookie": "HW_id_com_huawei_ide_data_repo_harmonyos_com=72aae5ba47524959978458d176bf06c8; HW_idts_com_huawei_ide_data_repo_harmonyos_com=1681264437997; HW_refts_com_huawei_ide_data_repo_harmonyos_com=1681266440448; HW_idn_com_huawei_ide_data_repo_harmonyos_com=229b229faa29461bbd9678e1fa4b9f23; HW_viewts_com_huawei_ide_data_repo_harmonyos_com=1681458563674; HW_idvc_com_huawei_ide_data_repo_harmonyos_com=114"
    }
    # 获取网页请求结果
    resp = requests.get(url, headers=headers, cookies=cookie)
    page_content = resp.text

    # 创建正则
    obj = re.compile(r'{"name":"@(?P<longname>.*?)","version":"(?P<version>.*?)","rom":.*?"publishTime":'
                     r'(?P<stamp>.*?),')
    # 匹配正则，返回迭代器
    result = obj.finditer(page_content)

    # 遍历迭代器，通过分组获取所需数据
    for it in result:
        # print(it.group("name"))
        # print(it.group("version"))
        longname = it.group("longname")
        name = longname.split("/")[-1]
        hpm = "hpm i @" + longname
        longname = "@" + longname
        # version = it.group("version")
        # stamp = it.group("stamp")
        # realtime = stampToTime(stamp)
        # print(name, version, hpm, realtime)

        # 往表中插入数据的sql语句
        sql2 = '''
        insert into panzhuo_systempart_test(name, version, longname, author, description, fenlei, license, release_time, download_addr, md_addr,
            git_addr, kernel_type, os_version,hpm) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        '''
        # cur.execute(sql2, (name, version, realtime, hpm))
        res = system_part_additional_info.getdetail(longname)
        # print(longname)
        cur.execute(sql2, (
            res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9], res[10], res[11], res[12],
            hpm))

    print("get one page success\n")
    # 提交事务
    db.commit()
    db.close()


if __name__ == '__main__':
    # for循环遍历页号1-49页的内容(官方组件看似有65页，实际从第50页开始都是重复内容)
    for i in range(1, 50):
        getPackageName(20, i)
