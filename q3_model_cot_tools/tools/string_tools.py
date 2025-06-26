def count_vowels(s):
    return sum(1 for c in s.lower() if c in 'aeiou')

def count_consonants(s):
    return sum(1 for c in s.lower() if c.isalpha() and c not in 'aeiou')

def count_letters(s):
    return sum(1 for c in s if c.isalpha()) 