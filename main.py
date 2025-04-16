import os
import random
import json

shuffle_questions_enabled = False
shuffle_answers_enabled = False
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

def load_settings():
    global shuffle_questions_enabled, shuffle_answers_enabled
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            shuffle_questions_enabled = settings.get('shuffle_questions', False)
            shuffle_answers_enabled = settings.get('shuffle_answers', False)
    except FileNotFoundError:
        pass 
    except Exception as e:
        print(f"Ошибка загрузки настроек: {str(e)}")

def save_settings():
    settings = {
        'shuffle_questions': shuffle_questions_enabled,
        'shuffle_answers': shuffle_answers_enabled
    }
    try:
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения настроек: {str(e)}")


def parse_questions(file_path):
    questions = []
    current_question = None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('#'):
                if current_question is not None:
                    questions.append(current_question)
                question_text = line[1:].strip()
                current_question = {
                    'question_text': question_text,
                    'options': []
                }
            elif line.startswith('+') or line.startswith('-'):
                if current_question is None:
                    continue
                is_correct = line.startswith('+')
                option_text = line[1:].strip()
                current_question['options'].append({
                    'text': option_text,
                    'is_correct': is_correct
                })
        
        if current_question is not None:
            questions.append(current_question)
    
    return questions

def shuffle_questions(questions):
    random.shuffle(questions)

def shuffle_answers(question, shuffle=True):
    if shuffle:
        random.shuffle(question['options'])

def run_quiz(questions, shuffle_questions_flag=True, shuffle_answers_flag=True):
    score = 0
    total = len(questions)
    
    if shuffle_questions_flag:
        shuffle_questions(questions)
    
    for question in questions:
        shuffle_answers(question, shuffle=shuffle_answers_flag)
        
        print(f"\n{question['question_text']}")
        options = question['options']
        
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option['text']}")
        
        correct_indices = [i+1 for i, opt in enumerate(options) if opt['is_correct']]
        
        while True:
            try:
                user_input = input("Введите номера правильных ответов через пробел: ").strip()
                if not user_input:
                    selected = []
                else:
                    selected = list(map(int, user_input.split()))
                
                valid = all(1 <= num <= len(options) for num in selected)
                if not valid:
                    print(f"Ошибка: введите числа от 1 до {len(options)}")
                    continue
                
                selected_set = set(selected)
                correct_set = set(correct_indices)
                
                if selected_set == correct_set:
                    print("✓ Правильно!")
                    score += 1
                else:
                    print("✗ Неправильно")
                    if correct_indices:
                        print(f"Правильные ответы: {', '.join(map(str, correct_indices))}")
                
                break
            except ValueError:
                print("Ошибка: введите только числа, разделенные пробелами")
    
    print(f"\nРезультат: {score} из {total} правильных ответов")

def display_available_files(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    if not files:
        print("В папке нет текстовых файлов.")
        return None
    print("\nДоступные файлы:")
    for idx, file_name in enumerate(files, 1):
        print(f"{idx}. {file_name}")
    while True:
        try:
            choice = int(input("Выберите номер файла: "))
            if 1 <= choice <= len(files):
                return os.path.join(directory, files[choice - 1])
            else:
                print("Неверный выбор. Пожалуйста, выберите существующий номер.")
        except ValueError:
            print("Ошибка: введите число.")


#MAIN
def main_menu():
    while True:
        print("\nМЕНЮ:")
        print("1. Начать тестирование")
        print("2. Настройки тестирования")
        print("3. Выход")
        choice = input("Выберите действие: ")
        if choice == '1':
            directory = os.path.dirname(os.path.abspath(__file__))
            file_path = display_available_files(os.path.join(directory, "Texts"))
            if file_path:
                main(file_path, shuffle_questions_enabled, shuffle_answers_enabled)
        elif choice == '2':
            settings_menu()
        elif choice == '3':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

def settings_menu():
    while True:
        print("\nНАСТРОЙКИ ТЕСТИРОВАНИЯ:")
        print("1. Перемешивать вопросы")
        print("2. Перемешивать ответы")
        print("3. Вернуться в главное меню")
        choice = input("Выберите действие: ")
        if choice == '1':
            toggle_shuffle_questions()
        elif choice == '2':
            toggle_shuffle_answers()
        elif choice == '3':
            break
        else:
            print("Неверный выбор")

def toggle_shuffle_questions():
    global shuffle_questions_enabled
    shuffle_questions_enabled = not shuffle_questions_enabled
    save_settings()
    print(f"Перемешивание вопросов {'включено' if shuffle_questions_enabled else 'выключено'}.")

def toggle_shuffle_answers():
    global shuffle_answers_enabled
    shuffle_answers_enabled = not shuffle_answers_enabled
    save_settings()
    print(f"Перемешивание ответов {'включено' if shuffle_answers_enabled else 'выключено'}.")

def main(file_path=None, shuffle_questions_flag=False, shuffle_answers_flag=False):
    if file_path is None:
        file_path = input("Введите путь к файлу с тестами: ")
    
    if not os.path.exists(file_path):
        print("Ошибка: файл не найден")
        return
    
    try:
        questions = parse_questions(file_path)
        valid_questions = []
        
        for q in questions:
            if not q['options']:
                continue
            if not any(opt['is_correct'] for opt in q['options']):
                print(f"Вопрос '{q['question_text']}' пропущен (нет правильных ответов)")
                continue
            valid_questions.append(q)
        
        if not valid_questions:
            print("Нет валидных вопросов для тестирования")
            return
        
        print(f"\nНайдено вопросов: {len(valid_questions)}")
        input("Нажмите Enter чтобы начать... ")
        run_quiz(valid_questions, shuffle_questions_flag, shuffle_answers_flag)
        print("\nТестирование завершено. Возвращаемся в главное меню.")
    
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    print('Добро пожаловать в TestX. Репозиторий https://github.com/Lyups/TestX')
    load_settings()
    main_menu()