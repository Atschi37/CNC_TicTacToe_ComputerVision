import serial
import serial.tools.list_ports
import time

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def set_home(serial_port, baud_rate=115200):
    with serial.Serial(serial_port, baud_rate) as ser:
        # Warte, bis die Verbindung hergestellt ist
        time.sleep(2)
        
        # Sende den Befehl zum Setzen des Home-Punkts
        ser.write(b'$H\n')
        
        # Warte auf die Antwort des Controllers
        response = ser.readline().decode('utf-8').strip()
        print(f'Set Home: Received: {response}')
        
        # Warte kurz, um Überlastung zu vermeiden
        time.sleep(0.1)

def stream_gcode(file_path, serial_port, baud_rate=115200):
    # Öffne die serielle Verbindung
    with serial.Serial(serial_port, baud_rate) as ser:
        # Warte, bis die Verbindung hergestellt ist
        time.sleep(2)
        
        # Öffne die Gcode-Datei
        with open(file_path, 'r') as file:
            for line in file:
                # Entferne Leerzeichen und Zeilenumbrüche
                gcode_line = line.strip()
                
                if gcode_line:
                    # Sende die Gcode-Zeile an den GRBL-Controller
                    ser.write((gcode_line + '\n').encode('utf-8'))
                    
                    # Warte auf die Antwort des Controllers
                    response = ser.readline().decode('utf-8').strip()
                    print(f'Sent: {gcode_line} | Received: {response}')
                    
                    # Warte kurz, um Überlastung zu vermeiden
                    time.sleep(0.1)

if __name__ == "__main__":
    ports = list_serial_ports()
    if not ports:
        print("Keine seriellen Ports gefunden.")
    else:
        print("Verfügbare serielle Ports:")
        for i, port in enumerate(ports):
            print(f"{i}: {port}")
        
        port_index = int(input("Wähle den seriellen Port aus (Nummer eingeben): "))
        serial_port = ports[port_index]
        baud_rate = 115200
        gcode_file_path = 'path_to_your_gcode_file.gcode'
        
        # Setze den Home-Punkt
        set_home(serial_port, baud_rate)
        
        # Streame die Gcode-Datei
        stream_gcode(gcode_file_path, serial_port, baud_rate)