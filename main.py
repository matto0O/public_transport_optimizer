import fetch_data

if __name__ == '__main__':
    fetch_data.fetch_all()
    for line in fetch_data.lines:
        print(line)
        print("\n")
