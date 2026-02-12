# EPCS-Linux-v1.0.1

//English/Español//


///


1. Overview / Descripción:

   -Problem: The Python Global Interpreter Lock (GIL) prevents true parallelism in multithreaded applications, causing performance bottlenecks in real-time communication systems.
   
   -Solution: EPCS-Linux-v1.0.1 utilizes the multiprocessing library and the native Linux fork start method to achieve process-level parallelism. By assigning each client connection to an independent CPU core, the system ensures zero-blocking I/O and sub-millisecond broadcast latency.


   -Problema: El Global Interpreter Lock (GIL) de Python impide el paralelismo real en aplicaciones multihilo, causando cuellos de botella en sistemas de comunicación en tiempo real.
   
   -Solución: EPCS-Linux-v1.0.1 utiliza la librería multiprocessing y el método nativo fork de Linux para lograr paralelismo a nivel de procesos. Al asignar cada conexión de cliente a un núcleo de CPU independiente, el sistema garantiza I/O sin bloqueos y una latencia de difusión mínima.


///


2. Technical Features / Características Técnicas:

   -2.1. Architecture / Arquitectura: MIMD (Multiple Instruction, Multiple Data) centralized Client-Server model. / Modelo Cliente-Servidor centralizado bajo taxonomía MIMD.

   -2.2. Parallelism / Paralelismo: Dynamic process-per-client allocation via multiprocessing.Process. / Asignación dinámica de un proceso por cliente mediante multiprocessing.Process.

   -2.3. IPC / Comunicación Interprocesos: Asynchronous message bus utilizing multiprocessing.Queue. / Bus de mensajes asíncrono utilizando multiprocessing.Queue.

   -2.4. Synchronization / Sincronización: Thread-safe persistent logging to chat_log.txt using multiprocessing.Lock. / Registro persistente seguro mediante primitivas multiprocessing.Lock.

   -2.5. Networking / Red: Reliable TCP Stream Sockets (SOCK_STREAM) for ordered delivery. / Sockets de flujo TCP fiables para una entrega de datos ordenada.

   -2.6. OS Optimization / Optimización de SO: Native support for Linux socket descriptor inheritance. / Soporte nativo para la herencia de descriptores de socket en Linux.


///


3. Installation & Execution / Instalación y Ejecución
    -Strictly optimized for Pop!_OS / Ubuntu environments.
    -Optimizado estrictamente para entornos Pop!_OS / Ubuntu.


   -3.1. Prerequisites / Requisitos:

      -3.1.1. Python 3.10+

      -3.1.2. Linux Kernel 5.15+ (Required for native fork behavior / Requerido para comportamiento fork nativo).


   -3.2. Steps / Pasos:

      -3.2.1. Clone / Clonar: git clone https://github.com/CommanderZoomie/EPCS-Linux-v1.0.1.git cd EPCS-Linux-v1.0.1

      -3.2.2. Initialize Server / Iniciar Servidor: python3 server.py

      -3.2.3. Launch Clients / Iniciar Clientes: python3 client.py


///


4. Maintenance Guide / Guía de Mantenimiento:
   
   -4.1. Backend (Server Logic / Lógica del Servidor):

      -4.1.1. Process Lifecycle / Ciclo de Vida: The main process executes an infinite loop on socket.accept(). When a connection is detected, the descriptor is cloned into a worker subprocess. / El proceso principal ejecuta un bucle infinito en socket.accept(). Al detectar una conexión, el descriptor se clona en un subproceso trabajador.

      -4.1.2. Broadcasting / Difusión: A dedicated worker process monitors the shared Queue to trigger .send() operations across the active client registry. / Un proceso trabajador dedicado monitorea la Queue compartida para disparar operaciones .send() en el registro de clientes activos.

      -4.1.3. Critical Sections / Secciones Críticas: Every write operation to chat_log.txt is protected by a multiprocessing.Lock to ensure audit integrity. / Cada operación de escritura en chat_log.txt está protegida por un multiprocessing.Lock para asegurar la integridad de la auditoría.


   -4.2.Frontend (Client Logic / Lógica del Cliente):

      -4.2.1. Concurrency / Concurrencia: Implements a hybrid model using threading.Thread(daemon=True) for async data reception without blocking user input(). / Implementa un modelo híbrido usando threading.Thread(daemon=True) para recepción asíncrona sin bloquear el input() del usuario.

      -4.2.2. Error Handling / Manejo de Errores: Utilizes exception trapping for BrokenPipeError to ensure clean resource release on exit. / Utiliza captura de excepciones para BrokenPipeError para asegurar la liberación limpia de recursos al salir.


///


5. Troubleshooting / Resolución de Problemas

    -5.1. Issue: Address already in use

      -5.1.1. Cause / Causa: Port 5000 is occupied by a stale process. / Puerto 5000 ocupado por proceso zombi.

      -5.1.2. Action / Acción: Run sudo fuser -k 5000/tcp to purge the port. / Ejecutar sudo fuser -k 5000/tcp para purgar el puerto.


    -5.2. Issue: ConnectionRefusedError

      -5.2.1. Cause / Causa: Server node is inactive or firewall blocked. / Servidor inactivo o bloqueado por firewall.

      -5.2.2. Action / Acción: Check status with ps aux | grep server.py or allow port with sudo ufw allow 5000/tcp. / Verificar estado con ps aux | grep server.py o habilitar puerto con sudo ufw allow 5000/tcp.


    -5.3. Issue: PickleError

      -5.3.1. Cause / Causa: Non-Linux environment usage. / Uso en entorno no Linux.

      -5.3.2. Action / Acción: Switch to Pop!_OS/Linux to enable fork inheritance. / Cambiar a Pop!_OS/Linux para habilitar la herencia por fork.


///


6. License / Licencia

This Caso Práctico is licensed under the Apache License 2.0. It includes an explicit patent grant and is ready for enterprise integration and professional contracting. See the LICENSE and NOTICE files for details.

Este Caso Práctico está bajo la licencia Apache License 2.0. Incluye una concesión explícita de patentes y está listo para integración empresarial y contratación profesional. Consulte los archivos LICENSE y NOTICE para más detalles.


///


Author / Autor: Anthony Nicholas Carmen 
Repository / Repositorio:(https://github.com/CommanderZoomie/EPCS-Linux-v1.0.1)


///
