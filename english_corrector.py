from IPython.display import display, HTML
import requests

stop = "no"
original_sentence = ""

# Initial user input
category = input("Select Category. Write 'stop' to quit: ")
index = int(input("Select the index of the first sentence to get: "))
print()

while stop == "no":

    if category == "stop":
        stop = "yes"
        break

    payload = {
        "category": category,
        "index": index
    }

    # Send a POST request to the endpoint
    url = f"{domain}/get-new-sentence"
    response = requests.post(url, json=payload)

    # Check if the request was successful and display the result
    if response.status_code == 200:
        sentence = response.json()['ita']
        original_sentence = response.json()['eng']
        
        # Display sentence using HTML formatting
        display(HTML(f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; background-color: #f9f9f9;">
                <strong>Sentence {index}:</strong><br>
                <span>{sentence}</span>
            </div>
        """))
    else:
        display(HTML(f"<div style='color: red;'>Request failed with status code: {response.status_code}<br>Error: {response.text}</div>"))

    translated = False
    retries_counter = 0
    while translated is False:
        if retries_counter == 0:
            translated_sentence = input("Your Translation: ")
        else:
            translated_sentence = input("Try another translation: ")
    
        if translated_sentence == "stop":
            stop = "yes"
            break
    
        url = f"{domain}/check-sentences"
    
        payload = {
            "sentence1": original_sentence,
            "sentence2": translated_sentence
        }
    
        # Send a POST request to the endpoint
        response = requests.post(url, json=payload)
    
        # Check if the request was successful and display feedback
        if response.status_code == 200:
            similarity_score = float(response.json()['similarity_score'])
            
            if similarity_score >= 95.00:  # Adjust leniency threshold here
                index += 1
                translated = True
                
                feedback_msg = f"Good job! You got it with a similarity score of {int(similarity_score)}%" if retries_counter == 0 else f"Good job! It took you {retries_counter} try/tries with {int(similarity_score)}% accuracy."
                
                display(HTML(f"""
                    <div style="border: 2px solid green; padding: 10px; margin: 10px 0; background-color: #e7f7e7;">
                        <p>{feedback_msg}</p>
                        <p>Let's go to the next one!</p>
                    </div>
                    <hr>
                """))
            else:
                # Retrieve and display hints as a dotted list
                hints = response.json()['hints']
                
                # Function to process each hint
                def split_and_process_hint(hint):
                    # Split the hint on dashes and strip whitespace
                    parts = [part.strip().capitalize() for part in hint.split('-') if part.strip()]
                    return parts
                
                # Remove leading dash and space if they exist and create list items
                if isinstance(hints, list):
                    hints_list = ''.join(
                        f"<li>{sub_hint}</li>"
                        for hint in hints
                        for sub_hint in split_and_process_hint(hint)
                    )
                else:
                    hints_list = ''.join(
                        f"<li>{sub_hint}</li>"
                        for sub_hint in split_and_process_hint(hints)
                    )
            
                display(HTML(f"""
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; background-color: #ffebcc;">
                        <p style="font-size: 1.25em; font-weight: bold;">Similarity: {int(similarity_score)}%</p>
                        <p style="font-size: 1.1em; font-weight: bold;">Hints:</p>
                        <ul style="list-style-type: disc; padding-left: 20px;">
                            {hints_list}
                        </ul>
                    </div>
                """))
                retries_counter += 1
        else:
            display(HTML(f"<div style='color: red;'>Request failed with status code: {response.status_code}<br>Error: {response.text}</div>"))