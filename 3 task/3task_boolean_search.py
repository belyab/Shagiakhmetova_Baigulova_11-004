import json
import re

def load_index(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        index_data = file.readlines()

    inverted_index = {}
    for entry in index_data:
        entry_data = json.loads(entry)
        word = entry_data['word']
        inverted_index[word] = set(entry_data['inverted_array'])

    return inverted_index

def process_query(query, inverted_index):
    operators = [op.strip() for op in re.split(r'\b(AND|OR|NOT)\b|\(|\)', query) if op and op.strip()]
    operators = [op.strip() for op in operators if op.strip()]

    result_stack = []
    current_operator = None
    current_result = None

    for operator in operators:
        if operator == '(':
            result_stack.append((current_result, current_operator))
            current_result = None
            current_operator = None
        elif operator == ')':
            prev_result, prev_operator = result_stack.pop()
            if prev_operator == 'AND':
                current_result = prev_result.intersection(current_result) if current_result is not None else prev_result
            elif prev_operator == 'OR':
                current_result = prev_result.union(current_result) if current_result is not None else prev_result
            elif prev_operator == 'NOT':
                current_result = prev_result.difference(current_result) if current_result is not None else prev_result
            else:
                current_result = prev_result
        elif operator in {'AND', 'OR', 'NOT'}:
            current_operator = operator
        else:
            term = operator.lower()
            term_indices = inverted_index.get(term, set())

            if current_operator == 'AND':
                current_result = term_indices if current_result is None else current_result.intersection(term_indices)
            elif current_operator == 'OR':
                current_result = term_indices if current_result is None else current_result.union(term_indices)
            elif current_operator == 'NOT':
                current_result = term_indices if current_result is None else current_result.difference(term_indices)
            else:
                current_result = term_indices

    return current_result

if __name__ == '__main__':
    inverted_index = load_index('inverted_index.txt')

    while True:
        query = input('Введите ваш запрос (для выхода введите "exit"): ')
        if query.lower() == 'exit':
            break

        result = process_query(query, inverted_index)

        if result:
            print('Результат поиска:', result)
        else:
            print('Ничего не найдено.')
