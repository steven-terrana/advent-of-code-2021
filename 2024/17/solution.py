class Computer:
    def __init__(self, a, b, c, program):
        self.a = a
        self.b = b
        self.c = c
        self.program = program
        self.reversed_program = list(reversed(program))
        self.i = 0
        self.out = []

    def reset(self, a):
        self.a = a
        self.b = 0
        self.c = 0
        self.out = []

    def combo(self, operand):
        if 0 <= operand <= 3:
            return operand
        elif operand == 4:
            return self.a
        elif operand == 5:
            return self.b
        elif operand == 6:
            return self.c
        elif operand == 7:
            raise Exception("unexpected operand 7 provided")

    def execute(self):
        while self.i + 1 < len(self.program):
            opcode, operand = self.program[self.i : self.i + 2]
            if opcode == 0:
                self.a = int(self.a / 2 ** self.combo(operand))
            elif opcode == 1:
                self.b = self.b ^ operand
            elif opcode == 2:
                self.b = self.combo(operand) % 8
            elif opcode == 3:
                if self.a == 0:
                    break
                self.i = operand
                continue
            elif opcode == 4:
                self.b = self.b ^ self.c
            elif opcode == 5:
                self.out.append(self.combo(operand) % 8)
            elif opcode == 6:
                self.b = int(self.a / 2 ** self.combo(operand))
            elif opcode == 7:
                self.c = int(self.a / 2 ** self.combo(operand))

            self.i += 2

    @staticmethod
    def parse(input: str):
        import re

        digits = list(map(int, re.findall(r"\d+", input)))
        return Computer(*digits[:3], digits[3:])


def main(input: str):
    c = Computer.parse(input)
    c.execute()
    part1 = ",".join(str(n) for n in c.out)
    print("Part 1:", part1)

    # Step 1: reverse engineer the program manually:
    #
    # 2,4 -> b = a % 8
    # 1,1 -> b = b ^ 1
    # 7,5 -> c = a / 2^b
    # 1,5 -> b = b ^ 5
    # 4,1 -> b = b ^ c
    # 5,5 -> output b % 8
    # 0,3 -> a = a // 8
    # 3,0 -> iterate again if a is not 0
    #
    # the program runs operations and outputs 1 value every
    # iteration until a // 8 is 0, so that means the seed
    # value must be at least 8 to the power of len(program)
    # to be big enough to generate enough outputs

    min_a = 8 ** (len(c.program) - 1)

    # given the emphasis on 8 bits in the program instructions
    # and outputs, i tried looking at patterns when converting
    # the a register to 8 bits

    bits = [int(n) for n in oct(min_a)[2:]]

    # perhaps unsurprisingly, the number of input bits matched the
    # number of output bits, so i started manually testing bit
    # values and saw that early index input bit changes changed
    # late index output bits
    #
    # so lets try a depth first search manipulating input bits
    # until they patch required output bits

    idx = 0
    while idx < len(c.program):
        # try setting the input bit at index idx
        # until we find a match - if we do, then
        # move on to the next input bit. if we
        # dont, then backtrack
        bits[idx] += 1
        if bits[idx] > 7:
            bits[idx] = 0
            idx -= 1
            continue
        a = int("".join(str(n) for n in bits), 8)
        c.reset(a)
        c.execute()
        output = list(reversed(c.out))
        # uncomment to visualize whats happening
        # print("-" * 32)
        # print("  input:", bits)
        # print(" output:", output)
        # print("program:", c.reversed_program)
        # print("-" * 32)

        if output[idx] == c.reversed_program[idx]:
            idx += 1
        if c.out == c.program:
            print("Part 2:", a)
            break
        if idx == -1:
            print("no solution")


if __name__ == "__main__":
    import cProfile
    import pstats
    import os
    import time
    from colorama import Fore, Style
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser()

    # Add a flag (boolean argument)
    parser.add_argument(
        "--profile",
        action="store_true",  # Makes the flag act as a boolean
        help="Enable cProfile",
    )

    args = parser.parse_args()

    with open(f"{os.path.dirname(__file__)}/input.txt", "r") as f:
        input = f.read()

    if args.profile:
        with cProfile.Profile() as pr:
            start_time = time.time()
            main(input)
            end_time = time.time()

            # Save the profile data to a file
            with open(f"{os.path.dirname(__file__)}/solution.prof", "w") as f:
                stats = pstats.Stats(pr, stream=f)
                stats.strip_dirs()
                stats.sort_stats("cumtime")
                stats.dump_stats(f"{os.path.dirname(__file__)}/solution.prof")
    else:
        start_time = time.time()
        main(input)
        end_time = time.time()

    print(
        Fore.CYAN
        + f"execution time: {end_time - start_time:.3f} seconds"
        + Style.RESET_ALL
    )
