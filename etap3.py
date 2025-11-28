#!/usr/bin/env python3
import argparse
import json
import sys

# Размер команд (для декодирования)
INSTRUCTION_SIZES = {
    28: 6,  # LOAD_CONST (B:2, C:3)
    24: 9,  # LOAD_MEM (B:2, C:3, D:3)
    17: 5,  # STORE (B:2, C:2)
    19: 9   # SQRT (B:2, C:3, D:3)
}



# ======== ДЕКОДИРОВАНИЕ БАЙТОВОЙ КОМАНДЫ ======== #
def decode_instruction(data: bytes, offset: int):
    if offset >= len(data):
        return None, offset
    A = data[offset]
    size = INSTRUCTION_SIZES.get(A)
    if size is None:
        raise ValueError(f"Неизвестный опкод {A} на позиции {offset}")
    chunk = data[offset:offset+size]
    B = C = D = None
    if A == 28:  # LOAD_CONST
        B = int.from_bytes(chunk[1:3], 'little')
        C = int.from_bytes(chunk[3:6], 'little')
    elif A == 24:  # LOAD_MEM
        B = int.from_bytes(chunk[1:3], 'little')
        C = int.from_bytes(chunk[3:6], 'little')
        D = int.from_bytes(chunk[6:9], 'little')
    elif A == 17:  # STORE
        B = int.from_bytes(chunk[1:3], 'little')
        C = int.from_bytes(chunk[3:5], 'little')
    elif A == 19:  # SQRT
        B = int.from_bytes(chunk[1:3], 'little')
        C = int.from_bytes(chunk[3:6], 'little')
        D = int.from_bytes(chunk[6:9], 'little')

    return {"A": A, "B": B, "C": C, "D": D}, offset + size


# ======== ИНТЕРПРЕТАТОР ======== #
class UVM:
    def __init__(self, memory_size=4096):
        self.memory = [0] * memory_size  # объединённая память данных и команд
        self.pc = 0  # указатель на текущую команду

    def load_program(self, binary_path):
        with open(binary_path, "rb") as f:
            self.program = f.read()

    def step(self):
        if self.pc >= len(self.program):
            return False
        instr, next_pc = decode_instruction(self.program, self.pc)
        print(f"PC={self.pc} | EXECUTE: {instr}")  # <-- вывод перед выполнением
        self.execute(instr)
        self.pc = next_pc
        return True

    def run(self):
        while self.step():
            pass

    def ensure_memory(self, addr):
        if addr >= len(self.memory):
            self.memory.extend([0] * (addr - len(self.memory) + 1))

    def execute(self, cmd):
        A, B, C, D = cmd["A"], cmd["B"], cmd["C"], cmd["D"]
        if A == 28:  # LOAD_CONST
            self.ensure_memory(B)
            self.memory[B] = C
        elif A == 24:  # LOAD_MEM
            self.ensure_memory(B + C - 1)
            self.ensure_memory(D + C - 1)
            for i in range(C):
                self.memory[B+i] = self.memory[D+i]
        elif A == 17:  # STORE
            self.ensure_memory(B)
            self.ensure_memory(C)
            self.memory[C] = self.memory[B]
        elif A == 19:  # SQRT
            self.ensure_memory(B)
            self.ensure_memory(D)
            import math
            self.memory[D] = int(math.isqrt(self.memory[B]))
        else:
            raise ValueError(f"Неизвестная команда A={A}")

    def dump_memory(self, output_path, start=0, end=None):
        if end is None or end > len(self.memory):
            end = len(self.memory)
        dump = {str(i): self.memory[i] for i in range(start, end)}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dump, f, indent=2)


# ======== CLI ======== #
def main():
    parser = argparse.ArgumentParser(description="UVM Interpreter (Stage 3)")
    parser.add_argument("input", type=str, help="BIN вход")
    parser.add_argument("dump", type=str, help="JSON дамп памяти")
    parser.add_argument("--start", type=int, default=0, help="Начало диапазона дампа")
    parser.add_argument("--end", type=int, default=None, help="Конец диапазона дампа")
    args = parser.parse_args()

    uvm = UVM(memory_size=2048)
    uvm.load_program(args.input)
    uvm.run()
    uvm.dump_memory(args.dump, start=args.start, end=args.end)
    print(f"Программа выполнена. Дамп памяти сохранён в {args.dump}")


if __name__ == "__main__":
    main()
