class MCQ:
    def __init__(self, data):
        self.question = data[0]
        self.option1 = data[1]
        self.option2 = data[2]
        self.option3 = data[3]
        self.option4 = data[4]
        self.Answer = int(data[5])
        self.userAns = None
        self.cursor_history = []
        self.selected_hand_id = None

    def update(self, cursor, bboxs, selected_hand_id):
        if selected_hand_id is not None and self.selected_hand_id is not None:
            if selected_hand_id != self.selected_hand_id:
                return

        self.cursor_history.append(cursor)
        if len(self.cursor_history) > 5:
            self.cursor_history.pop(0)

        avg_cursor = (
            sum(coord[0] for coord in self.cursor_history) / len(self.cursor_history),
            sum(coord[1] for coord in self.cursor_history) / len(self.cursor_history),
        )

        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < avg_cursor[0] < x2 and y1 < avg_cursor[1] < y2:
                self.userAns = x + 1
