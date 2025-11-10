
import time
from operator import itemgetter


'''
Laddar vald textfil och returnerar en lista med rader
Tomma rader ignoreras
'''
def load_text_file(filename):
    lines = []
    with open(filename) as f:
        for raw_line in f:
            stripped = raw_line.strip()
            if stripped: #Hoppar över tomma rader
                lines.append(stripped)
    return lines


'''
Beräknar ordprecision för en rad
Ordprecision = ((korrekta_ord - extra_ord) / ord_i_text) * 100
'''
def calculate_word_precision(correct_line, user_line):
    correct_words = correct_line.split()
    user_words = user_line.split()
    total_words_in_text = len(correct_words)

    #Räknar hur många ord som är korrekta och på rätt plats
    nr_correct_words = 0
    for i in range(min(len(correct_words), len(user_words))):
        if user_words[i] == correct_words[i]:
            nr_correct_words += 1

    #Räknar ut extra ord
    extra_words = max(0, len(user_words) - len(correct_words))
    #Räknar ut felaktiga ord (inklusive de ord som inte skrevs ut av användaren)
    wrong_words = max(len(user_words), len(correct_words)) - nr_correct_words

    if total_words_in_text == 0:
        precision = 0.0
    else:
        precision = ((nr_correct_words - extra_words) / total_words_in_text) * 100
        if precision < 0:
            precision = 0.0 #Förhindrar negativa värden

    return round(precision, 2), wrong_words, nr_correct_words, extra_words


"""
Uppdaterar histogrammet med ord som användaren skrivit fel.
Räknar hur många gånger varje ord skrivits fel.
"""
def update_histogram(histogram, correct_line, user_line):
    correct_words = correct_line.split()
    user_words = user_line.split()

    index = 0
    while index < len(correct_words):
        correct_word = correct_words[index]
        user_word = ""
        if index < len(user_words):
            user_word = user_words[index]

        # Om ordet inte stämmer överens
        if user_word != correct_word:
            if correct_word in histogram:
                histogram[correct_word] += 1
            else:
                histogram[correct_word] = 1
        index += 1


"""
Skriver ut histogrammet sorterat efter antal (fallande)
och sedan alfabetiskt vid lika många
"""
def print_histogram(histogram):
    if len(histogram) == 0:
        print("No errors to display in the histogram.")
        return

    items = list(histogram.items())
    items.sort(key=itemgetter(0), reverse=True)  # sortera alfabetiskt (Z->A)
    items.sort(key=itemgetter(1), reverse=True)  # sedan på antal, fallande

    #Skriver ut histogrammet
    print("\nHistogram with misspelled words:\n")
    for word, count in items:
        print(f"{word:<20}: {'#' * count}")


'''
Kör själva skrivtestet
Beräknar precision per rad, uppdaterar histogrammet och visar resultat
'''
def run_typing_test(filename):
    lines = load_text_file(filename)
    histogram = {}
    total_typed_words = 0
    total_wrong_words = 0
    total_correct_words = 0
    total_extra_words = 0
    total_words_in_text = 0

    print("\n--- Typing test started ---\n")
    input("Press Enter to begin...")

    start_time = time.time()

    for correct_line in lines:
        print("\nText to type:")
        print(correct_line)
        user_line = input("> ")

        #Beräkna radprecision och uppdatera histogram
        precision, wrong_words, nr_correct_words, extra_words = (
            calculate_word_precision(correct_line, user_line)
        )

        temp_histogram = {}
        update_histogram(temp_histogram, correct_line, user_line)
        update_histogram(histogram, correct_line, user_line)

        #Samla statistik för slutresultatet
        total_correct_words += nr_correct_words
        total_extra_words += extra_words
        total_words_in_text += len(correct_line.split())
        total_wrong_words += wrong_words
        total_typed_words += len(user_line.split())

        #Skriver ut precision och histogram för enskild rad
        print(f"Precision this line: {precision}%")
        print_histogram(temp_histogram)

    elapsed_time = time.time() - start_time

    #Genomsnittlig ordprecision
    if total_words_in_text > 0:
        avg_precision = round(((total_correct_words-total_extra_words)/total_words_in_text)*100, 2)
        if avg_precision < 0:
            avg_precision = 0.0
    else:
        avg_precision = 0.0

    stats = {
        "avg_precision": avg_precision,
        "elapsed_time": elapsed_time,
        "total_typed_words": total_typed_words,
        "total_wrong_words": total_wrong_words,
        "histogram": histogram,
    }

    #Ropar på funktionerna som skriver ut resultatet och sparar det
    print_final_results(stats)
    print("\n")
    name = input("Enter your name: ").strip()
    save_score(name, avg_precision, filename, "scores.txt")

    return avg_precision


"""
Skriver ut slutresultat efter avslutat test
"""
def print_final_results(stats):
    avg_precision = stats["avg_precision"]
    elapsed_time = stats["elapsed_time"]
    total_typed_words = stats["total_typed_words"]
    total_wrong_words = stats["total_wrong_words"]
    histogram = stats["histogram"]

    print("\n--- Test complete! ---")
    print(f"Final average precision: {avg_precision}%")
    print_histogram(histogram)

    #Beräkna tid och ord per minut
    print(f"It took {int(elapsed_time // 60)} minutes and {elapsed_time:.2f} seconds")
    minutes = round_minutes(elapsed_time)
    gross_wpm = round(total_typed_words / minutes, 2)
    net_wpm = max(0, round(gross_wpm - (total_wrong_words / minutes), 2))
    if gross_wpm > 0:
        accuracy = round((net_wpm / gross_wpm) * 100, 2)
    else:
        accuracy = 0.0

    print(f"Gross WPM: {gross_wpm}")
    print(f"Net WPM: {net_wpm}")
    print(f"Accuracy: {accuracy}%")
    print(f"You type as fast as a {get_animal_category(net_wpm)}")


'''
Sköter avrundningen av tiden för uträkningen av WPM
'''
def round_minutes(seconds):
    ROUND_UP_THRESHOLD = 30 # Gräns för att avrunda uppåt
    minutes = int(seconds // 60)
    leftover = seconds % 60
    if minutes == 0:
        return 1  # allt under 1 minut blir 1
    elif leftover >= ROUND_UP_THRESHOLD:
        return minutes + 1
    else:
        return minutes


'''
Returnerar djurkategori baserat på användarens net WPM
'''
def get_animal_category(net_wpm):
    #Sätter max threshold
    ANIMAL_THRESHOLDS = [
        (5, "Sloth"),
        (15, "Snail"),
        (30, "Manatee"),
        (40, "Human"),
        (50, "Gazelle"),
        (60, "Ostrich"),
        (70, "Cheetah"),
        (80, "Swordfish"),
        (90, "Spur-winged goose"),
        (100, "White-throated needletail"),
        (120, "Golden eagle"),
        (float("inf"), "Peregrine falcon"),  # täcker allt över 120
    ]
    for threshold, name in ANIMAL_THRESHOLDS:
        if net_wpm <= threshold:
            return name # Returnerar djur beroende på net_wpm
    return "Unknown"


"""
Läser av svårighetsgrad baserat på filnamn
"""
def difficulty_from_filename(filename):
    filename = filename.lower()
    for key in ["easy", "medium", "hard"]:
        if key in filename:
            return key
    return "unknown"


'''
Sparar precision, namn och svårighetsgraden
Skriver det till en fil
'''
def save_score(name, avg_precision, filename, scores_file):
    difficulty = difficulty_from_filename(filename)
    with open(scores_file, "a") as f:
        f.write(f"{name}\t{avg_precision}\t{difficulty}\n")


'''
Returnerar en sorteringsnyckel för score
Sorterar först efter svårighetsgrad (easy → medium → hard),
sedan efter precision och namn
'''
def sort_key_for_scores(item):
        name, precision, diff = item
        difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
        diff_val = difficulty_order.get(diff, 99)
        return (diff_val, -precision, name)


'''
Läser av och sorterar scores baserat på svårighet, ordprecision och namn,
mha sort_key_for_scores, sen skriver den ut alla scores

'''
def read_and_print_scores(scores_file):
    scores = []
    try:
        with open(scores_file) as f:
            for line in f:
                line_stripped = line.strip()
                if line_stripped:
                    name, precision, diff = line_stripped.split("\t")
                    scores.append((name, float(precision), diff))
        if not scores:
            print("Scores file is empty")
            return
    except FileNotFoundError:
        print("No scores recorded yet.")
        return

    #Sortera med hjälp av helper-funktionen
    scores.sort(key=sort_key_for_scores)
    #Skriver ut alla rader
    for name, precision, diff in scores:
        print(f"{name:<8}{precision:<10}{diff}")
