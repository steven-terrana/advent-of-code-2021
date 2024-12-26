def part1(g1, g2):
    g1 = sorted(g1)
    g2 = sorted(g2)
    sum = 0
    for n in range(len(g1)):
        sum = sum + abs(g1[n] - g2[n])
    return sum


def part2(g1: list[int], g2: list[int]) -> int:
    sum = 0
    for n in set(g1):
        sum = sum + n * g1.count(n) * g2.count(n)
    return sum


def main(input: str):
    (g1, g2) = zip(*[[int(n) for n in line.split()] for line in input.split("\n")])
    print(part1(g1, g2))
    print(part2(g1, g2))


if __name__ == "__main__":
    import cProfile
    import pstats
    import os
    import time
    from colorama import Fore

    with open(f"{os.path.dirname(__file__)}/input.txt", "r") as f:
        input = f.read()

    with cProfile.Profile() as pr:
        start_time = time.time()
        main(input)
        end_time = time.time()
        print(Fore.CYAN + f"execution time: {end_time - start_time:.3f} seconds")

        # Save the profile data to a file
        with open(f"{os.path.dirname(__file__)}/solution.prof", "w") as f:
            stats = pstats.Stats(pr, stream=f)
            stats.strip_dirs()
            stats.sort_stats("cumtime")
            stats.dump_stats(f"{os.path.dirname(__file__)}/solution.prof")
