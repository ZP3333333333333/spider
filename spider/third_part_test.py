import requests
import re
import pymysql
import time
import third_part_additional_info


# 时间戳转标准时间
def stampToTime(stamp):
    datatime = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(float(str(stamp)[0:10])))
    return datatime


def getPackageName(pageSize, curPage):
    db = pymysql.connect(host='47.97.5.196',
                         user='root',
                         password='Zhouhao123.',
                         database='LowCode')
    print("数据库连接成功")
    cur = db.cursor()

    url = '''https://repo.harmonyos.com/hapmservice/registry/api/bundles?condition=%7B%22orderBy%22:[%7B%22field%22:%22hapmDownloads%22,%22orderType%22:%22DESC%22%7D],%22matchBy%22:[%7B%22field%22:%22name%22,%22opt%22:%22CONTAIN%22,%22value%22:%22%22%7D]%7D
    ''' + f'''&pageSize={pageSize}&curPage={curPage}'''
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
    }
    cookie = {
        "cookie": "HW_id_com_huawei_ide_data_repo_harmonyos_com=72aae5ba47524959978458d176bf06c8; HW_idts_com_huawei_ide_data_repo_harmonyos_com=1681264437997; HW_refts_com_huawei_ide_data_repo_harmonyos_com=1681266440448; HW_idn_com_huawei_ide_data_repo_harmonyos_com=229b229faa29461bbd9678e1fa4b9f23; HW_viewts_com_huawei_ide_data_repo_harmonyos_com=1681458563674; HW_idvc_com_huawei_ide_data_repo_harmonyos_com=114"
    }
    resp = requests.get(url, headers=headers)
    page_content = resp.text

    obj = re.compile(
        r'{"name":"@(?P<longname>.*?)","version":"(?P<version>.*?)","rom":.*?"publishTime":(?P<time>.*?),"')
    result = obj.finditer(page_content)

    for it in result:
        # print(it.group("name"))
        # print(it.group("version"))
        longname = it.group("longname")
        name = longname.split("/")[-1]  # 通过字符串分割，去掉前缀“@发布者/”
        lname = "@" + longname
        _version = it.group("version")
        _release_time = stampToTime(it.group("time"))
        # print(name, version)
        sql2 = '''
        insert into panzhuo_thirdpart_test(name, version, longname, author, description, fenlei, license, release_time, download_addr, md_addr,git_addr) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        '''
        res = third_part_additional_info.getdetail(lname, _version, _release_time)

        cur.execute(sql2, (res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9], res[10]))
        # print(lname)

    print("get one page success\n")
    db.commit()
    db.close()


if __name__ == '__main__':

    for i in range(1, 45):
        getPackageName(20, i)

# https://contentcenter-drcn.dbankcdn.com/pub_1/DevEcoSpace_1_900_9/39/v3/1JwJ7c6PQEunlb_r8h0-3w/Mv_3bV2tTCm2nHG0mHkDhA.md
