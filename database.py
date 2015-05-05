import sqlite3


class Database():

    def __init__(self):
        #open database
        self.conn = sqlite3.connect('/home/linaro/www/database.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cols = ['name', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'time', 'output', 'xon', 'sunrise', 'sunset']

    def close(self):
        self.conn.close()

    def add(self, table, values):
        #table - (string)
        #values - (dictionary)
        #name, mon, tue, wed, thu, fri, sat, sun, time, on, relay
        print 'values:'
        print values
        st = ''
        first = True
        for v in values.values():
            print v
            if first:
                st += '\'%s\'' % v
                first = False
            else:
                st += ',\'%s\'' % v
        #sql = 'INSERT INTO %s %s VALUES %s' % (table, tuple(values.keys()).__str__(), tuple(t_values).__str__())
        sql = 'INSERT INTO %s %s VALUES (%s)' % (table, tuple(values.keys()).__str__(), st)
        print 'SQL:'
        print sql
        self.cursor.execute(sql)
        self.conn.commit()

    def delete(self, table, id):
        sql = 'DELETE FROM %s WHERE id=%s' % (table, id)
        self.cursor.execute(sql)
        self.conn.commit()

    def update(self, table, values, key='id'):
        print 'values:'
        print values
        print "this is %s: %s" % (key, values[key])
        id = values[key]
        del values[key]
        sql = 'UPDATE %s SET %s WHERE %s=\'%s\'' % (table, self.cols_schedule(values), key, id)
        print 'SQL: %s' % sql
        self.cursor.execute(sql)
        self.conn.commit()

    def cols_schedule(self, values):
        print 'calling cols_schedule'
        cols_sta = ''
        first = True
        for name, value in values.iteritems():
            print value
            if first:
                cols_sta += '%s=\'%s\'' % (name, value)
                first = False
            else:
                cols_sta += ',%s=\'%s\'' % (name, value)
        print 'cols_sta'
        print cols_sta
        print 'calling cols_schedule - end'
        return cols_sta

    def all(self, table):
        sql = 'select * from %s' % table
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        return rows
