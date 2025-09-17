import logging
import subprocess
import time
import threading

from kazoo.client import KazooClient, KazooState
from kazoo.exceptions import NoNodeError, NodeExistsError
from kazoo.recipe.watchers import DataWatch, ChildrenWatch

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


ZK_HOSTS = 'localhost:2181,localhost:2182,localhost:2183'
NODE_A_PATH = "/a"


running_app_details = {
    "name_from_znode": None,
    "process_name_for_stop": None
}
app_lock = threading.Lock()

zk = KazooClient(hosts=ZK_HOSTS)

def _derive_process_name_for_stop(app_name_from_znode: str) -> str:
    """Pobiera nazwę procesu do użycia z Stop-Process (bez .exe)"""
    if app_name_from_znode.lower().endswith(".exe"):
        return app_name_from_znode[:-4]
    return app_name_from_znode

def start_external_app(app_name_from_znode: str):
    """Uruchamia zewnętrzną aplikację przez PowerShell."""
    global running_app_details
    with app_lock:
        if running_app_details["name_from_znode"] == app_name_from_znode:
            logging.info(f"Aplikacja '{app_name_from_znode}' już powinna być uruchomiona. Nie uruchamiam ponownie.")
            return

        if running_app_details["process_name_for_stop"]:
            stop_external_app(running_app_details["process_name_for_stop"])

        logging.info(f"Uruchamianie aplikacji: {app_name_from_znode}")
        try:
            subprocess.Popen(
                ["powershell", "-Command", f"Start-Process {app_name_from_znode}"],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            running_app_details["name_from_znode"] = app_name_from_znode
            running_app_details["process_name_for_stop"] = _derive_process_name_for_stop(app_name_from_znode)
            logging.info(f"Aplikacja '{app_name_from_znode}' (proces: '{running_app_details['process_name_for_stop']}') została uruchomiona.")
        except Exception as e:
            logging.error(f"Nie udało się uruchomić aplikacji {app_name_from_znode}: {e}")

def stop_external_app(process_name_for_stop: str):
    """Zatrzymuje zewnętrzną aplikację przez PowerShell."""
    global running_app_details
    logging.info(f"Zatrzymywanie aplikacji (nazwa procesu): {process_name_for_stop}")
    try:
        result = subprocess.run(
            ["powershell", "-Command", f"Get-Process '{process_name_for_stop}' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"],
            creationflags=subprocess.CREATE_NO_WINDOW,
            capture_output=True, text=True, check=False
        )
        if result.stdout:
            logging.debug(f"Stop-Process stdout: {result.stdout.strip()}")
        if result.stderr:
            logging.warning(f"Stop-Process stderr: {result.stderr.strip()}")
        
        logging.info(f"Wysłano polecenie zatrzymania dla aplikacji o nazwie procesu '{process_name_for_stop}'.")
    except Exception as e:
        logging.error(f"Nie udało się zatrzymać aplikacji o nazwie procesu {process_name_for_stop}: {e}")
    finally:
        with app_lock:
            if running_app_details["process_name_for_stop"] == process_name_for_stop:
                running_app_details["name_from_znode"] = None
                running_app_details["process_name_for_stop"] = None


@zk.DataWatch(NODE_A_PATH)
def watch_node_a(data, stat, event):
    """Obserwator dla znode 'a' (tworzenie, usuwanie, zmiana danych)."""
    global running_app_details
    with app_lock:
        current_process_to_stop = running_app_details["process_name_for_stop"]

    if event:
        logging.info(f"Zdarzenie dla {NODE_A_PATH}: typ={event.type}, stan={event.state}, ścieżka={event.path}")
    else:
        logging.info(f"Początkowy stan dla {NODE_A_PATH}: dane={'istnieją' if data else 'brak'}, stat={'istnieje' if stat else 'brak'}")


    if stat is None:
        if current_process_to_stop:
            logging.info(f"Węzeł {NODE_A_PATH} nie istnieje lub został usunięty. Zatrzymywanie aplikacji '{current_process_to_stop}'.")
            stop_external_app(current_process_to_stop)
        else:
            logging.info(f"Węzeł {NODE_A_PATH} nie istnieje, żadna aplikacja nie była śledzona.")
    else:
        if data:
            app_name_from_znode = data.decode('utf-8').strip()
            if not app_name_from_znode:
                logging.warning(f"Węzeł {NODE_A_PATH} istnieje, ale nie zawiera danych (nazwy aplikacji).")
                if current_process_to_stop:
                    logging.info(f"Dane w {NODE_A_PATH} są puste. Zatrzymywanie aplikacji '{current_process_to_stop}'.")
                    stop_external_app(current_process_to_stop)
                return

            logging.info(f"Węzeł {NODE_A_PATH} istnieje. Dane (nazwa aplikacji): {app_name_from_znode}")
            
            if running_app_details["name_from_znode"] != app_name_from_znode:
                start_external_app(app_name_from_znode)
            else:
                logging.info(f"Aplikacja '{app_name_from_znode}' już powinna być uruchomiona zgodnie z danymi w ZNode.")
        else:
            logging.warning(f"Węzeł {NODE_A_PATH} istnieje, ale nie zawiera danych (nazwy aplikacji).")
            if current_process_to_stop:
                logging.info(f"Dane w {NODE_A_PATH} są puste. Zatrzymywanie aplikacji '{current_process_to_stop}'.")
                stop_external_app(current_process_to_stop)


@zk.ChildrenWatch(NODE_A_PATH, send_event=True)
def watch_children_of_a(children, event):
    """Obserwator dla potomków węzła 'a'."""
    if event:
        logging.info(f"Zdarzenie dla potomków {NODE_A_PATH}: typ={event.type}, stan={event.state}, ścieżka={event.path}")

    if zk.exists(NODE_A_PATH):
        logging.info(f"Węzeł '{NODE_A_PATH}' ma obecnie {len(children)} potomków: {children}")
    else:
        logging.info(f"Próba odczytu potomków {NODE_A_PATH}, ale węzeł już nie istnieje.")


def print_zk_tree(path, indent=""):
    """Wyświetla strukturę drzewa znode'ów od podanej ścieżki."""
    if not zk.connected:
        logging.warning("Nie można wyświetlić drzewa - brak połączenia z ZooKeeperem.")
        return
    try:
        node_name = path.split("/")[-1] if path != "/" else "/"
        if not node_name: node_name = "/"
        
        data, stat = zk.get(path)
        node_info = f"- {node_name}"
        if data:
            try:
                node_info += f" [dane: '{data.decode('utf-8')}']"
            except UnicodeDecodeError:
                node_info += f" [dane: {len(data)} bajtów (binarne)]"
        
        print(f"{indent}{node_info}")
        
        children = zk.get_children(path)
        for child in sorted(children):
            child_path = f"{path}/{child}" if path != "/" else f"/{child}"
            print_zk_tree(child_path, indent + "  ")
            
    except NoNodeError:
        print(f"{indent}- {path.split('/')[-1]} (Węzeł nie istnieje)")
    except Exception as e:
        print(f"{indent}  Błąd przy dostępie do {path}: {e}")

def state_listener(state):
    if state == KazooState.LOST:
        logging.warning("Utracono połączenie z ZooKeeperem. Próba ponownego połączenia...")
    elif state == KazooState.SUSPENDED:
        logging.warning("Połączenie z ZooKeeperem zawieszone.")
    elif state == KazooState.CONNECTED:
        logging.info("Pomyślnie połączono z ZooKeeperem.")
    else:
        logging.info(f"Zmiana stanu połączenia ZooKeeper: {state}")

def main():
    zk.add_listener(state_listener)
    try:
        zk.start(timeout=20)
    except Exception as e:
        logging.error(f"Nie udało się połączyć z ZooKeeperem: {e}")
        return

    logging.info("Aplikacja uruchomiona. Nasłuchiwanie na zmiany w ZooKeeperze.")
    logging.info(f"Obserwowanie węzła: {NODE_A_PATH}")
    logging.info(f"Obserwowanie potomków węzła: {NODE_A_PATH}")

    print("\nAplikacja monitorująca ZooKeeper uruchomiona.")
    print("Dostępne komendy:")
    print("  tree - wyświetl drzewo potomków węzła /a")
    print("  exit - zakończ aplikację")

    try:
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                if cmd == 'tree':
                    if zk.exists(NODE_A_PATH):
                        print(f"Struktura drzewa dla '{NODE_A_PATH}':")
                        print_zk_tree(NODE_A_PATH)
                    else:
                        print(f"Węzeł '{NODE_A_PATH}' nie istnieje.")
                elif cmd == 'exit':
                    break
                else:
                    if cmd:
                        print(f"Nieznana komenda: {cmd}")
            except EOFError:
                logging.info("EOFError, prawdopodobnie koniec strumienia wejściowego. Kończenie pracy.")
                break
            except Exception as e:
                logging.error(f"Błąd w pętli głównej: {e}")
                time.sleep(1)


    except KeyboardInterrupt:
        logging.info("Przerwanie przez użytkownika (Ctrl+C).")
    finally:
        logging.info("Zamykanie aplikacji...")
        with app_lock:
            if running_app_details["process_name_for_stop"]:
                logging.info(f"Zatrzymywanie aplikacji '{running_app_details['process_name_for_stop']}' przy zamykaniu.")
                stop_external_app(running_app_details["process_name_for_stop"])
        
        if zk.connected:
            zk.stop()
        zk.close()
        logging.info("Aplikacja zakończona.")

if __name__ == "__main__":
    main()