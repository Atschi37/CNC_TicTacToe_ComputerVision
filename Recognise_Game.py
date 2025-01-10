import cv2
import numpy as np

class TicTacToe:
    def __init__(self):
        self.points = []
        self.original_frame = None
        self.cap = cv2.VideoCapture(0)
        self.result = ["_" for _ in range(9)]  # 3x3 Spielfeld initialisieren

    def click_event(self, event, x, y, flags, param):
        """Mouse click event to capture points."""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Wenn alle 4 Punkte schon gesetzt sind, nichts mehr tun
            if len(self.points) >= 4:
                return

            # Map points from resized frame to original frame
            h, w, _ = self.original_frame.shape
            x_original = int(x * w / param.shape[1])
            y_original = int(y * h / param.shape[0])
            self.points.append((x_original, y_original))
            cv2.circle(param, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Select Grid", param)

            # Show instructions for which point is being marked
            if len(self.points) == 0:
                print("Mark the top-left corner.")
            elif len(self.points) == 1:
                print("Mark the top-right corner.")
            elif len(self.points) == 2:
                print("Mark the bottom-right corner.")
            elif len(self.points) == 3:
                print("Mark the bottom-left corner.")
            elif len(self.points) == 4:
                print("All points are set.")

    def reset_points(self):
        """Reset the points to allow a new selection."""
        self.points = []
        self.result = ["_" for _ in range(9)]  # Reset the result grid
        print("Points have been reset. Please select the corners again.")

    def extract_cells(self, frame):
        """Extract individual cells from the Tic-Tac-Toe grid using user-selected points."""
        rect = np.array(self.points, dtype="float32")

        # Determine the width and height of the new perspective
        width = int(max(np.linalg.norm(rect[0] - rect[1]), np.linalg.norm(rect[2] - rect[3])))
        height = int(max(np.linalg.norm(rect[0] - rect[3]), np.linalg.norm(rect[1] - rect[2])))

        dst = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype="float32")

        matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(frame, matrix, (width, height))

        # Rotate the image to align properly if needed
        if width < height:
            warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)

        # Split into 3x3 cells
        cell_width = warped.shape[1] // 3
        cell_height = warped.shape[0] // 3
        cells = []

        for i in range(3):
            for j in range(3):
                x_start = j * cell_width
                y_start = i * cell_height
                cell = warped[y_start:y_start + cell_height, x_start:x_start + cell_width]
                cells.append(cell)

        return cells, warped

    def detect_shape(self, cell):
        """Detect if the cell contains a circle or an X."""
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Bessere Schwellenwertsetzung und Rauschunterdrückung
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Entferne kleine Konturen und Rauschen
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 200:  # Ignoriere kleine Konturen
                continue

            # Fit a bounding rectangle and check aspect ratio
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)

            # Circle detection based on circularity
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * (area / (perimeter * perimeter)) if perimeter > 0 else 0

            if circularity > 0.7 and area > 500:  # Eine Mindestfläche für den Kreis
                return "O"  # Circle

            # Cross detection based on aspect ratio and contour shape
            if 0.8 < aspect_ratio < 1.2 and len(contour) >= 4:
                return "X"

        # Wenn keine Form erkannt wurde, dann leer
        return None

    def update_game_state(self, cells):
        """Detect shapes in all cells and update the game state."""
        for idx, cell in enumerate(cells):
            shape = self.detect_shape(cell)
            self.result[idx] = shape if shape else "_"

    def get_current_board(self):
        """Return the current game board."""
        return [self.result[i:i + 3] for i in range(0, 9, 3)]

    def main(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            self.original_frame = frame.copy()

            # Resize the frame for a larger display window
            resized_frame = cv2.resize(self.original_frame, (960, 720))

            # Let the user select the grid points
            cv2.imshow("Select Grid", resized_frame)
            cv2.setMouseCallback("Select Grid", self.click_event, resized_frame)

            # Wait until 4 points are selected
            while len(self.points) < 4:
                ret, frame = self.cap.read()
                if not ret:
                    break
                self.original_frame = frame.copy()
                resized_frame = cv2.resize(self.original_frame, (960, 720))
                for point in self.points:
                    scaled_point = (int(point[0] * resized_frame.shape[1] / frame.shape[1]),
                                    int(point[1] * resized_frame.shape[0] / frame.shape[0]))
                    cv2.circle(resized_frame, scaled_point, 5, (0, 0, 255), -1)
                cv2.imshow("Select Grid", resized_frame)
                cv2.waitKey(1)

            # Extract cells using the selected points
            cells, warped = self.extract_cells(self.original_frame)
            self.update_game_state(cells)

            # Display the result in the console
            current_board = self.get_current_board()
            for row in current_board:
                print(row)
            print("\n")

            # Show warped grid
            cv2.imshow("Warped Grid", warped)

            # Handle key press for resetting points or quitting
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Press 'q' to quit
                break
            elif key == ord('r'):  # Press 'r' to reset the points
                self.reset_points()

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tictactoe_game = TicTacToe()
    tictactoe_game.main()
