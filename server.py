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

# System validation for Pop!_OS (Linux) / Validación de entorno
if sys.platform!= 'linux':
    print(" EPCS requires the native Linux 'fork' method for descriptor inheritance.")
    sys.exit(1)

LOG_FILE = "chat_log.txt"
PORT = 5000

def logger_service(lock, message):
    """Writes to the log atomically using a Lock primitive. / Registro atómico sincronizado."""
    with lock:
        try:
            with open(LOG_FILE, "a") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f" {e}")

def client_handler(conn, addr, msg_queue, lock, client_list):
    """Subprocess dedicated to a specific client session. / Subproceso para sesión de cliente."""
    user_alias = "Unknown"
    try:
        # User Identification Phase / Fase de Identificación
        user_alias = conn.recv(1024).decode('utf-8')
        join_msg = f"SYSTEM: {user_alias} has joined the session from {addr}"
        msg_queue.put(join_msg)
        logger_service(lock, join_msg)

        # Message Reception Loop / Bucle de recepción
        while True:
            data = conn.recv(1024).decode('utf-8')
            
            # Detect disconnection or exit command / Detección de salida
            if not data or data == "/exit":
                break
            
            full_msg = f"{user_alias}: {data}"
            msg_queue.put(full_msg)
            logger_service(lock, full_msg)
            
    except (ConnectionResetError, BrokenPipeError):
        print(f"[INFO] Connection lost abruptly with {user_alias}")
    finally:
        # Critical: Remove from shared list and broadcast exit / Limpieza y notificación de salida
        if conn in client_list:
            client_list.remove(conn)
        
        exit_msg = f"SYSTEM: {user_alias} has left the chat."
        msg_queue.put(exit_msg)
        logger_service(lock, exit_msg)
        conn.close()

def broadcaster(msg_queue, client_list):
    """Independent process that replicates messages to all active nodes. / Difusión MIMD."""
    while True:
        # Blocks until a new message enters the IPC bus / Bloquea hasta nuevo mensaje en cola
        msg = msg_queue.get() 
        
        # Iterate over a copy to ensure thread-safety / Iteración segura sobre copia
        for client_conn in list(client_list):
            try:
                client_conn.send(f"\r{msg}\n> ".encode('utf-8'))
            except (BrokenPipeError, OSError):
                # Clean up stale socket if broadcaster detects a failure / Purga de socket fallido
                if client_conn in client_list:
                    client_list.remove(client_conn)

if __name__ == "__main__":
    # IPC and Shared Memory Initialization / Inicialización de recursos compartidos
    manager = mp.Manager()
    active_clients = manager.list()
    message_bus = mp.Queue()
    file_lock = mp.Lock()

    # Network Setup / Configuración de red
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable immediate port reuse on Linux / Reutilización inmediata de puerto
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_sock.bind(('0.0.0.0', PORT))
        server_sock.listen(10)
    except OSError as e:
        print(f" Port {PORT} is busy. Action: sudo fuser -k {PORT}/tcp")
        sys.exit(1)

    # Launch dedicated broadcast worker / Iniciar trabajador de difusión
    mp.Process(target=broadcaster, args=(message_bus, active_clients), daemon=True).start()

    print(f"[INFO] EPCS Server v{__version__} active on port {PORT}. (Pop!_OS/Linux Optimized)")

    try:
        while True:
            # Block until a node requests entry / Bloquea hasta petición de conexión
            conn, addr = server_sock.accept()
            active_clients.append(conn)
            
            # Spawn worker process with full argument list / Instanciación de proceso trabajador
            p = mp.Process(
                target=client_handler, 
                args=(conn, addr, message_bus, file_lock, active_clients)
            )
            p.start()
    except KeyboardInterrupt:
        print("\n[INFO] Graceful server shutdown initiated. Releasing socket...")
    finally:
        server_sock.close(
