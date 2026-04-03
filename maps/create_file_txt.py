# Tạo 10 file: 1.txt đến 10.txt
for i in range(1, 20):
    # filename = f"maps/{i}.txt"
    filename = f"maps/{i}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{i}")
    print(f"Đã tạo: {filename}")