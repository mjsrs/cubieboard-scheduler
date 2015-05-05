#!/usr/bin/python
import sqlite3


def main():
    database = 'database.db'
    tables = ['schedule', 'outputs']
    print tables
    #connect to database
    print "connecting to database %s" % database
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    #print tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    db_tables = c.fetchall()
    for t in db_tables:
        if t[0] == 'sqlite_sequence':
            continue
        sql = 'drop table %s' % t[0]
        print sql
        c.execute(sql)
    #create schedule table if not exists
    sql = '''create table if not exists %s (id integer primary key autoincrement,name text, mon text,tue text,wed text,thu text,fri text,sat text,sun text, time text, output text, xon text, sunrise text, sunset text);''' % tables[0]
    print "executing sql: %s" % sql
    c.execute(sql)
    sql = '''create table if not exists %s (id integer primary key autoincrement,name text, value text);''' % tables[1]
    print "SQL: %s" % sql
    c.execute(sql)

    #TODO: start pinout values
    values = ['(1,"R1","0")', '(2,"R2","0")', '(3,"R3","0")', '(4,"R4","0")']
    for value in values:
        sql = 'INSERT INTO outputs VALUES %s' % value
        print 'SQL: %s' % sql
        c.execute(sql)
    conn.commit()
    c.execute("SELECT * FROM outputs")
    rows = c.fetchall()
    print 'outputs: %s' % len(rows)
    for row in rows:
        print row
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print tables
    conn.close()
    print "done"


if __name__ == '__main__':
    main()


#{id:1, name:'ligar maq. cafe', week_days:[1,1,1,1,1,0,0], time:'08:30', on:True, relay:1},