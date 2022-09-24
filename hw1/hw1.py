def get_fizz_buzz(number):
    result = ''
    if number % 3 == 0:
        result += 'Fizz'
    if number % 5 == 0:
        result += 'Buzz'
    return result


def main():
    print(*[fizz_buzz if (fizz_buzz := get_fizz_buzz(number)) else number for number in range(1, 101)])


if __name__ == '__main__':
    main()
