def excel_reader_standalone(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            data.append(line.strip().split(','))  # Assuming CSV formatted
    return data

# Example usage:
if __name__ == '__main__':
    filename = 'example.csv'
    data = excel_reader_standalone(filename)
    for row in data:
        print(row)