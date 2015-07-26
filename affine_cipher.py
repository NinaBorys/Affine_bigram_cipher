#! /usr/bin/python3

import itertools
import sys
from math import log2


# alphabet_str = "абвгдежзийклмнопрстуфхцчшщыьэюя"
alphabet_str = "абвгдежзийклмнопрстуфхцчшщьыэюя"


def read_file():
    # for V* files use coding:  'cp866'
    with open('03.txt', 'r', encoding='cp1251') as f:
        z = f.read().replace('\n', '')
    return z


def char_frequency(check_string):
    """Frequency analysis, returns frequency of letters, returns ('symbol', occurrences) """
    res_dict = dict()
    for s in check_string:
        if s in res_dict: res_dict[s] += 1
        else: res_dict[s] = 1
    return res_dict


def bigrams_frequency_uncrossed(check_string):    
    """Frequency analysis, returns frequency of uncrossed bigrams, returns ('bigram', occurrences) """
    res_dict = dict()
    for i in range(0, len(check_string), 2):
        bigram = check_string[i:i+2]
        if bigram in res_dict: res_dict[bigram] += 1
        else: res_dict[bigram] = 1
    return [x[0] for x in sorted(res_dict.items(), key=lambda x: (-x[1], x[0]))]


def entropy(freq_dict, text):
    """Returns entropy value for text"""
    return abs(round(sum((i / len(text) * log2(i / len(text)) for i in freq_dict.values())), 3))


def gcd(a,b,x,y):
    """ ax + by = 1; returns (gcd, x, y) """
    if b == 0:
        return a, 1, 0
    x1 = 0
    y1 = 0
    r = gcd(b, a % b, x1, y1)
    d1 = r[0]
    x1 = r[1]
    y1 = r[2]
    x = y1
    y = x1 - (a // b) * y1
    return d1, x, y


def reversed_element(a,N):
    """ a * a^-1 = 1 mod N; returns a^-1"""
    d = gcd(a, N, 0, 0)
    if d[0] != 1: return 1
    else:
        return ((d[1] % N + N) % N)


def comprasion(a,b,m):
    """a * x = b (mod m); returns x"""
    d = gcd(a, m, 0, 0)[0]
    if (b / d - b // d != 0):
        return "comprasion is not solvable"
    rev_a = reversed_element(a // d, m // d)
    res = []
    res.append((rev_a * b // d) % (m // d))
    res[0] = ((res[0] + m // d) % (m // d))

    for i in range(1, d):
        res.insert(i, res[i-1] - (m // d))
        if res[i] < 0:
            res[i] = (res[i] + m) % m
    return res


def bigram_number(x1,x2):
    """For bigram (x1,x2) returns X = x1*m + x2 """
    return (alphabet_str.index(x1) *  len(alphabet_str) + alphabet_str.index(x2))


def bigram_from_number(k):
    """Recovers bigram (x1,x2) from its number; returns "x1x2" """
    x2 = k % len(alphabet_str)
    x1 = (k - x2) // len(alphabet_str)
    return alphabet_str[x1] + alphabet_str[x2]


def find_key_pair(x1, x2, y1, y2):
    """(y1 - y2) = a * (x1 - x2) mod m^2 ; returns key pairs (a,b) """
    X = bigram_number(x1[0], x1[1]) - bigram_number(x2[0], x2[1])
    Y = bigram_number(y1[0], y1[1]) - bigram_number(y2[0], y2[1])

    a = comprasion(X, Y, len(alphabet_str)*len(alphabet_str))
    if isinstance(a, str): return False
    b= []
    for x in a:
        b.append((bigram_number(y1[0],y1[1]) - x * bigram_number(x1[0],x1[1])) % (len(alphabet_str) ** 2))
    return zip(a,b)


def test_with_forbidden_bigrams(text):
    """Test for russian language recognizer with forbidden bigrams"""
    forbidden = ["фб", "фв", "фг", "ыа", "хы", "бп","хг"]
    for i in range(0,len(text), 2):
        bigram=text[i: i + 2]
        for j in range(len(forbidden)):
            if bigram == forbidden[j]: return False
    return True


def entrophy_test(text):
    """Test for russian language recognizer with entropy value"""
    if entropy(char_frequency(text),text) > 5: return False
    return True


def language_recognizer(text):
    """Checks if resulting text is informative"""
    return (test_with_forbidden_bigrams(text) and entrophy_test(text))


def affine_encode(PT,a,b):
    """Returns CT string"""
    CT = str()
    for i in range(0,len(PT),2):
        bigr = bigram_number(PT[i], PT[i+1])
        Y = (bigr * a + b ) % (len(alphabet_str) ** 2)
        CT += bigram_from_number(Y)
    return CT


def affine_decode(CT,a,b):
    """Returns PT string"""
    PT = str()
    for i in range(0,len(CT), 2):
        bigr = bigram_number(CT[i], CT[i+1])
        X = (reversed_element(a, len(alphabet_str) ** 2) * (bigr - b)) % (len(alphabet_str) ** 2)
        while X < 0:
            X += (len(alphabet_str) ** 2)
        PT += bigram_from_number(X)
    return PT


def affine_decipher(CT):
    """Desiphers text without knowing keys"""
    # most frequent bigrams of language
    russian_freq = ['ст','но','то','на','ен']
    # 5 most frequent bigrams of CT
    CT_most_freq = bigrams_frequency_uncrossed(CT)[:5]
    # matching bigrams and finding keys
    e = 0
    list2 = [CT_most_freq[e], CT_most_freq[e + 1]]
    perm = [tuple(zip(x, list2)) for x in itertools.permutations(russian_freq, len(list2))]
    for permutation in perm:
        a_b = find_key_pair(permutation[0][0], permutation[1][0], permutation[0][1], permutation[1][1])
        # trying keys
        if not a_b: continue
        for a, b in a_b:
            print("Trying with key: ", a, b)
            k = affine_decode(CT, a, b )            
            # test if deciphered text is informative
            if not language_recognizer(k): continue
            print(k[:45])
            ifyesorno = int(input("Is this it? (1/0): "))
            e += 1
            if ifyesorno:
                print("Your key is: ", a,b, "\n Great job!")
                sys.exit()

      
def main():
    """_____  Affine bigram cipher _____"""
    CT = read_file()
    # print(CT) 
    # print(affine_decode(CT,199,700))
    affine_decipher(CT)


if __name__ == '__main__':
    main()