pos = 0
start = 0
text = "Beverly Hills 90210"


def one(predicate):
    global pos
    global start
    global text

    start = pos

    if predicate():
        pos = pos + 1
        print(text[start])


def one_or_more(predicate):
    global pos
    global start
    global text

    start = pos

    if predicate():
        pos = pos + 1

        while predicate(): 
            pos = pos + 1

        print(text[start:pos])


def digit():
    global pos
    global text

    if pos < len(text) and text[pos] >= '0' and text[pos] <= '9':
        return True
        
    return False


def alpha():
    return loweralpha() or upperalpha()


def loweralpha():
    global pos
    global text

    if pos < len(text) and text[pos] >= 'a' and text[pos] <= 'z':
        return True

    return False


def upperalpha():
    global pos
    global text

    if text[pos] >= 'A' and text[pos] <= 'Z':
        return True

    return False


def whitespace():
    global pos
    global text

    if text[pos] == ' ':
        pos = pos + 1


one_or_more(alpha)
one_or_more(whitespace)
one_or_more(alpha)
one_or_more(whitespace)
one_or_more(digit)
