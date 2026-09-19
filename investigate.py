from parse_data import load_items, get_unclaimed_items, save_result## Import the necessary modules
import json
import re
import ollama
from parse_data import load_items, get_unclaimed_items, save_result
## Import the function from the module parse_data   


## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.

def build_prompt(description, available_items):
    system_prompt = (
        "You are a campus lost-and-found assistant. "
        "Find possible matches between the user's lost item and the database.\n\n"
        "RULES:\n"
        "- Use ONLY the given JSON data.\n"
        "- Not all details need to match.\n"
        "- Return ONLY JSON with exactly this structure:\n"
        '{\n    "matches": ["ITEM_ID"],\n    "confidence": "LOW"\n}\n'
        "- matches: list of item IDs (empty list if none)\n"
        "- confidence: exactly one of LOW, MEDIUM, HIGH\n"
        "- No explanation, no markdown."
    )
    user_prompt = (
        f"User's lost item description: {description}\n\n"
        f"Available items:\n{json.dumps(available_items, indent=2)}"
    )
    return system_prompt, user_prompt
    

## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        think=False,
    )
    return response["message"]["content"]


## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    text = response_text.strip()

    text = re.sub(r" thinking.*?", "", text, flags=re.DOTALL)
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)
    


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if not isinstance(result, dict):
        return False
    if "matches" not in result or "confidence" not in result:
        return False
    if not isinstance(result["matches"], list):
        return False
    if not isinstance(result["confidence"], str):
        return False
    if result["confidence"] not in ("LOW", "MEDIUM", "HIGH"):
        return False

    valid_ids = {item["id"] for item in available_items}
    for match_id in result["matches"]:
        if match_id not in valid_ids:
            return False
    return True


def display_matches(result, available_items):
    print("\nMATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence']}\n")

    if not result["matches"]:
        print("No matches were found.")
        print("Possible matches: []")
        return

    items_by_id = {item["id"]: item for item in available_items}
    print("Possible matches:\n")
    for match_id in result["matches"]:
        item = items_by_id.get(match_id)
        if item:
            print(f"ID: {item['id']}")
            print(f"Item: {item['item']}")
            print(f"Color: {item['color']}")
            print(f"Location: {item['location']}")
            print(f"Date found: {item['date']}")
            print()

def main():
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)

    description = input("\nDescribe the item you lost: ")

    items = load_items("found_items.json")
    available_items = get_unclaimed_items(items)

    system_prompt, user_prompt = build_prompt(description, available_items)

    print("\nSearching for possible matches...\n")
    response_text = ask_qwen(system_prompt, user_prompt)

    try:
        result = parse_response(response_text)
    except json.JSONDecodeError:
        print("Error: model did not return valid JSON.")
        print("Raw response:", response_text)
        return

    if not validate_result(result, available_items):
        print("Error: invalid result structure.")
        print("Parsed result:", result)
        return

    display_matches(result, available_items)

    save_result(result, "output/match_result.json")
    print("Result saved to output/match_result.json")


if __name__ == "__main__":
    main()

## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    pass
    

## Control center for the entire program.
def main():
    pass


if __name__ == "__main__":
    main()