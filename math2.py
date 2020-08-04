code = "1 + 2 * 3 + 4"
pos = 0


def expression():
    global code
    global pos

    result = term()

    while pos < len(code):

        # add
        if code[pos] == "+":
            pos = pos + 1
            result = result + term()

        # subtract
        elif code[pos] == "-":
            pos = pos + 1
            result = result - term()

        # passthrough
        else:
            break

    return result


def term():
    global code
    global pos

    result = factor()

    while pos < len(code):

        # multiply
        if code[pos] == "*":
            pos = pos + 1
            return result * factor()

        # divide
        elif code[pos] == "/":
            pos = pos + 1
            return result / factor()

        # passthrough
        else:
            break

    return result


def factor():
    global code
    global pos
    trivia()

    # check if integer is possible
    if pos < len(code) and code[pos] >= "0" and code[pos] <= "9":

        # integer
        start = pos
        while pos < len(code) and code[pos] >= "0" and code[pos] <= "9":
            pos = pos + 1
        result = int(code[start:pos])

        trivia()
        return result

    else:
        raise Exception("SyntaxError: number expected.")


def trivia():
    global code
    global pos

    # skip whitespace
    while pos < len(code) and code[pos] == " ":
        pos = pos + 1


print(expression())
