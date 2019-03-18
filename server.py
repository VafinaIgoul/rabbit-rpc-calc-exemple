#!/usr/bin/env python
# coding: utf-8
import pika

# Подключаемся к брокеру на локальном хосте
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

# Создаем очередь 'calc_queue'.
#  В эту очередь будут приходить
# данные от клиента.
channel.queue_declare(queue='calc_queue')


def on_request(ch, method, props, body):
    u"""Обрабатывем, полученное из очереди сообщение
     и отправляем ответное."""
    data = body.split(' ')
    first = int(data[0])
    second = int(data[1])
    operation = data[2]
    if operation == '+':
        print("Add {0} to {1}" .format(first, second))
        response = first + second
    elif operation == '-':
        print("Subtract {0} from {1}".format(first, second))
        response = first - second
    elif operation == '*':
        print ("Multiple {0} to {1}".format(first, second))
        response = first * second
    elif operation == '/':
        print ("Division {0} to {1}".format(first, second))
        response = first/second
    else:
        response = 'Incorrect operation'
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=
                                                     props.correlation_id),
                     body=str(response))
    # Подтверждаем, что сообщение было обработано
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='calc_queue')

print(" [x] Awaiting Calculator requests")
channel.start_consuming()
