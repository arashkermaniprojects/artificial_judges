import argparse
import json
from openai import OpenAI
import pandas as pd
from tqdm import tqdm 
import os 

system_prompt = '''You are a helpful assistant.'''
api_key = os.getenv('OPENAI_API_KEY')

if api_key is None:
    raise ValueError("No API key found in environment variables.")

system_prompt = '''You are a helpful assistant.'''
client = OpenAI(api_key=api_key)

def get_response(user_prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        temperature=0.7,
        messages=[
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{user_prompt}"}
        ]
    )
    return completion.choices[0].message.content

def generate_persona(categories):
    # Create a prompt to generate a persona's background based on the categories
    prompt = f"Generate a very brief description of a person who is an expert in the following topics:  {categories}."
    persona_background = get_response(prompt)
    return persona_background

def assess_learning_path(persona_background, learning_path,keyword):
    # Create a prompt to evaluate the learning path based on the persona's expertise
    prompt = f'''You are an expert with the following background: {persona_background}.
    You are evaluating a learning path for mastering the keyword '{keyword}'.

    Here is the learning path to assess: {learning_path}.

    Consider the following when evaluating:
    - Does the learning path follow a logical progression for understanding the keyword?
    - Are the topics relevant and useful for gaining a deep understanding of the keyword?
    - Are there any gaps or unnecessary steps in the path?
    - How well does this learning path help someone with no knowledge in the keyword?
    In your assessment return a Yes if the learning path is more than 50% suitable, a No if its less than 50% and an Unclear if its 50%
    '''
    assessment = get_response(prompt)
    # Extract the "Yes" or "No" part from the response
    if "Yes" in assessment:
        return "Yes"
    elif "No" in assessment:
        return "No"
    else:
        return "Unclear"

def main(args):
    # Load the Excel file
    df = pd.read_excel(args.input_path)
    
    if args.index is not None:
        # Ensure the specified index is valid
        if args.index < 0 or args.index >= len(df):
            raise ValueError(f"Invalid index: {args.index}. Index should be between 0 and {len(df)-1}.")
        # Process only the specified index
        indices = [args.index]
    else:
        # Process the specified number of entries
        num_entries = min(args.num_entries, len(df))
        indices = range(num_entries)
    
    results = []
    
    # Initialize the progress bar
    with tqdm(total=len(indices), desc="Processing Entries", unit="entry") as pbar:
        for i in indices:
            # Extract categories and learning path (recommendations) for each entry
            categories = df.iloc[i]['categories']
            learning_path = df.iloc[i][['recom_1', 'recom_2', 'recom_3', 'recom_4', 'recom_5']].tolist()
            keyword=df.iloc[i]['keyword']
            
            # Generate persona's background based on categories
            persona_background = generate_persona(categories)
            # Assess the learning path with the generated persona background
            assessment = assess_learning_path(persona_background, learning_path,keyword)
            
            # Store results for each entry
            result = {
                "entry": i + 1,
                "persona_background": persona_background,
                "assessment": assessment
            }
            results.append(result)
            
            # Update the progress bar
            pbar.update(1)
    
    # Save all outputs to a file
    with open(args.output_path, "w", encoding='utf-8') as out:
        json.dump(results, out, ensure_ascii=False, indent=2)
    
    print(f"\nOutputted the results to: {args.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate personas' backgrounds and assess learning paths.")
    parser.add_argument('--input_path', type=str, required=True, help='Path to the input Excel file.')
    parser.add_argument('--output_path', type=str, required=True, help='Path to the output file.')
    parser.add_argument('--num_entries', type=int, default=1, help='Number of entries to process from the Excel file.')
    parser.add_argument('--index', type=int, help='Specific index to process from the Excel file.')

    args = parser.parse_args()
    main(args)