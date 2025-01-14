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

def draw_win(win_type, ser):
    if win_type == "Row 0":
        Gcode_Streamer.stream_gcode(ser, "gcode/wh0.ngc")
    elif win_type == "Row 1":
        Gcode_Streamer.stream_gcode(ser, "gcode/wh1.ngc")
    elif win_type == "Row 2":
        Gcode_Streamer.stream_gcode(ser, "gcode/wh2.ngc")
    elif win_type == "Column 0":
        Gcode_Streamer.stream_gcode(ser, "gcode/wv0.ngc")
    elif win_type == "Column 1":
        Gcode_Streamer.stream_gcode(ser, "gcode/wv1.ngc")
    elif win_type == "Column 2":
        Gcode_Streamer.stream_gcode(ser, "gcode/wv2.ngc")
    elif win_type == "Main diagonal":
        Gcode_Streamer.stream_gcode(ser, "gcode/wdl-r.ngc")
    elif win_type == "Anti-diagonal":
        Gcode_Streamer.stream_gcode(ser, "gcode/wdr-l.ngc")
    Gcode_Streamer.raise_toolhead(ser, 15)

def draw_move(move, ser):
    if move == (0, 0):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_0-0.ngc")
    elif move == (0, 1):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_0-1.ngc")
    elif move == (0, 2):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_0-2.ngc")
    elif move == (1, 0):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_1-0.ngc")
    elif move == (1, 1):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_1-1.ngc")
    elif move == (1, 2):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_1-2.ngc")
    elif move == (2, 0):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_2-0.ngc")
    elif move == (2, 1):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_2-1.ngc")
    elif move == (2, 2):
        Gcode_Streamer.stream_gcode(ser, "gcode/dreieck_2-2.ngc")
    Gcode_Streamer.stream_gcode(ser, "gcode/scanpos.ngc")

while True:
    command = input(" [1] Ursprung setzen und Kopf heben (G92)\n [2] G-Code streamen\n [3] Werkzeugkopf anheben\n [4] Besten Zug für T berechenen\n [5] Move to Scan Position\n [6] Automatisch besten Zug ausführen\n [7] Grid+scanpos\n [8] Full Setup\n [9] Beenden\n")
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
        Gcode_Streamer.stream_gcode(ser, "gcode/scanpos.ngc")
    elif command =="6":

        current_board = game.get_current_board()
        print(current_board)
        winner, win_type = TicTacToeAI.is_winner(current_board, 'T')
        if winner:#Check if 'T' wins and draw Line to mark win
            print(f"'T' wins! {win_type}")
            draw_win(win_type, ser)
        else:
            winner, win_type = TicTacToeAI.is_winner(current_board, 'O')
            if winner:# Check if 'O' wins and draw Line to mark win
                print(f"'O' wins! {win_type}")
                draw_win(win_type, ser)
            else: #Find and draw best move

                best_move = TicTacToeAI.find_best_move(current_board)
                print(f"Best move for 'T' is: {best_move}")
                draw_move(best_move, ser)
    elif command == "7":
        Gcode_Streamer.stream_gcode(ser, "gcode/grid.ngc")
        Gcode_Streamer.stream_gcode(ser, "gcode/scanpos.ngc")
    elif command == "8":
        Gcode_Streamer.set_zero_point(ser)
        Gcode_Streamer.raise_toolhead(ser, 15)
        Gcode_Streamer.stream_gcode(ser, "gcode/grid.ngc")
        Gcode_Streamer.stream_gcode(ser, "gcode/scanpos.ngc")
    elif command == "9":
        break



    elif command == "7":
        break