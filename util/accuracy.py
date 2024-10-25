from util.benchmark import get_final_score, start_benchmark, banchmark_started, add_student
from Levenshtein import distance

class Accuracy:
    def __init__(self):
        self.accuracy_scores = []
        self.skipped_characters = []
        self.ghost_characters = []
        self.character_accuracy = []

    def append_calculation(self, student, response_data, verbose=False):
        if not banchmark_started():
            start_benchmark()

        add_student()

        checked_values = student[1:]  # Get all checked values
        response_values = response_data + ['-999999'] * (3 - len(response_data))  # Pad responses

        # Calculate accuracy
        accuracies = [1 if checked == response else 0 for checked, response in zip(checked_values, response_values)]
        overall_accuracy = sum(accuracies) / len(checked_values) if checked_values else 0
        self.accuracy_scores.append([student[0], overall_accuracy])

        # Check for skipped characters
        skipped_chars = [
            [char for char in checked if char not in response]
            for checked, response in zip(checked_values, response_values)
        ]

        all_skipped = [char for sublist in skipped_chars for char in sublist]  # Flatten the list
        self.skipped_characters.append([student[0], all_skipped])

        # Check for ghost characters
        ghost_chars = [
            [char for char in response if char not in checked]
            for checked, response in zip(checked_values, response_values)
        ]

        all_ghosts = [char for sublist in ghost_chars for char in sublist]  # Flatten the list
        self.ghost_characters.append([student[0], all_ghosts])

        # Calculate character accuracy (Levenshtein distance)
        char_accuracies = [
            1 - (distance(checked, response) / max(len(checked), len(response)))
            for checked, response in zip(checked_values, response_values)
        ]
        overall_char_accuracy = sum(char_accuracies) / len(checked_values) if checked_values else 0
        self.character_accuracy.append([student[0], overall_char_accuracy])

        if verbose:
            print(f'Student {student[0]} accuracy: {round(overall_accuracy * 100, 3)}%')
            print(f'Student {student[0]} character accuracy: {round(overall_char_accuracy * 100, 3)}%')
            print(f'Student {student[0]} skipped characters: {all_skipped}')
            print(f'Student {student[0]} ghost characters: {all_ghosts}')
            print()
        
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
    
    def get_final_score(self):
        return round(get_final_score(self.get_overall_word_accuracy(), self.get_overall_character_accuracy()), 3)
    
    def print_report(self):
        # overall accuracy
        print()
        print()
        print('---------------------------------')
        print(f'Overall word accuracy: {round(self.get_overall_word_accuracy() * 100, 3)}%')
        print(f'Overall character accuracy: {round(self.get_overall_character_accuracy() * 100, 3)}%')
        print('---------------------------------')
        print(f'Minimum word accuracy: {self.get_min_word_accuracy()[0]}, {round(self.get_min_word_accuracy()[1] * 100, 3)}%')
        print(f'Minimum character accuracy: {self.get_min_character_accuracy()[0]}, {round(self.get_min_character_accuracy()[1] * 100)}%')
        print('---------------------------------')
        if len(self.get_most_common_skipped_characters()) > 0:
            print(f'Most common skipped characters: {self.get_most_common_skipped_characters()[0][0]}, {self.get_most_common_skipped_characters()[0][1]} times')
        if len(self.get_most_common_ghost_characters()) > 0:
            print(f'Most common ghost characters: {self.get_most_common_ghost_characters()[0][0]}, {self.get_most_common_ghost_characters()[0][1]} times')
        print('---------------------------------')
        
    def return_report_as_string(self):
        resp_a =  f'Overall word accuracy: {round(self.get_overall_word_accuracy() * 100, 3)}%\n' + \
                f'Overall character accuracy: {round(self.get_overall_character_accuracy() * 100, 3)}%\n' + \
                f'Minimum word accuracy: {self.get_min_word_accuracy()[0]}, {round(self.get_min_word_accuracy()[1] * 100, 3)}%\n' + \
                f'Minimum character accuracy: {self.get_min_character_accuracy()[0]}, {round(self.get_min_character_accuracy()[1] * 100)}%\n'
                
        resp_b = ''
        if len(self.get_most_common_skipped_characters()) > 0:
            resp_b += f'Most common skipped characters: {self.get_most_common_skipped_characters()[0][0]}, {self.get_most_common_skipped_characters()[0][1]} times\n'
        if len(self.get_most_common_ghost_characters()) > 0:
            resp_b += f'Most common ghost characters: {self.get_most_common_ghost_characters()[0][0]}, {self.get_most_common_ghost_characters()[0][1]} times\n'
            
        return resp_a + resp_b