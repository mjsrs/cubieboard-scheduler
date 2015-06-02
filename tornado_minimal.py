#!/usr/bin/env python
import logging
import tornado
import tornado.web


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Helloo, worlddd")


def main():
    application = tornado.web.Application(
        [
            (r"/", HomeHandler)
        ])
    application.listen(80)
    logging.info("server is listening...")
    print "server is listening..."
    tornado.ioloop.IOLoop.instance().start()
    print "server is stopped..."
    logging.info("server is stopped...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        logging.info("service stopped")
