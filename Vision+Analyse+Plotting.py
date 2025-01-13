import Recognise_Game
import TicTacToeAI
import Gcode_Streamer
import threading
import serial
import time

game = Recognise_Game.TicTacToe()
def start_game():
    game.main()
port = Gcode_Streamer.select_port()

print("Verbinden mit GRBL-Controller.")
ser = serial.Serial(port, baudrate=115200, timeout=1)
ser.write(b'\r\n')
time.sleep(2)  # Warte auf GRBL-Start
ser.flushInput()
Gcode_Streamer.unlock_grbl(ser)
print("Verbunden mit GRBL-Controller.")

print("Starte Video Analyse...")
threading.Thread(target=start_game).start()
print("Video Analyse gestartet.")

while True:
    command = input("[1] Ursprung setzen und Kopf heben (G92)\n [2] G-Code streamen\n [3] Werkzeugkopf anheben\n [4] Besten Zug für T berechenen\n [5] Move to Scan Position\n [6] Automatisch besten Zug ausführen\n [7] Beenden\n")
    if command == "1":
        Gcode_Streamer.set_zero_point(ser)
        Gcode_Streamer.raise_toolhead(ser, 15)
    elif command == "2":
        gcode_file_path = input("Geben Sie den Pfad zur G-Code-Datei ein: ")
        Gcode_Streamer.stream_gcode(ser, gcode_file_path)
    elif command == "3":
        Gcode_Streamer.raise_toolhead(ser, 15)
    elif command == "4":
        current_board = game.get_current_board()
        print(current_board)
        winner, win_type = TicTacToeAI.is_winner(current_board, 'T')
        if winner:
            print(f"'T' wins! {win_type}")
        else:
            winner, win_type = TicTacToeAI.is_winner(current_board, 'O')
            if winner:
                print(f"'O' wins! {win_type}")
            else:
                best_move = TicTacToeAI.find_best_move(current_board)
                print(f"Best move for 'T' is: {best_move}")
    elif command == "5":
        Gcode_Streamer.stream_gcode(ser, "scanpos.ngc")
    elif command =="6":
        pass
    elif command == "7":
        break