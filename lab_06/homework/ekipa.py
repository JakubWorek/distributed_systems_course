import pika
import sys
import uuid
import json
import time
import threading
from config import *

class Ekipa:
    def __init__(self, nazwa_ekipy):
        self.nazwa_ekipy = nazwa_ekipy
        max_retries = 10
        retry_delay = 5
        for i in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
                actor_name = getattr(self, 'nazwa_ekipy', getattr(self, 'nazwa_dostawcy', getattr(self, 'nazwa_admina', 'NieznanyAktor')))
                print(f"[*] {self.__class__.__name__} '{actor_name}' pomyślnie połączony z RabbitMQ.")
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"[*] {self.__class__.__name__} - Nie można połączyć się z RabbitMQ (próba {i+1}/{max_retries}): {e}. Ponawiam za {retry_delay}s...")
                if i + 1 == max_retries:
                    print(f"[*] {self.__class__.__name__} - Osiągnięto maksymalną liczbę prób połączenia. Przerywam.")
                    sys.exit(1)
                time.sleep(retry_delay)
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=ZLECENIA_EXCHANGE, exchange_type='direct')
        self.channel.exchange_declare(exchange=POTWIERDZENIA_EXCHANGE, exchange_type='direct')
        self.channel.exchange_declare(exchange=ADMIN_LOG_EXCHANGE, exchange_type='fanout')
        self.channel.exchange_declare(exchange=ADMIN_BROADCAST_EKIPY_EXCHANGE, exchange_type='fanout')


        self.reply_queue_name = f"{self.nazwa_ekipy}{REPLY_QUEUE_SUFFIX}"
        self.channel.queue_declare(queue=self.reply_queue_name, durable=True)
        self.channel.queue_bind(exchange=POTWIERDZENIA_EXCHANGE, queue=self.reply_queue_name, routing_key=self.nazwa_ekipy)
        
        self.admin_msg_queue_name = f"{self.nazwa_ekipy}{ADMIN_MSG_QUEUE_SUFFIX}"
        self.channel.queue_declare(queue=self.admin_msg_queue_name, durable=True)
        self.channel.queue_bind(exchange=ADMIN_BROADCAST_EKIPY_EXCHANGE, queue=self.admin_msg_queue_name)

        print(f"[*] Ekipa '{self.nazwa_ekipy}' gotowa. Nasłuchuje na '{self.reply_queue_name}' i '{self.admin_msg_queue_name}'")

        threading.Thread(target=self.start_consuming_replies, daemon=True).start()
        threading.Thread(target=self.start_consuming_admin_msgs, daemon=True).start()

    def callback_reply(self, ch, method, properties, body):
        potwierdzenie = json.loads(body.decode())
        print(f"[{self.nazwa_ekipy}] Otrzymano potwierdzenie: {potwierdzenie}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def callback_admin_msg(self, ch, method, properties, body):
        wiadomosc = body.decode()
        print(f"[{self.nazwa_ekipy}] Wiadomość od ADMINA: {wiadomosc}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming_replies(self):
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        ch = conn.channel()
        ch.basic_qos(prefetch_count=1)
        ch.basic_consume(queue=self.reply_queue_name, on_message_callback=self.callback_reply)
        try:
            ch.start_consuming()
        except KeyboardInterrupt:
            ch.stop_consuming()
        conn.close()

    def start_consuming_admin_msgs(self):
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        ch = conn.channel()
        ch.basic_qos(prefetch_count=1)
        ch.basic_consume(queue=self.admin_msg_queue_name, on_message_callback=self.callback_admin_msg)
        try:
            ch.start_consuming()
        except KeyboardInterrupt:
            ch.stop_consuming()
        conn.close()
        
    def wyslij_zlecenie(self, typ_sprzetu):
        zlecenie_id = str(uuid.uuid4())
        wiadomosc = {
            'nazwa_ekipy': self.nazwa_ekipy,
            'typ_sprzetu': typ_sprzetu,
            'zlecenie_id': zlecenie_id,
            'reply_to_ekipa_q_name': self.reply_queue_name
        }
        body = json.dumps(wiadomosc)

        self.channel.basic_publish(
            exchange=ZLECENIA_EXCHANGE,
            routing_key=typ_sprzetu,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                reply_to=self.reply_queue_name
            ))
        print(f"[{self.nazwa_ekipy}] Wysłano zlecenie: {typ_sprzetu} (ID: {zlecenie_id})")

        log_wiadomosc = {'typ_logu': 'zlecenie', 'dane': wiadomosc, 'zrodlo': self.nazwa_ekipy}
        body_logu = json.dumps(log_wiadomosc)
        self.channel.basic_publish(
            exchange=ADMIN_LOG_EXCHANGE,
            routing_key='',
            body=body_logu,
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )

    def close(self):
        self.connection.close()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        nazwa_ekipy_arg = sys.argv[1]
        if nazwa_ekipy_arg == "Ekipa1":
            ekipa = Ekipa(nazwa_ekipy_arg)
            time.sleep(5)
            print(f"Ekipa {nazwa_ekipy_arg} wysyła serię zleceń...")
            zlecenia_do_wyslania = ['tlen', 'tlen', 'buty', 'buty', 'plecak', 'plecak']
            for sprzet in zlecenia_do_wyslania:
                ekipa.wyslij_zlecenie(sprzet)
                time.sleep(0.2)

    if len(sys.argv) < 2:
        print(f"Użycie: python ekipa.py <nazwa_ekipy> [typ_sprzetu_1 typ_sprzetu_2 ...]")
        sys.exit(1)

    nazwa_ekipy_arg = sys.argv[1]
    ekipa = Ekipa(nazwa_ekipy_arg)

    if len(sys.argv) > 2:
        for i in range(2, len(sys.argv)):
            ekipa.wyslij_zlecenie(sys.argv[i])
            time.sleep(0.1)

    print(f"[*] Ekipa '{nazwa_ekipy_arg}' zakończyła wysyłanie zleceń (jeśli były). Nasłuchuje na odpowiedzi i wiadomości admina.")
    print(f"[*] Naciśnij CTRL+C aby zakończyć.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Zamykanie ekipy...")
    finally:
        ekipa.close()