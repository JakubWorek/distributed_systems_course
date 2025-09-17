import pika
import sys
import json
import time
import random
import threading
from config import *

class Dostawca:
    def __init__(self, nazwa_dostawcy, obslugiwane_typy):
        self.nazwa_dostawcy = nazwa_dostawcy
        self.obslugiwane_typy = obslugiwane_typy
        self.nr_zlecenia_wewnetrzny = 0

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
        self.channel.exchange_declare(exchange=ADMIN_BROADCAST_DOSTAWCY_EXCHANGE, exchange_type='fanout')

        for typ in self.obslugiwane_typy:
            queue_name = f"{ZLECENIA_QUEUE_PREFIX}{typ}"
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(exchange=ZLECENIA_EXCHANGE, queue=queue_name, routing_key=typ)
            thread = threading.Thread(target=self.start_consuming_zlecenia, args=(queue_name,), daemon=True)
            thread.start()
            print(f"[*] Dostawca '{self.nazwa_dostawcy}' nasłuchuje na zlecenia '{typ}' na kolejce '{queue_name}'")

        self.admin_msg_queue_name = f"{self.nazwa_dostawcy}{ADMIN_MSG_QUEUE_SUFFIX}"
        self.channel.queue_declare(queue=self.admin_msg_queue_name, durable=True)
        self.channel.queue_bind(exchange=ADMIN_BROADCAST_DOSTAWCY_EXCHANGE, queue=self.admin_msg_queue_name)
        
        admin_thread = threading.Thread(target=self.start_consuming_admin_msgs, daemon=True)
        admin_thread.start()
        print(f"[*] Dostawca '{self.nazwa_dostawcy}' nasłuchuje na wiadomości admina na '{self.admin_msg_queue_name}'")


    def callback_zlecenie(self, ch, method, properties, body):
        zlecenie = json.loads(body.decode())
        typ_sprzetu = zlecenie['typ_sprzetu']
        nazwa_ekipy_zlecajacej = zlecenie['nazwa_ekipy']
        id_zlecenia_ekipy = zlecenie.get('zlecenie_id', 'BRAK_ID_EKIPY')

        print(f"[{self.nazwa_dostawcy}] Otrzymano zlecenie na '{typ_sprzetu}' od '{nazwa_ekipy_zlecajacej}' (ID Ekipy: {id_zlecenia_ekipy})")
        
        self.nr_zlecenia_wewnetrzny += 1
        id_zlecenia_dostawcy = f"{self.nazwa_dostawcy}-{self.nr_zlecenia_wewnetrzny}"

        potwierdzenie = {
            'nazwa_dostawcy': self.nazwa_dostawcy,
            'id_zlecenia_dostawcy': id_zlecenia_dostawcy,
            'typ_sprzetu_potwierdzony': typ_sprzetu,
            'dla_ekipy': nazwa_ekipy_zlecajacej,
            'oryginalne_id_zlecenia_ekipy': id_zlecenia_ekipy
        }
        body_potwierdzenia = json.dumps(potwierdzenie)

        self.channel.basic_publish(
            exchange=POTWIERDZENIA_EXCHANGE,
            routing_key=nazwa_ekipy_zlecajacej,
            body=body_potwierdzenia,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        
        print(f"[{self.nazwa_dostawcy}] Wysłano potwierdzenie: {potwierdzenie}")

        log_wiadomosc = {'typ_logu': 'potwierdzenie', 'dane': potwierdzenie, 'zrodlo': self.nazwa_dostawcy}
        body_logu = json.dumps(log_wiadomosc)
        self.channel.basic_publish(
            exchange=ADMIN_LOG_EXCHANGE,
            routing_key='',
            body=body_logu,
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def callback_admin_msg(self, ch, method, properties, body):
        wiadomosc = body.decode()
        print(f"[{self.nazwa_dostawcy}] Wiadomość od ADMINA: {wiadomosc}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming_zlecenia(self, queue_name):
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        ch = conn.channel()
        ch.basic_qos(prefetch_count=1)
        ch.basic_consume(queue=queue_name, on_message_callback=self.callback_zlecenie)
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

    def close(self):
        self.connection.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Użycie: python dostawca.py <nazwa_dostawcy> <typ_sprzetu_1> [typ_sprzetu_2 ...]")
        sys.exit(1)

    nazwa_dostawcy_arg = sys.argv[1]
    typy_sprzetu_args = sys.argv[2:]
    
    dostawca = Dostawca(nazwa_dostawcy_arg, typy_sprzetu_args)

    print(f"[*] Dostawca '{nazwa_dostawcy_arg}' gotowy. Obsługuje: {', '.join(typy_sprzetu_args)}.")
    print(f"[*] Naciśnij CTRL+C aby zakończyć.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"Zamykanie dostawcy {nazwa_dostawcy_arg}...")
    finally:
        dostawca.close()