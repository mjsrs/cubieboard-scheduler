#!/usr/bin/env python
import logging
from tornado.options import define, options
from tornado import websocket, web, ioloop, escape, httpserver
import datetime
from boardio import Outputs
from database import Database
from tests.remote import RemotePubNub
import signal
import config

#using astral for sunrise/sunset calcs
#http://pythonhosted.org/astral/
import astral

DEBUG = True
CONFIG_FILE_PATH = "/home/linaro/www/config.ini"
define("port", default=80, help="run on the given port", type=int)
shutdown = False


class BaseHandler(web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def outputs(self):
        return self.application.outputs

    def get_login_url(self):
        return u"/login"

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return escape.json_decode(user_json)
        else:
            return None


class HomeHandler(BaseHandler):
    @web.authenticated
    def get(self):
        self.render("index.html")


class SchedulerItems(BaseHandler):
    @web.authenticated
    def get(self):
        rows = self.application.db.all('schedule')
        data = []
        for row in rows:
            output = {}
            map(lambda x: output.update({'%s' % x: row[x]}), row.keys())
            output['_time'] = '%s' % row['time']
            if row['sunset'] == '1':
                output['_time'] = 'Sunset'
            if row['sunrise'] == '1':
                output['_time'] = 'Sunrise'
            data.append(output)
        self.write(escape.json_encode(data))

    @web.authenticated
    def post(self):
        #start values with the checkbox because unchecked checkbox are not posted
        values = {'mon': '0', 'tue': '0', 'wed': '0', 'thu': '0', 'fri': '0', 'sat': '0', 'sun': '0', 'sunrise': '0', 'sunset': '0'}
        for key in self.request.arguments.keys():
            print self.get_argument(key).encode('utf-8')
            values[key] = '%s' % self.get_argument(key).encode('utf-8')
        print values
        if values['id'] == '':
            del values['id']
            self.application.db.add('schedule', values)
        else:
            self.application.db.update('schedule', values)
        self.redirect('/')

    def put(self):
        self.write('PUT not implemented - use post with blank id')


class DeleteSchedulerItems(BaseHandler):
    @web.authenticated
    def post(self):
        data = {'message': '', 'success': 'true'}
        ids = self.get_argument("ids")
        if ids != '':
            values = ids.split(',')
            for value in values:
                self.application.db.delete('schedule', value)
        self.write(escape.json_encode(data))


class ApiHandler(BaseHandler):
    @web.authenticated
    @web.asynchronous
    def get(self, *args):
        output = self.get_argument("output")
        value = int(self.get_argument("value"))
        values = {'output': output, 'xon': value}
        self.application.set_output(values)
        self.finish()

    @web.asynchronous
    def post(self):
        pass


class AuthLoginHandler(BaseHandler):
    def get(self):
        try:
            errormessage = self.get_argument("error")
        except:
            errormessage = ""
        self.render("login.html", errormessage=errormessage)

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.check_permission(password, username)
        if auth:
            self.set_current_user(username)
            print "logged in redirecting to: %s" % self.get_argument("next", u"/")
            self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + escape.url_escape("Login incorrect")
            self.redirect(u"/login" + error_msg)

    def check_permission(self, password, username):
        #TODO: improve security
        if username == "admin" and password == "admin":
            return True
        return False

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", escape.json_encode(user))
        else:
            self.clear_cookie("user")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in self.application.clients:
            self.application.clients.append(self)
        if len(self.application.clients) == 1:
            self.callback = ioloop.PeriodicCallback(self.getIOs, 500)
            self.callback.start()

    def on_close(self):
        if self in self.application.clients:
            self.application.clients.remove(self)
        if len(self.application.clients) == 0:
            self.callback.stop()

    def on_message(self, message):
        print 'message: %s' % message

    def getIOs(self):
        #Only send when any information is different
        dd = datetime.datetime.now()
        sun = self.application.city.sun(date=datetime.datetime.now())
        d = {'date': '%s' % dd.date(), 'time': '%s' % dd.strftime('%H:%M'), 'ios': self.application.outputs.outputs, 'conn_clients': len(self.application.clients), 'sunset': '%s' % sun['sunset'].strftime('%H:%M'), 'sunrise': '%s' % sun['sunrise'].strftime('%H:%M')}
        for c in self.application.clients:
            c.write_message(d)


class Server(web.Application):

    def __init__(self):
        #logging.basicConfig(filename='/home/linaro/www/log', format='%(asctime)s %(message)s', level=logging.DEBUG)
        self.config = config.getConfiguration(CONFIG_FILE_PATH)
        required_keys = ['city', 'LOG_FILE', 'DATABASE_PATH']
        for key in required_keys:
            if key not in self.config:
                message = "*** ERROR: key \'%s\' is required" % key
                raise Exception(message)
        self.logger = logging.getLogger('server')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.handlers.RotatingFileHandler(self.config['LOG_FILE'])
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)
        self.logger.info("starting service")
        self.logger.info("DEBUG: %s" % DEBUG)
        self.logger.debug("connecting to database")
        self.clients = []
        self.db = Database(self.config['DATABASE_PATH'])

        _astral = astral.Astral()
        _astral.solar_depression = 'civil'
        self.city = _astral[self.config['city']]

        #pubnub
        if 'pubnub' in self.config:
            if 'PUBNUB_PUBLISH_KEY' in self.config['pubnub'] and 'PUBNUB_SUBSCRIBE_KEY' in self.config['pubnub']:
                self.pubnub = RemotePubNub(self.config['pubnub']['PUBNUB_PUBLISH_KEY'], self.config['pubnub']['PUBNUB_SUBSCRIBE_KEY'])
                #self.pubnub.subscribe('control')
            else:
                del self.config['pubnub']

        #get outputs initial status
        init_outputs = []
        db_outputs = self.db.all('outputs')
        for output in db_outputs:
            init_outputs.append({'name': output['name'], 'value': output['value']})
        self.logger.debug("initializing outputs")

        self.outputs = Outputs(init_outputs)
        self.logger.info("starting server")
        options.parse_command_line()
        handlers = [
            (r"/", HomeHandler),
            (r"/login", AuthLoginHandler),
            (r"/logout", AuthLogoutHandler),
            (r"/scheduleritems", SchedulerItems),
            (r"/deletescheduleritems", DeleteSchedulerItems),
            #(r'/', IndexHandler),
            (r'/ws', SocketHandler),
            (r'/api', ApiHandler),
            #(r"/(.*)", web.StaticFileHandler,{"path": "/www/tornado"})
            (r"/(.*)", web.StaticFileHandler, {"path": "/root/www/static"})
        ]
        settings = {
            "template_path": "/home/linaro/www/static/",
            "static_path": "/home/linaro/www/static/",
            "cookie_secret": "user",
            "login_url": "/login",
            "debug": DEBUG
        }
        self.logger.info("Application init")
        self.periodic_call = ioloop.PeriodicCallback(self.check_outputs, 1000)
        self.logger.info("periodic call")
        self.periodic_call.start()
        self.logger.info("periodic call - start")
        return web.Application.__init__(self, handlers, **settings)
        #super(Server, self).__init__(self, handlers, **settings)

    #function to set output and save status to database
    #"values" should be {'output':'','xon':''}
    def set_output(self, values):
        #print "set_output called"
        if self.outputs.set(values['output'], values['xon']):  # save only if status was different
            #save status to database
            self.db.update('outputs', {'name': values['output'], 'value': values['xon']}, 'name')

    def check_outputs(self):
        global shutdown
        if shutdown is True:
            self.stop()
            return
        rows = self.db.all('outputs')
        for row in rows:
            if int(self.outputs.outputs[row['name']]['value']) != int(row['value']):
                self.logger.info('SET %s - %s:%s' % (row['id'], row['name'], row['value']))
                self.outputs.set(row['name'], row['value'])
        weekday = datetime.datetime.today().strftime("%a")
        #TODO: special sql query only weekday = 1
        rows = self.db.all('schedule')
        for row in rows:
            if row[weekday] == "1":
                _time = row['time']
                sun = self.city.sun(date=datetime.datetime.now())
                if row['sunrise'] == "1":
                    _time = '%s' % sun['sunrise'].strftime('%H:%M')
                if row['sunset'] == "1":
                    _time = '%s' % sun['sunset'].strftime('%H:%M')
                time2check = _time.split(':')
                if len(time2check) < 2:
                    continue
                #print time
                hours = time2check[0]
                minutes = time2check[1]
                now = datetime.datetime.now()
                now_hours = now.strftime('%H')
                now_minutes = now.strftime('%M')
                if now_hours == hours:
                    if now_minutes == minutes:
                        self.set_output(row)
        self.pubnub_ios()

    def pubnub_ios(self):
        ios = self.outputs.outputs
        message = {'outputs': '%s' % ios}
        if 'pubnub' in self.config:
            self.pubnub.publish('ios', message)

    def stop(self):
        #self.pubnub.pubnub.unsubscribe(channel='control')
        #self.pubnub.pubnub.stop()
        ioloop.IOLoop.instance().stop()
        self.logger.info('shutting down server')


def signal_handler(signum, frame):
    global shutdown
    logging.info('trying to stop server...')
    shutdown = True


def main():
    options.parse_command_line()
    signal.signal(signal.SIGINT, signal_handler)
    application = Server()
    http_server = httpserver.HTTPServer(application)
    http_server.listen(options.port)
    application.logger.info("server is listening...")
    ioloop.IOLoop.instance().start()
    application.logger.info("server is stopped...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ioloop.IOLoop.instance().stop()
        logging.info("service stopped")
