#!/usr/bin/env python
import logging
from Pubnub import Pubnub


class RemotePubNub():

    def __init__(self, PUBNUB_PUBLISH_KEY="demo", PUBNUB_SUBSCRIBE_KEY="demo", queue=None):
        self.pubnub = Pubnub(publish_key=PUBNUB_PUBLISH_KEY, subscribe_key=PUBNUB_SUBSCRIBE_KEY)
        self.queue = queue

    def get_queue(self):
        return self.queue

    def publish(self, channel, message):
        self.pubnub.publish(channel, message)
        #logging.info("message published")

    def subscribe(self, channel):
        self.pubnub.subscribe(
            channel, callback=self.parse_command, error=self.sub_error,
            connect=self.sub_connect, disconnect=self.sub_disconnect)

    def parse_command(self, message, channel):
        if self.queue is not None:
            print message
            self.queue.put(message)

    def sub_error(message):
        logging.ERROR(message)

    def sub_connect(self, channel):
        message = 'Connected to: %s' % channel
        logging.info(message)

    def sub_disconnect(self, message):
        logging.info(message)
