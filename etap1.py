#!/usr/bin/env python3
import argparse
import csv
import sys

# Опкоды УВМ
INSTRUCTION_SIZES = {
    28: 6,  # LOAD_CONST
    24: 6,  # LOAD_MEM
    17: 5,  # STORE
    19: 6   # SQRT
}

def parse_csv(path: str):
    program = []
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for line_num, row in enumerate(reader, start=1):
                if not row or len(row) == 0:
                    continue  # пропуск пустых строк

                try:
                    A = int(row[0])
                except:
                    raise ValueError(f"Ошибка в строке {line_num}: opcode A не число")

                if A not in INSTRUCTION_SIZES:
                    raise ValueError(f"Неизвестная команда A={A} (строка {line_num})")

                # безопасное извлечение полей
                def val(i):
                    return int(row[i]) if i < len(row) and row[i].strip() != "" and row[i] != "-" else None

                entry = {
                    "A": A,
                    "B": val(1),
                    "C": val(2),
                    "D": val(3),
                    "size": INSTRUCTION_SIZES[A]
                }
                program.append(entry)

        return program

    except FileNotFoundError:
        print("Файл не найден:", path)
        sys.exit(1)
    except Exception as e:
        print("Ошибка:", e)
        sys.exit(1)


def write_binary(program, output_path):
    with open(output_path, "wb") as f:
        for cmd in program:
            f.write(cmd["A"].to_bytes(1, "little"))
            if cmd["B"] is not None: f.write(cmd["B"].to_bytes(2, "little", signed=False))
            if cmd["C"] is not None: f.write(cmd["C"].to_bytes(2, "little", signed=False))
            if cmd["D"] is not None: f.write(cmd["D"].to_bytes(2, "little", signed=False))


def print_intermediate(program):
    for cmd in program:
        fields = " ".join(f"{k}={v}" for k,v in cmd.items())
        print(fields)


def main():
    parser = argparse.ArgumentParser(description="UVM assembler — Этап 1")
    parser.add_argument("input", type=str, help="путь к CSV-файлу программы")
    parser.add_argument("output", type=str, help="путь к бинарному файлу результата")
    parser.add_argument("--test", action="store_true", help="режим тестирования")
    args = parser.parse_args()

    program = parse_csv(args.input)

    if args.test:
        print("\n===== ВНУТРЕННЕЕ ПРЕДСТАВЛЕНИЕ =====\n")
        print_intermediate(program)
        print("\n===== END =====\n")

    write_binary(program, args.output)
    print("Сборка завершена. Файл создан:", args.output)


if __name__ == "__main__":
    main()
