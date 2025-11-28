#!/usr/bin/env python3
import argparse
import csv
import sys

# Новые размеры команд в байтах
INSTRUCTION_SIZES = {
    28: 6,  # LOAD_CONST (B=2, C=3)
    24: 9,  # LOAD_MEM (B=2, C=3, D=3)
    17: 4,  # STORE (B=2, C=2)
    19: 9   # SQRT (B=2, C=3, D=3)
}


# ======== CSV → Промежуточное представление ======== #
def parse_csv(path: str):
    program = []
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for line_num, row in enumerate(reader, start=1):
                if not row or row[0].strip() == "":
                    continue

                try:
                    A = int(row[0])
                except:
                    raise ValueError(f"Ошибка в строке {line_num}: opcode A не число.")

                if A not in INSTRUCTION_SIZES:
                    raise ValueError(f"Неизвестная команда A={A} (строка {line_num})")

                def val(i):
                    return int(row[i]) if i < len(row) and row[i].strip() not in ("","-") else 0

                program.append({
                    "A": A,
                    "B": val(1),
                    "C": val(2),
                    "D": val(3),
                    "size": INSTRUCTION_SIZES[A]
                })
        return program

    except FileNotFoundError:
        print("Файл не найден:", path)
        sys.exit(1)
    except Exception as e:
        print("Ошибка:", e)
        sys.exit(1)


def print_intermediate(program):
    print("\n=== Внутреннее представление ===")
    for cmd in program:
        print(" ".join(f"{k}={v}" for k,v in cmd.items()))
    print("===============================\n")


# ======== Генерация бинарного кода ======== #
def encode_instruction(cmd: dict) -> bytes:
    A, B, C, D = cmd["A"], cmd["B"], cmd["C"], cmd["D"]
    out = bytearray()
    out.append(A)  # 1 байт — опкод

    if A == 28:  # LOAD_CONST (B=2, C=3)
        out += B.to_bytes(2, 'little')
        out += C.to_bytes(3, 'little')

    elif A == 24:  # LOAD_MEM (B=2, C=3, D=3)
        out += B.to_bytes(2, 'little')
        out += C.to_bytes(3, 'little')
        out += D.to_bytes(3, 'little')

    elif A == 17:  # STORE (B=2, C=2)
        out += B.to_bytes(2, 'little')
        out += C.to_bytes(2, 'little')

    elif A == 19:  # SQRT (B=2, C=3, D=3)
        out += B.to_bytes(2, 'little')
        out += C.to_bytes(3, 'little')
        out += D.to_bytes(3, 'little')

    return bytes(out)


def write_binary(program, output_path):
    with open(output_path, "wb") as f:
        for cmd in program:
            f.write(encode_instruction(cmd))


def assemble(program, output_path, test_mode):
    write_binary(program, output_path)
    print(f"Собрано команд: {len(program)}")
    if test_mode:
        print("=== Машинный код (HEX) ===")
        full = b''.join(encode_instruction(cmd) for cmd in program)
        print(" ".join(f"{x:02X}" for x in full))
        print("==========================\n")


# ======== CLI ======== #
def main():
    parser = argparse.ArgumentParser(description="UVM Assembler (Stage 2 fixed for Stage 3)")
    parser.add_argument("input", type=str, help="CSV вход")
    parser.add_argument("output", type=str, help="BIN выход")
    parser.add_argument("--test", action="store_true", help="режим тестирования")
    args = parser.parse_args()

    program = parse_csv(args.input)

    if args.test:
        print_intermediate(program)

    assemble(program, args.output, args.test)


if __name__ == "__main__":
    main()

# python etap2.py samples/test_program.csv out.bin --test
