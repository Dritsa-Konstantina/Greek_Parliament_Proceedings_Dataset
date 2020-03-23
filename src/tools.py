# -*- coding: utf-8 -*-
import re

def greek_numerals_to_numbers(numeral):

    number = 0

    greek_numerals = {"α": 1,"a":1, "β": 2, "b":2, "γ": 3,"δ": 4, "ε": 5, "έ":5, "e":5,
                      "στ": 6, "ζ": 7, "z":7,"η": 8, "ή":8, "h":8, "θ": 9,
                      "ι": 10, "i":10, "κ": 20, "k":20, "λ": 30, "μ": 40,
                      "m":40, "ν": 50, "n":50, "ξ": 60,"ο": 70, "o":70, "ό":70,
                      "π": 80, "ϙ": 90, "ϟ":90, "ρ": 100,"p":100, "σ": 200, "τ": 300,
                      "t":300, "υ": 400, "φ": 500, "χ": 600,"ψ": 700, "ω": 800,
                      "ϡ": 900}

    numeral = re.sub("[΄'`’(); r'\d']","", numeral)

    numeral_letters = list(numeral.lower())

    new_letters=[]

    for i in range(len(numeral_letters)):
        if numeral_letters[i] == 'σ':
            if i!=len(numeral_letters)-1: #if σ is not the last letter
                if numeral_letters[i+1]== 'τ': #if σ is followed by τ
                    new_letters.append('στ') #join σ and τ
            else:
                new_letters.append(numeral_letters[i])
        elif numeral_letters[i] == 'τ':
            pass
        else:
            new_letters.append(numeral_letters[i])

    for letter in new_letters:
        number+= greek_numerals[letter]

    return str(number)

