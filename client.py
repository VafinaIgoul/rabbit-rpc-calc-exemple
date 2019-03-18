#!/usr/bin/env python
# coding: utf-8
import pika
import uuid


class CalculateClient(object):
    u"""Клиент, который через очердь, обращается
    к приложению-серверу."""
    def __init__(self):
        self.response = None
        # Подключились к брокеру на локальном хосте
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        # Создали очередь, которая завершит работу
        #  после окнчания работы CalculateClient.
        #  Эта очередь получает результат работы сервера.
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        # Подключаемся к очерди
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        u"""Функция, обрабатывающая очередь с результатом от сервера."""
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, first, second, operation):
        u"""Функционал клиента."""
        self.corr_id = str(uuid.uuid4())
        # Публикуем сообщение в очередь calc_queue сервера
        self.channel.basic_publish(exchange='',
                                   routing_key='calc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to=self.callback_queue,
                                         correlation_id=self.corr_id,
                                         ),
                                   body="{0} {1} {2}".format(
                                       first, second, operation))
        while self.response is None:
            # Делаем запрос в очередь клиента
            #  пока не получим результат
            self.connection.process_data_events()
        return self.response

calculate = CalculateClient()

# Принмаем из консоли 2 числа и оператор. Отправляем все
#  на сервер, от которого полуаем результат и публикуем его
while True:
    try:
        first_argument = input("Enter first arg:\n")
        second_argument = input("Enter second arg:\n")
        operation = raw_input("Import operation:\n")
        response = calculate.call(first_argument,
                                  second_argument,
                                  operation)
        print(" Result {0}".format(response))
    except EOFError:
        print 'finish'
        break
