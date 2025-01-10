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
            if len(self.points) >= 4:
                return
            h, w, _ = self.original_frame.shape
            x_original = int(x * w / param.shape[1])
            y_original = int(y * h / param.shape[0])
            self.points.append((x_original, y_original))
            cv2.circle(param, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Select Grid", param)

    def reset_points(self):
        """Reset the points to allow a new selection."""
        self.points = []
        self.result = ["_" for _ in range(9)]
        print("Points have been reset. Please select the corners again.")

    def extract_cells(self, frame):
        """Extract individual cells from the Tic-Tac-Toe grid using user-selected points."""
        rect = np.array(self.points, dtype="float32")
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
        """Detect if the cell contains a circle or a triangle."""
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 500:
                continue
            approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
            if len(approx) == 3:
                return "T"
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * (area / (perimeter * perimeter)) if perimeter > 0 else 0
            if circularity > 0.7 and area > 500:
                return "O"
        return "_"

    def draw_grid(self, warped):
        """Draw a 3x3 grid on the warped image."""
        height, width = warped.shape[:2]
        cell_width = width // 3
        cell_height = height // 3

        # Draw horizontal lines
        for i in range(1, 3):
            cv2.line(warped, (0, i * cell_height), (width, i * cell_height), (255, 255, 255), 2)

        # Draw vertical lines
        for i in range(1, 3):
            cv2.line(warped, (i * cell_width, 0), (i * cell_width, height), (255, 255, 255), 2)

    def mark_dead_zone(self, warped):
        """Mark the dead zone on the warped image."""
        height, width = warped.shape[:2]
        cell_width = width // 3
        cell_height = height // 3
        margin = int(min(cell_width, cell_height) * 0.08)

        overlay = warped.copy()

        # Iterate through cells and mark margins
        for i in range(3):
            for j in range(3):
                x_start = j * cell_width + margin
                y_start = i * cell_height + margin
                x_end = (j + 1) * cell_width - margin
                y_end = (i + 1) * cell_height - margin

                # Draw transparent overlay for dead zones
                cv2.rectangle(overlay, (x_start, y_start), (x_end, y_end), (0, 0, 255), -1)

        # Blend the overlay with transparency
        alpha = 0.3  # Transparency factor
        cv2.addWeighted(overlay, alpha, warped, 1 - alpha, 0, warped)

    def update_game_state(self, cells, warped):
        """Detect shapes in cells, update the game state, and overlay results."""
        cell_width = warped.shape[1] // 3
        cell_height = warped.shape[0] // 3

        for idx, cell in enumerate(cells):
            shape = self.detect_shape(cell)
            self.result[idx] = shape if shape else "_"

            # Overlay the detected shape
            row, col = divmod(idx, 3)
            x_center = int(col * cell_width + cell_width / 2)
            y_center = int(row * cell_height + cell_height / 2)

            if shape == "O":
                cv2.putText(warped, "O", (x_center - 15, y_center + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            elif shape == "T":
                cv2.putText(warped, "T", (x_center - 15, y_center + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)

    def get_current_board(self):
        """Return the current game board."""
        return [self.result[i:i + 3] for i in range(0, 9, 3)]

    def main(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            self.original_frame = frame.copy()
            resized_frame = cv2.resize(self.original_frame, (960, 720))
            cv2.imshow("Select Grid", resized_frame)
            cv2.setMouseCallback("Select Grid", self.click_event, resized_frame)

            while len(self.points) < 4:
                ret, frame = self.cap.read()
                if not ret:
                    break
                resized_frame = cv2.resize(frame, (960, 720))
                for point in self.points:
                    scaled_point = (int(point[0] * resized_frame.shape[1] / frame.shape[1]),
                                    int(point[1] * resized_frame.shape[0] / frame.shape[0]))
                    cv2.circle(resized_frame, scaled_point, 5, (0, 0, 255), -1)
                cv2.imshow("Select Grid", resized_frame)
                cv2.waitKey(1)

            cells, warped = self.extract_cells(self.original_frame)
            self.update_game_state(cells, warped)
            self.draw_grid(warped)
            self.mark_dead_zone(warped)
            cv2.imshow("Warped Grid", warped)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_points()

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    tictactoe_game = TicTacToe()
    tictactoe_game.main()
