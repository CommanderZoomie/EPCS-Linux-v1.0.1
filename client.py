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

import socket
import threading
import sys

def receive_loop(sock):
    """Hilo secundario para recepción asíncrona."""
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if not data: break
            print(data, end="")
        except:
            print("\n[INFO] Conexión cerrada por el servidor.")
            break

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect(('127.0.0.1', 5000))
        alias = input("Ingrese su alias empresarial: ")
        client.send(alias.encode('utf-8'))

        # Iniciar thread de escucha para no bloquear el input()
        threading.Thread(target=receive_loop, args=(client,), daemon=True).start()

        print(f"Bienvenido {alias}. Escriba su mensaje o '/exit' para salir.")
        while True:
            msg = input("> ")
            client.send(msg.encode('utf-8'))
            if msg == "/exit":
                break
    except Exception as e:
        print(f" No se pudo conectar al servidor: {e}")
    finally:
        client.close()
        sys.exit(0)
