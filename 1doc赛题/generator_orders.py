# coding=utf-8

import random
import socket
import time
import pymysql
import threading
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def send_to_socket(hostname,port):
    print("开始端口发送数据............,请确保机器{}上的MySql中具有ds_pub数据库".format(hostname))
    print("开始端口发送数据............,请确保机器{}上的端口{}已被监听".format(hostname,port))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((hostname, port))

    # fake = Faker(locale='zh_CN')
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='ds_pub', charset='utf8')
    cursor = conn.cursor()
    cont = cursor.execute("""
        select order_info.id,consignee,consignee_tel,final_total_amount,order_status,user_id,feight_fee,create_time,expire_time,base_province.name as province_name,base_region.region_name from order_info
        inner join base_province on order_info.province_id=base_province.id
        inner join base_region on base_province.region_id=base_region.id
    """)
    res = cursor.fetchall()

    cursor2 = conn.cursor()
    cont2 = cursor2.execute("""
        select id,order_id,sku_id,order_price,sku_num,create_time from order_detail
    """)
    res2 = cursor2.fetchall()

    cursor.close()
    cursor2.close()
    conn.commit()
    conn.close()
    # 逐行将数据发送至端口
    recordResults = []  # 定义一个数组
    # 遍历元组数据将数据装到指定元组
    for row in res:
        result = '==order_info==({}+{}+{}+{}+{}+{}+{}+\'{}\'+\'{}\'+{}+{})'.format(row[0],
                                                                                  row[1], row[2], float(row[3]), row[4],row[5],
                                                                                  float(row[6]), row[7], row[8], row[9],
                                                                                  row[10])
        recordResults.append(result)

    for row in res2:
        result = '==order_detail==({}+{}+"{}"+{}+{}+"{}")'.format(row[0],
                                                        row[1], row[2], row[3], row[4],row[5])
        recordResults.append(result)

    random.shuffle(recordResults)
    # 发送给指定端口延迟0.5秒
    for line in recordResults:
        time.sleep(0.5)
        print("" + (str(line)))
        client.send((str(line)+'\n').encode('utf-8'))

    print("端口数据发送完毕............")

if __name__ == '__main__':
    send_to_socket('127.0.0.1',10050)
    t1 = threading.Thread(target=send_to_socket,args=('127.0.0.1',25001))   #这里根据需要连接监听的端口机器ip
    t1.start()
