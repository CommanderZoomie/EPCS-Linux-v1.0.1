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
