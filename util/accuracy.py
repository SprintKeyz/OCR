class Accuracy:
    def __init__(self):
        self.accuracy_scores = []
        self.skipped_characters = []
        self.ghost_characters = []
        self.character_accuracy = []

    def append_calculation(self, student, response_data):
        checked_a = student[1]
        checked_b = student[2]
        checked_c = student[3]

        resp_a = response_data[0]
        resp_b = response_data[1]
        resp_c = response_data[2]

        # get accuracy by comparing the checked values to the response values and assinging a 1 for correct and 0 for incorrect
        accuracy_a = 1 if checked_a == resp_a else 0
        accuracy_b = 1 if checked_b == resp_b else 0
        accuracy_c = 1 if checked_c == resp_c else 0

        # sum the accuracies and divide by 3 to get the overall accuracy
        overall_accuracy = (accuracy_a + accuracy_b + accuracy_c) / 3
        self.accuracy_scores.append([student[0], overall_accuracy])

        # check for any skipped characters and append the character that was skipped
        skipped_chars_a = [char for char in checked_a if char not in resp_a]
        skipped_chars_b = [char for char in checked_b if char not in resp_b]
        skipped_chars_c = [char for char in checked_c if char not in resp_c]
        skipped_chars = skipped_chars_a + skipped_chars_b + skipped_chars_c
        self.skipped_characters.append([student[0], skipped_chars])

        # check for any ghost characters and append the character that was added
        ghost_chars_a = [char for char in resp_a if char not in checked_a]
        ghost_chars_b = [char for char in resp_b if char not in checked_b]
        ghost_chars_c = [char for char in resp_c if char not in checked_c]
        ghost_chars = ghost_chars_a + ghost_chars_b + ghost_chars_c
        self.ghost_characters.append([student[0], ghost_chars])

        # get the character accuracy by comparing the checked values to the response values and assinging a 1 for correct and 0 for incorrect
        char_accuracy_a = sum([1 if checked_a[i] == resp_a[i] else 0 for i in range(min(len(checked_a), len(resp_a)))]) / min(len(checked_a), len(resp_a))
        char_accuracy_b = sum([1 if checked_b[i] == resp_b[i] else 0 for i in range(min(len(checked_b), len(resp_b)))]) / min(len(checked_b), len(resp_b))
        char_accuracy_c = sum([1 if checked_c[i] == resp_c[i] else 0 for i in range(min(len(checked_c), len(resp_c)))]) / min(len(checked_c), len(resp_c))
        overall_char_accuracy = (char_accuracy_a + char_accuracy_b + char_accuracy_c) / 3
        self.character_accuracy.append([student[0], overall_char_accuracy])
        
    def get_overall_word_accuracy(self):
        return sum([score[1] for score in self.accuracy_scores]) / len(self.accuracy_scores)
    
    def get_overall_character_accuracy(self):
        return sum([score[1] for score in self.character_accuracy]) / len(self.character_accuracy)
    
    def get_min_word_accuracy(self):
        return min(self.accuracy_scores, key=lambda x: x[1])
    
    def get_min_character_accuracy(self):
        return min(self.character_accuracy, key=lambda x: x[1])
    
    def get_most_common_skipped_characters(self):
        most_common_skipped_characters = {}
        for student in self.skipped_characters:
            for char in student[1]:
                if char in most_common_skipped_characters:
                    most_common_skipped_characters[char] += 1
                else:
                    most_common_skipped_characters[char] = 1
        return sorted(most_common_skipped_characters.items(), key=lambda x: x[1], reverse=True)
    
    def get_most_common_ghost_characters(self):
        most_common_ghost_characters = {}
        for student in self.ghost_characters:
            for char in student[1]:
                if char in most_common_ghost_characters:
                    most_common_ghost_characters[char] += 1
                else:
                    most_common_ghost_characters[char] = 1
        return sorted(most_common_ghost_characters.items(), key=lambda x: x[1], reverse=True)
    
    def get_ghost_character_count(self):
        return len(self.get_most_common_ghost_characters())
    
    def get_skipped_character_count(self):
        return len(self.get_most_common_skipped_characters())
    
    def get_accuracy_scores(self):
        return self.accuracy_scores
    
    def get_character_accuracy(self):
        return self.character_accuracy
    
    def get_skipped_characters(self):
        return self.skipped_characters
    
    def get_ghost_characters(self):
        return self.ghost_characters
    
    def get_accuracy_by_student(self, student_id):
        return [score[1] for score in self.accuracy_scores if score[0] == student_id][0]
    
    def get_students_by_accuracy_high_to_low(self):
        return sorted(self.accuracy_scores, key=lambda x: x[1], reverse=True)
    
    def get_students_by_accuracy_low_to_high(self):
        return sorted(self.accuracy_scores, key=lambda x: x[1])