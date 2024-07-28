import hashlib
import random
import csv
import os

common_password_words = [
    "password", "123456", "123456789", "qwerty", "abc123", "letmein", "monkey", "dragon",
    "111111", "baseball", "iloveyou", "sunshine", "princess", "football", "welcome",
    "shadow", "master", "hotdog", "muffin", "cookie", "pepper", "guitar", "jordan",
    "superman", "hannah", "tigger", "buster", "soccer", "qazwsx", "michael", "michelle",
    "magic", "mustang", "batman", "flower", "naruto", "pokemon", "peanut", "snoopy",
    "turtle", "chelsea", "summer", "blink182", "spider", "hockey", "ashley", "silver",
    "cookie", "shadow", "butter", "coffee", "chocolate", "family", "ginger", "hunter",
    "sunset", "rainbow", "skittles", "starwars", "awesome", "forever", "freedom", "ninja"
]

def hash_word(word: str) -> str:
    hash_object = hashlib.md5(word.encode())
    return hash_object.hexdigest()

def generate_hashed_word() -> str:
    word = random.choice(common_password_words)
    hashed_word = hash_word(word)
    return hashed_word

def write_hashed_words_to_csv(filename: str, hashed_words):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Hashed Word'])
        for hashed_word in hashed_words:
            writer.writerow([hashed_word])

def main():
    try:
        print("Generating hashed words...\n")
        hashed_words = [generate_hashed_word() for _ in range(100)]

        output_folder = 'generated_hash'
        output_file = os.path.join(output_folder, 'hashed_words.csv')

        write_hashed_words_to_csv(output_file, hashed_words)
        print(f"Hashed words have been written to: {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()