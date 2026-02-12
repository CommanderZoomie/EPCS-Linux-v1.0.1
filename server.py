# Copyright 2026 Anthony Nicholas Carmen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Anthony Nicholas Carmen"
__copyright__ = "Copyright 2026, Anthony Nicholas Carmen"
__license__ = "Apache-2.0"
__version__ = "1.0.1"

import multiprocessing as mp
import socket
import sys
import time

# Configuración de entorno Linux
if sys.platform!= 'linux':
    print(" Este sistema requiere el método 'fork' nativo de Linux.")
    sys.exit(1)

LOG_FILE = "chat_log.txt"
PORT = 5000

def logger_service(lock, message):
    """Escribe en el log de forma atómica usando un Lock primitive."""
    with lock:
        with open(LOG_FILE, "a") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")

def client_handler(conn, addr, msg_queue, lock, client_list):
    """Subproceso con rutina de limpieza garantizada."""
    user_alias = "Unknown"
    try:
        # Identification
        user_alias = conn.recv(1024).decode('utf-8')
        join_msg = f"SYSTEM: {user_alias} joined from {addr}"
        msg_queue.put(join_msg)
        logger_service(lock, join_msg)

        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data or data == "/exit":
                break
            
            full_msg = f"{user_alias}: {data}"
            msg_queue.put(full_msg)
            logger_service(lock, full_msg)
            
    except (ConnectionResetError, BrokenPipeError):
        print(f" Connection lost abruptly with {user_alias}")
    finally:
        # Action: Remove from shared list before notifying others
        if conn in client_list:
            client_list.remove(conn)
        
        exit_msg = f"SYSTEM: {user_alias} has left the chat."
        msg_queue.put(exit_msg)
        logger_service(lock, exit_msg)
        conn.close()

def broadcaster(msg_queue, client_list):
    """Proceso de difusión con tolerancia a fallos por socket."""
    while True:
        msg = msg_queue.get()
        # Iterar sobre una copia para evitar errores de mutación durante el envío
        for client_conn in list(client_list):
            try:
                client_conn.send(f"\r{msg}\n> ".encode('utf-8'))
            except (BrokenPipeError, OSError):
                # Action: Purge stale socket if it's still in the list
                if client_conn in client_list:
                    client_list.remove(client_conn)

if __name__ == "__main__":
    # Inicialización de recursos IPC
    manager = mp.Manager()
    active_clients = manager.list()
    message_bus = mp.Queue()
    file_lock = mp.Lock()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', PORT))
    server_sock.listen(10)

    # Iniciar proceso de difusión global
    mp.Process(target=broadcaster, args=(message_bus, active_clients), daemon=True).start()

    print(f"[INFO] EPCS Server activo en puerto {PORT}. MIMD Mode ON.")

    try:
        while True:
            conn, addr = server_sock.accept()
            active_clients.append(conn)
            # Spawning de proceso trabajador por cliente
            p = mp.Process(target=client_handler, args=(conn, addr, message_bus, file_lock))
            p.start()
    except KeyboardInterrupt:
        print("\n[INFO] Apagado grácil del servidor.")
    finally:
        server_sock.close()
