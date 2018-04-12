import sqlite3
import csv

"""
CREATE TABLE "rps_record" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "id1" varchar(200) NOT NULL, 
    "id2" varchar(200) NOT NULL, 
    "action1" integer NOT NULL, 
    "action2" integer NOT NULL, 
    "competition_id" varchar(400) NOT NULL, 
    "count" integer NOT NULL, 
    "date" datetime NOT NULL
);
"""

sql_query = 'SELECT id1, id2, action1, action2, count, date FROM rps_record'

path = '/home/baislsl/Documents/srtp/data/实验数据1/db.sqlite3'
connect = sqlite3.connect(path)
cursor = connect.cursor()

result = cursor.execute(sql_query)

#
# for row in result:
#     print(row[4], '|', 'id1=', row[0], ',id2=', row[1], ',action1=', row[2], ',action2=', row[3])

headers = ['count', 'id1', 'id2', 'action1', 'action2']

rows = []
with open(path + '.csv', 'w') as csv_file:
    f_csv = csv.writer(csv_file)
    f_csv.writerow(headers)
    for row in result:
        data = [row[4], row[0], row[1], row[2], row[3]]
        rows.append(data)
    print(rows)
    f_csv.writerows(rows)