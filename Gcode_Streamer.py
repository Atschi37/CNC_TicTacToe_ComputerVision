import serial
import serial.tools.list_ports
import time

def list_ports():
    """List available serial ports."""
    ports = serial.tools.list_ports.comports()
    for i, port in enumerate(ports):
        print(f"[{i}] {port.device}")
    return ports

def select_port():
    """Let the user select a serial port."""
    ports = list_ports()
    if not ports:
        print("Keine verfügbaren Ports gefunden.")
        return None
    
    while True:
        try:
            selection = int(input("Wählen Sie einen Port aus (Nummer eingeben): "))
            if 0 <= selection < len(ports):
                return ports[selection].device
            else:
                print("Ungültige Auswahl. Bitte erneut versuchen.")
        except ValueError:
            print("Bitte eine gültige Zahl eingeben.")

def send_command(serial_connection, command):
    """Send a single command to the GRBL controller and wait for completion."""
    serial_connection.write((command + '\n').encode())
    while True:
        response = serial_connection.readline().decode().strip()
        if response:
            print(f"GRBL: {response}")
        if response == "ok":
            break
        elif response.startswith("error"):
            raise Exception(f"GRBL-Fehler: {response}")

def unlock_grbl(serial_connection):
    """Unlock the GRBL controller if it is in alarm state."""
    print("Entsperre GRBL (Alarm Lock aufheben)...")
    send_command(serial_connection, "$X")

def set_zero_point(serial_connection):
    """Set the current position as the zero point."""
    print("Setze aktuellen Standort als Ursprung...")
    send_command(serial_connection, "G92 X0 Y0 Z0")

def stream_gcode(serial_connection, file_path):
    """Stream a G-code (.ngc) file to the GRBL controller."""
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('%') and not line.startswith(';'):
                    print(f"Sende: {line}")
                    send_command(serial_connection, line)
        print("G-Code-Streaming abgeschlossen.")
    except FileNotFoundError:
        print(f"Datei {file_path} nicht gefunden.")
    except Exception as e:
        print(f"Fehler beim Streamen der Datei: {e}")

def set_feedrate(serial_connection, feedrate):
    """Set the feedrate (F value) for the GRBL controller."""
    print(f"Setze Feedrate auf {feedrate}...")
    send_command(serial_connection, f"F{feedrate}")

def main():
    print("GRBL Controller Python Interface")

    port = select_port()
    if not port:
        return

    # Pfad zur G-Code-Datei hier festlegen
    gcode_file_path = "gcode/grid.ngc"  # Ersetze "example.gcode" durch den tatsächlichen Pfad

    try:
        with serial.Serial(port, baudrate=115200, timeout=1) as ser:
            print("Verbunden mit GRBL-Controller.")

            # Initialisierung von GRBL
            ser.write(b'\r\n')
            time.sleep(2)  # Warte auf GRBL-Start
            ser.flushInput()

            # Alarm Lock entsperren, falls erforderlich
            unlock_grbl(ser)

            # Hauptmenü
            while True:
                print("\nOptionen:")
                print("[1] Ursprung setzen (G92)")
                print("[2] G-Code streamen")
                print("[3] Feedrate setzen")
                print("[4] Beenden")

                choice = input("Wählen Sie eine Option: ")

                if choice == "1":
                    set_zero_point(ser)
                elif choice == "2":
                    stream_gcode(ser, gcode_file_path)
                elif choice == "3":
                    try:
                        feedrate = float(input("Geben Sie die gewünschte Feedrate ein: "))
                        set_feedrate(ser, feedrate)
                    except ValueError:
                        print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
                elif choice == "4":
                    print("Beende Programm.")
                    break
                else:
                    print("Ungültige Auswahl. Bitte erneut versuchen.")

    except serial.SerialException as e:
        print(f"Fehler beim Verbinden mit dem Port: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    main()
