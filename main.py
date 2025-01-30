"""
Project: YouTube Spam Filter
NAME: Gabe Schneider
CLASS: CS1430
PURPOSE: Detect Spam Comments On YouTube
INPUT: Potential Spam Comments
OUTPUT: Spam Score
"""
import re
import string

#############
# CONSTANTS #
#############

_BARBWIRE = "+-" * 22
_VIEW_PLAN = 1
_TEST_COMMENT = 2
_SCAN_COMMENT = 3
_SPAM_HISTORY = 4

_BETA_STRING = 6
_MAX_REPEAT = 5
_BETA_REPEAT = 1

_BETA_TOTAL = 3
_MAX_TOTAL = 0

_SHORT_COMMENT = 20
_LARGE_COMMENT = 100

_SHORT_PARAGRAPH = 100
_LARGE_PARAGRAPH = 300

_SHORT_DENSITY = 0.25 # 25%
_MEDIUM_DENSITY = 0.20 # 20%
_LARGE_DENSITY = 0.15 # 15%

_MAX_AVG_SENTENCE = 10
_MAX_PUNC_TYPE = 5

_MAX_SHORT = 1
_MAX_MEDIUM = 3
_MAX_LARGE = 5

_SPAM_COUNT = 1
_URL_COUNT = 1

def process_string(user_string):
    # Remove Spaces
    stripped_string = user_string.strip()
    return stripped_string


def check_spam(user_string):
    # Keep track of spam score
    spam_score = 0

    # Preprocess string
    processed_string = process_string(user_string)

    # Indicator 1 (Letter Repeats)
    result = letter_repeats(processed_string)
    spam_score += result

    # Indicator 2 (All Caps)
    result = all_caps(processed_string)
    spam_score += result

    # Indicator 3 (Punctuation)
    result = punctuation_check(processed_string)
    spam_score += result

    # Indicator 4 (Keywords)
    result = check_keywords(processed_string)
    spam_score += result

    # Indicator 5 (URL and Emoji)
    result = links_emojis(processed_string)
    spam_score += result

    return spam_score


def check_keywords(user_string):
    ###
    total_score = 0
    spam_count = 0
    ###

    # List of spam keywords, will be read from file at some point
    spam_keywords = [
        "free", "winner", "guaranteed", "exclusive", "limited time", "act now", "call now",
        "congratulations", "click here", "don’t miss", "earn", "easy money", "urgent",
        "cash bonus", "investment", "instant access", "special offer", "risk-free", "discount",
        "buy now", "cheap", "save big", "lowest price", "millionaire", "offer ends",
        "amazing deal", "credit card", "pre-approved", "apply now", "100%", "no obligation",
        "satisfaction guaranteed", "trial", "free trial", "unlimited", "bargain", "bonus",
        "double your", "earn cash", "debt-free", "get paid", "no cost", "verified", "instant",
        "work from home", "weight loss", "make money", "subscription", "income", "profits"
    ]

    processed_string = user_string.lower()

    # Check for spam keywords
    for words in spam_keywords:
        if words in processed_string:
            spam_count += 1

    if spam_count >= _SPAM_COUNT:
        total_score += 1

    return total_score


def links_emojis(user_string):
    ###
    total_score = 0
    num_urls = 0
    num_emojis = 0
    ###

    # Detect URL pattern
    result = re.findall('(http[s]?://[^\s]+|www\.[^\s]+|[^\s]+\.(com|net|org|info|biz|io|co|us|edu))', user_string)

    for _ in result:
        num_urls += 1

    if num_urls >= _URL_COUNT:
        total_score += 1

    # Detect emojis by their Unicode character
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F" 
        "\U0001F300-\U0001F5FF" 
        "\U0001F680-\U0001F6FF" 
        "\U0001F1E0-\U0001F1FF" 
        "\U00002702-\U000027B0"  
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )

    emoji_matches = emoji_pattern.findall(user_string)

    for _ in emoji_matches:
        num_emojis += 1

    if num_emojis >= 1:
        total_score += 1

    return total_score


def letter_repeats(user_string):
    ###
    beta_repeat = 0 # 3 allowed
    max_repeat = 0  # Track the maximum repeat count
    total_score = 0 # Total spam score from repeats
    ###

    # Check for letter repeats
    my_list = []
    my_count = 1

    for letter in range(len(user_string)-1):
        if user_string[letter] == user_string[letter+1]:
            my_count += 1
        else:
            my_list.append(my_count)
            my_count = 1
    my_list.append(my_count)

    # Iterate through list and add every repeat
    for nums in my_list:
        if nums > _BETA_REPEAT:
            beta_repeat += 1
        if nums >= _MAX_REPEAT:
            max_repeat += 1

    # Classify as spam or not
    if max_repeat > _MAX_TOTAL or beta_repeat > _BETA_TOTAL:
        total_score += 1

    return total_score


def punctuation_check(user_string):
    ###
    total_score = 0
    punctuation_count = 0
    my_sentences = 0
    ###

    # Detects spammy punctuation while allowing normal usage
    my_length = len(user_string)
    punctuation_clusters = {}

    # Count punctuation and clusters
    for char in user_string:
        if char in string.punctuation:
            punctuation_count += 1
            if char in ".!?":
                my_sentences += 1
            if char not in punctuation_clusters:
                punctuation_clusters[char] = 1
            else:
                punctuation_clusters[char] += 1

    # Fixed a bug where it would auto-detect one letter as spam
    if my_sentences == 0:
        sentence_length_avg = my_length
    else:
        sentence_length_avg = my_length / my_sentences

    # Calculate punctuation density
    punctuation_density = punctuation_count / my_length if my_length > 0 else 0

    # Spam thresholds (may change to custom config.ini file later)
    if my_length < _SHORT_PARAGRAPH:
        if punctuation_density > _SHORT_DENSITY and sentence_length_avg < _MAX_AVG_SENTENCE:
            total_score += 1
    # Handle Small paragraph
    elif _SHORT_PARAGRAPH <= my_length <= _LARGE_PARAGRAPH:
        if punctuation_density > _MEDIUM_DENSITY or max(punctuation_clusters.values(), default=0) > _MAX_PUNC_TYPE:
            total_score += 1
    # Handle large paragraph
    elif my_length > _LARGE_PARAGRAPH:
        if punctuation_density > _LARGE_DENSITY:
            total_score += 1

    return total_score



def all_caps(user_string):
    ###
    is_spam = 0
    all_caps_count = 0
    ###

    # Check if all caps
    my_words = user_string.split()
    string_length = len(user_string)

    # Check for uppercase word
    for word in my_words:
        if word.isupper():
            all_caps_count += 1

    # Short Comments (1-20 Characters)
    if string_length <= _SHORT_COMMENT and all_caps_count > _MAX_SHORT:
        is_spam += 1
    # Medium Comments (20-100 Characters)
    elif _SHORT_COMMENT < string_length <= _LARGE_COMMENT and all_caps_count > _MAX_MEDIUM:
        is_spam += 1
    # Long Comments (>100 Characters)
    elif string_length > _LARGE_COMMENT and all_caps_count > _MAX_LARGE:
        is_spam += 1

    return is_spam


def spam_history(spam_comments):
    user_file = open("spam_history.txt", "a", encoding="utf-8")

    for comment in spam_comments:
        user_file.writelines(comment + "\n")

    user_file.close()

def view_history():
    # View spam history
    user_file = open("spam_history.txt", "r", encoding="utf-8")
    result = user_file.read()
    user_file.close()

    return result

def scan_list(user_input):
    ###
    total_spam = 0
    result = []
    spam_list = []
    ###

    user_file = open(user_input, "r", encoding="utf-8")
    user_lines = user_file.readlines()

    user_file.close()

    for line in user_lines:
        if line.strip().startswith("@") or "ago" in line or "Reply" in line:
            continue
        if line.strip():
            result.append(line.strip())

    for comment in result:
        checked_comment = check_spam(comment)
        if checked_comment >= 1:
            total_spam += 1
            spam_list.append(comment)

    spam_history(spam_list)

    return total_spam


def view_plan(user_plan):
    # State the user plan
    result = ""

    if user_plan == "Free":
        result = "You are on the free plan, enjoy!"
    elif user_plan == "Premium":
        result = "You are on the Premium plan, enjoy unlimited features and AI!"

    return result


def user_selection(user_input):
    if user_input == _VIEW_PLAN:
        user_plan = "Free"
        print(view_plan(user_plan))
    elif user_input == _TEST_COMMENT:
        # Enter in and check the string
        user_string = input("Please enter your comment: ")
        result = check_spam(user_string)
        print("This comment has", result, "spam indicators!")

    elif user_input == _SCAN_COMMENT:
        print("Please enter PATH to comments: ")
        user_input = input()
        result = (scan_list(user_input))
        print(f"There are {result} spam comments in {user_input}")

    elif user_input == _SPAM_HISTORY:
        print("Here are the detected spam comments:")
        print(view_history())


def user_menu():
    print(_BARBWIRE)
    print("Please select from the following menu:")
    print(_BARBWIRE)
    print("1: View plan")
    print("2: Input test comment")
    print("3: Scan comment list")
    print("4: View spam history")


def main():
    print("Welcome to YouBuster spam detection tool")
    user_menu()
    user_input = int(input("Please select option number -> "))
    user_selection(user_input)


if __name__ == '__main__':
    main()
