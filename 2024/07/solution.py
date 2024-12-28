def parse(input):
    equations = []
    for line in input.split("\n"):
        result_str, nums_str = line.split(": ")
        result = int(result_str)
        nums = tuple(map(int, nums_str.split()))
        equations.append((result, nums))
    return equations


def solve(result, numbers, allow_concat, value, index):
    # found the solution
    if value == result and index == len(numbers):
        return True

    # overshot and all operations are increasing
    # so end early
    if value > result:
        return False

    # out of numbers
    if index >= len(numbers):
        return False

    # allow concat
    if allow_concat:
        if solve(
            result,
            numbers,
            allow_concat,
            int(str(value) + str(numbers[index])),
            index + 1,
        ):
            return True

    # addition
    if solve(result, numbers, allow_concat, value + numbers[index], index + 1):
        return True

    # multiply
    if solve(result, numbers, allow_concat, value * numbers[index], index + 1):
        return True

    # no options remaining
    return False


def main(input):
    equations = parse(input)
    remaining = []
    total = 0
    for result, numbers in equations:
        if solve(result, numbers, False, numbers[0], 1):
            total += result
        else:
            remaining.append((result, numbers))
    print("Part 1:", total)

    for result, numbers in remaining:
        if solve(result, numbers, True, numbers[0], 1):
            total += result
    print("Part 2:", total)


if __name__ == "__main__":
    import cProfile
    import pstats
    import os
    import time
    from colorama import Fore, Style

    with open(f"{os.path.dirname(__file__)}/input.txt", "r") as f:
        input = f.read()

    with cProfile.Profile() as pr:
        start_time = time.time()
        main(input)
        end_time = time.time()
        print(
            Fore.CYAN
            + f"execution time: {end_time - start_time:.3f} seconds"
            + Style.RESET_ALL
        )

        # Save the profile data to a file
        with open(f"{os.path.dirname(__file__)}/solution.prof", "w") as f:
            stats = pstats.Stats(pr, stream=f)
            stats.strip_dirs()
            stats.sort_stats("cumtime")
            stats.dump_stats(f"{os.path.dirname(__file__)}/solution.prof")
