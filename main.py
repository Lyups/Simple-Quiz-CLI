import os
import random
import json
from colorama import Fore, Style, init

init() # initialize colorama

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
    incorrectly_answered_questions = []
    questions_attempted = 0
    
    if shuffle_questions_flag:
        shuffle_questions(questions)
    
    for i, question in enumerate(questions):
        shuffle_answers(question, shuffle=shuffle_answers_flag)
        
        print(f"\n{Fore.CYAN}{question['question_text']}{Style.RESET_ALL}")
        options = question['options']
        
        for idx, option in enumerate(options, 1):
            print(f"{Fore.YELLOW}{idx}. {option['text']}{Style.RESET_ALL}")
        
        correct_indices = [i+1 for i, opt in enumerate(options) if opt['is_correct']]
        
        while True:
            try:
                user_input = input(f"{Fore.GREEN}Введите номера правильных ответов через пробел (или \"quit\"/\"выйти\" для выхода): {Style.RESET_ALL}").strip().lower()
                
                if user_input in ['quit', 'выйти']:
                    print(f"{Fore.CYAN}Выход из тестирования...{Style.RESET_ALL}")
                    solved_questions = questions_attempted
                    incorrect_questions_count = len(incorrectly_answered_questions)
                    unattempted_questions = total - solved_questions
                    print(f"{Fore.MAGENTA}\nСтатистика на момент выхода:{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Решено вопросов: {solved_questions}{Style.RESET_ALL}")
                    print(f"{Fore.RED}Ошибок: {incorrect_questions_count}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Не приступали: {unattempted_questions}{Style.RESET_ALL}")
                    return None

                questions_attempted += 1

                if not user_input:
                    print(f"{Fore.RED}Пожалуйста, введите номера ответов или 'quit'/\'выйти' для выхода.{Style.RESET_ALL}")
                    continue # Продолжаем цикл, чтобы запросить ввод снова
                else:
                    selected = list(map(int, user_input.split()))
                
                valid = all(1 <= num <= len(options) for num in selected)
                if not valid:
                    print(f"{Fore.RED}Ошибка: введите числа от 1 до {len(options)}{Style.RESET_ALL}")
                    continue
                
                selected_set = set(selected)
                correct_set = set(correct_indices)
                
                if selected_set == correct_set:
                    print(f"{Fore.GREEN}✓ Правильно!{Style.RESET_ALL}")
                    score += 1
                else:
                    print(f"{Fore.RED}✗ Неправильно{Style.RESET_ALL}")
                    if correct_indices:
                        print(f"{Fore.YELLOW}Правильные ответы: {', '.join(map(str, correct_indices))}{Style.RESET_ALL}")
                    incorrectly_answered_questions.append(question)
                
                break
            except ValueError:
                print(f"{Fore.RED}Ошибка: введите только числа, разделенные пробелами{Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}Результат: {score} из {total} правильных ответов{Style.RESET_ALL}")
    return incorrectly_answered_questions

def display_available_files(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    if not files:
        print(f"{Fore.RED}В папке нет текстовых файлов.{Style.RESET_ALL}")
        return None
    print(f"{Fore.BLUE}\nДоступные файлы:{Style.RESET_ALL}")
    for idx, file_name in enumerate(files, 1):
        print(f"{Fore.YELLOW}{idx}. {file_name}{Style.RESET_ALL}")
    while True:
        try:
            choice = int(input(f"{Fore.GREEN}Выберите номер файла: {Style.RESET_ALL}"))
            if 1 <= choice <= len(files):
                return os.path.join(directory, files[choice - 1])
            else:
                print(f"{Fore.RED}Неверный выбор. Пожалуйста, выберите существующий номер.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Ошибка: введите число.{Style.RESET_ALL}")


#MAIN
def main_menu():
    while True:
        print(f"{Fore.BLUE}\nМЕНЮ:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1. Начать тестирование{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. Настройки тестирования{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. Показать текущие настройки{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4. Выход{Style.RESET_ALL}")
        choice = input(f"{Fore.GREEN}Выберите действие: {Style.RESET_ALL}")
        if choice == '1':
            directory = os.path.dirname(os.path.abspath(__file__))
            file_path = display_available_files(os.path.join(directory, "Texts"))
            if file_path:
                main(file_path, shuffle_questions_enabled, shuffle_answers_enabled)
        elif choice == '2':
            settings_menu()
        elif choice == '3':
            display_current_settings()
        elif choice == '4':
            print(f"{Fore.CYAN}Выход из программы.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Неверный выбор. Пожалуйста, попробуйте снова.{Style.RESET_ALL}")

def settings_menu():
    while True:
        print(f"{Fore.BLUE}\nНАСТРОЙКИ ТЕСТИРОВАНИЯ:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1. Перемешивать вопросы{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. Перемешивать ответы{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. Вернуться в главное меню{Style.RESET_ALL}")
        choice = input(f"{Fore.GREEN}Выберите действие: {Style.RESET_ALL}")
        if choice == '1':
            toggle_shuffle_questions()
        elif choice == '2':
            toggle_shuffle_answers()
        elif choice == '3':
            break
        else:
            print(f"{Fore.RED}Неверный выбор{Style.RESET_ALL}")

def toggle_shuffle_questions():
    global shuffle_questions_enabled
    shuffle_questions_enabled = not shuffle_questions_enabled
    save_settings()
    print(f"{Fore.GREEN}Перемешивание вопросов {'включено' if shuffle_questions_enabled else 'выключено'}.{Style.RESET_ALL}")

def toggle_shuffle_answers():
    global shuffle_answers_enabled
    shuffle_answers_enabled = not shuffle_answers_enabled
    save_settings()
    print(f"{Fore.GREEN}Перемешивание ответов {'включено' if shuffle_answers_enabled else 'выключено'}.{Style.RESET_ALL}")

def display_current_settings():
    print(f"{Fore.BLUE}\nТЕКУЩИЕ НАСТРОЙКИ:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Перемешивать вопросы: {'Включено' if shuffle_questions_enabled else 'Выключено'}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Перемешивать ответы: {'Включено' if shuffle_answers_enabled else 'Выключено'}{Style.RESET_ALL}")
    input(f"{Fore.GREEN}Нажмите Enter, чтобы продолжить...{Style.RESET_ALL}")

def main(file_path=None, shuffle_questions_flag=False, shuffle_answers_flag=False):
    if file_path is None:
        file_path = input(f"{Fore.GREEN}Введите путь к файлу с тестами: {Style.RESET_ALL}")
    
    if not os.path.exists(file_path):
        print(f"{Fore.RED}Ошибка: файл не найден{Style.RESET_ALL}")
        return
    
    try:
        questions = parse_questions(file_path)
        valid_questions = []
        
        for q in questions:
            if not q['options']:
                continue
            if not any(opt['is_correct'] for opt in q['options']):
                print(f"{Fore.YELLOW}Вопрос '{q['question_text']}' пропущен (нет правильных ответов){Style.RESET_ALL}")
                continue
            valid_questions.append(q)
        
        if not valid_questions:
            print(f"{Fore.RED}Нет валидных вопросов для тестирования{Style.RESET_ALL}")
            return
        
        print(f"{Fore.BLUE}\nНайдено вопросов: {len(valid_questions)}{Style.RESET_ALL}")
        input(f"{Fore.GREEN}Нажмите Enter чтобы начать... {Style.RESET_ALL}")
        incorrectly_answered_questions = run_quiz(valid_questions, shuffle_questions_flag, shuffle_answers_flag)

        if incorrectly_answered_questions is None:
            return # Пользователь вышел из викторины

        if incorrectly_answered_questions:
            while True:
                retry_choice = input(f"{Fore.YELLOW}У вас есть неправильные ответы. Хотите попробовать еще раз только неправильные вопросы? (да/нет): {Style.RESET_ALL}").strip().lower()
                if retry_choice == 'да':
                    print(f"{Fore.BLUE}\nПовторное тестирование неправильных вопросов...{Style.RESET_ALL}")
                    retried_incorrect_questions = run_quiz(incorrectly_answered_questions, shuffle_questions_flag, shuffle_answers_flag)
                    if retried_incorrect_questions is None:
                        return # Пользователь вышел во время повторного тестирования
                    break
                elif retry_choice == 'нет':
                    break
                else:
                    print(f"{Fore.RED}Неверный ввод. Пожалуйста, введите 'да' или 'нет'.{Style.RESET_ALL}")

        print(f"{Fore.CYAN}\nТестирование завершено. Возвращаемся в главное меню.{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}Произошла ошибка: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    print(f'{Fore.LIGHTMAGENTA_EX}Добро пожаловать в Simple Quiz CLI. Репозиторий https://github.com/Lyups/Simple-Quiz-CLI{Style.RESET_ALL}')
    load_settings()
    main_menu()