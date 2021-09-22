__author__ = "wahyudi@multidaya.id"

import pika
import logging
from _cConfig import _Common


LOGGER = logging.getLogger()
AMQP = None


def init(
    host=None,
    port=None,
    user=None,
    password=None
    ):
    global AMQP
    try:
        if host is None:
            host = _Common.AMQP_HOST
        if port is None:
            port = _Common.AMQP_PORT
        if user is None:
            user = _Common.AMQP_USER
        if password is None:
            password = _Common.AMQP_PASS
        config = 'amqp://'+user+':'+password+'@'+host+':'+port+'/%2f'
        params = pika.URLParameters(config)
        AMQP = pika.BlockingConnection(params)
        LOGGER.info(('AMQP Established', config))
    except Exception as e:
        LOGGER.warning((e))


def publish(
    channel='test-channel',
    message='Bla..Bla..Bla..',
    ):
    global AMQP
    result = False
    if AMQP is None:
        init()
    try:
        __channel = AMQP.channel()
        __channel.queue_declare(queue=channel)
        __channel.basic_publish(exchange='', routing_key=channel, body=message)
        result = True
    except Exception as e:
        LOGGER.warning((e))
    finally:
        if AMQP is not None:
            AMQP.close()
        return result


def callback(ch, method, properties, body):
    # TODO Finalise This Callback
    print(" [x] Received " + str(body))


def listen(channel=''):
    global AMQP
    if AMQP is None:
        init()
    try:
        __channel = AMQP.channel()
        __channel.basic_consume(queue=channel, on_message_callback=callback, auto_ack=True)
    except Exception as e:
        LOGGER.warning((e))
    finally:
        if AMQP is not None:
            AMQP.close()
