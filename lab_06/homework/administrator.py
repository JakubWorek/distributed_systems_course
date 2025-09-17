import pika
import sys
import json
import time
import threading
from config import *

class Administrator:
    def __init__(self, nazwa_admina="Admin"):
        self.nazwa_admina = nazwa_admina
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

        self.channel.exchange_declare(exchange=ADMIN_BROADCAST_EKIPY_EXCHANGE, exchange_type='fanout')
        self.channel.exchange_declare(exchange=ADMIN_BROADCAST_DOSTAWCY_EXCHANGE, exchange_type='fanout')
        self.channel.exchange_declare(exchange=ADMIN_LOG_EXCHANGE, exchange_type='fanout')

        self.channel.exchange_bind(destination=ADMIN_LOG_EXCHANGE, source=ADMIN_BROADCAST_EKIPY_EXCHANGE)
        self.channel.exchange_bind(destination=ADMIN_LOG_EXCHANGE, source=ADMIN_BROADCAST_DOSTAWCY_EXCHANGE)

        self.channel.queue_declare(queue=ADMIN_LOG_QUEUE, durable=True)
        self.channel.queue_bind(exchange=ADMIN_LOG_EXCHANGE, queue=ADMIN_LOG_QUEUE)
        
        print(f"[*] Administrator '{self.nazwa_admina}' gotowy. Nasłuchuje na logi w '{ADMIN_LOG_QUEUE}'.")

        threading.Thread(target=self.start_consuming_logs, daemon=True).start()

    def callback_log(self, ch, method, properties, body):
        try:
            source_exchange = method.exchange
            
            decoded_body = body.decode()
            log_data = json.loads(decoded_body)

            if 'typ_logu' in log_data and 'dane' in log_data:
                print(f"[{self.nazwa_admina}][LOG][{log_data.get('typ_logu','NIEZNANY_TYP').upper()} od {log_data.get('zrodlo','NIEZNANE_ZRODLO')}] Dane: {log_data['dane']}")
            else:
                print(f"[{self.nazwa_admina}][LOG z {source_exchange}] Odebrano (surowe): {decoded_body}")

        except json.JSONDecodeError:
            print(f"[{self.nazwa_admina}][LOG z {source_exchange}] Odebrano tekst (nie JSON): {body.decode()}")
        except Exception as e:
            print(f"[{self.nazwa_admina}][LOG z {source_exchange}] Błąd przetwarzania logu: {e}, body: {body}")
            
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming_logs(self):
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        ch = conn.channel()
        ch.basic_qos(prefetch_count=1)
        ch.basic_consume(queue=ADMIN_LOG_QUEUE, on_message_callback=self.callback_log)
        try:
            ch.start_consuming()
        except KeyboardInterrupt:
            ch.stop_consuming()
        conn.close()

    def wyslij_do_ekip(self, wiadomosc):
        print(f"[{self.nazwa_admina}] Wysyłam do EKIP: '{wiadomosc}'")
        self.channel.basic_publish(
            exchange=ADMIN_BROADCAST_EKIPY_EXCHANGE,
            routing_key='',
            body=wiadomosc
        )

    def wyslij_do_dostawcow(self, wiadomosc):
        print(f"[{self.nazwa_admina}] Wysyłam do DOSTAWCÓW: '{wiadomosc}'")
        self.channel.basic_publish(
            exchange=ADMIN_BROADCAST_DOSTAWCY_EXCHANGE,
            routing_key='',
            body=wiadomosc
        )

    def wyslij_do_wszystkich(self, wiadomosc):
        print(f"[{self.nazwa_admina}] Wysyłam do WSZYSTKICH: '{wiadomosc}'")
        self.wyslij_do_ekip(f"(DO WSZYSTKICH) {wiadomosc}")
        self.wyslij_do_dostawcow(f"(DO WSZYSTKICH) {wiadomosc}")

    def close(self):
        self.connection.close()

if __name__ == '__main__':
    autorun = False
    if len(sys.argv) > 1 and sys.argv[1] == "--autorun":
        autorun = True

    admin = Administrator()

    if autorun:
        print("[*] Administrator w trybie --autorun. Czekam chwilę na ustabilizowanie się systemu...")
        time.sleep(10)

        print("\n--- SCENARIUSZ ADMINA ---")
        admin.wyslij_do_ekip("Pilna wiadomość dla wszystkich ekip! Przygotujcie się na zmianę pogody.")
        time.sleep(1)
        admin.wyslij_do_dostawcow("Proszę o potwierdzenie dostępności sprzętu zimowego.")
        time.sleep(1)
        admin.wyslij_do_wszystkich("Uwaga! Jutro ćwiczenia ewakuacyjne w bazie.")
        time.sleep(5)
        print("--- KONIEC SCENARIUSZA ADMINA ---")
        print("[*] Administrator zakończył zadania w trybie --autorun. Pozostaje aktywny dla logów. Naciśnij CTRL+C aby zakończyć.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nZamykanie administratora (autorun)...")
        finally:
            admin.close()
    else:
        print(f"[*] Administrator gotowy. Wpisz komendę:")
        print(f"    ekipy <wiadomosc>   - wyślij do wszystkich ekip")
        print(f"    dostawcy <wiadomosc> - wyślij do wszystkich dostawców")
        print(f"    wszyscy <wiadomosc>  - wyślij do wszystkich")
        print(f"    exit                - zakończ")

        try:
            while True:
                try:
                    polecenie_input = input("> ")
                    if not polecenie_input.strip():
                        continue
                    
                    parts = polecenie_input.split(" ", 1)
                    command = parts[0].lower()
                    
                    message = ""
                    if len(parts) > 1:
                        message = parts[1]

                    if command == "ekipy":
                        if message:
                            admin.wyslij_do_ekip(message)
                        else:
                            print("Brak wiadomości do wysłania.")
                    elif command == "dostawcy":
                        if message:
                            admin.wyslij_do_dostawcow(message)
                        else:
                            print("Brak wiadomości do wysłania.")
                    elif command == "wszyscy":
                        if message:
                            admin.wyslij_do_wszystkich(message)
                        else:
                            print("Brak wiadomości do wysłania.")
                    elif command == "exit":
                        break
                    else:
                        print("Nieznana komenda.")
                except EOFError:
                    break
                except Exception as e:
                    print(f"Wystąpił błąd: {e}")

        except KeyboardInterrupt:
            print("\nZamykanie administratora...")
        finally:
            admin.close()