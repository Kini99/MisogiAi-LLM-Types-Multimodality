# Tool-Enhanced Reasoning Script

This project demonstrates a simple tool-augmented reasoning system using an LLM (Gemmini 2.0 Flash) and Python functions for math and string operations.

## Features
- Chain-of-thought (CoT) reasoning with LLM
- Automatic tool selection and calling (math, string tools)
- Combines LLM reasoning and tool results for final answers
- No agents or frameworks required

## Installation
1. Clone this repository.
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Gemmini API key in a `.env` file (see `.env.example`).

## Usage
Run the script with:
```bash
python main.py
```
You will be prompted to enter a natural language query.

## Example Queries & Outputs
1. **Query:** What's the square root of the average of 18 and 50?
   - Reasoning: First, we need to find the average of 18 and 50.  The average is calculated by summing the numbers and dividing by the count of numbers.  Then, we need to find the square root of that average.
   Step 1: Calculate the average of 18 and 50.
   (18 + 50) / 2 = 68 / 2 = 34
   Step 2: Calculate the square root of the average (34).
   - Tool used: calculator sqrt(34)
   - Final answer: 5.8309518948453

2. **Query:** How many vowels are in the word 'Multimodality'?
   - Reasoning: To find the number of vowels in the word 'Multimodality', we need to identify each vowel and count them. The vowels in the English alphabet are A, E, I, O, U. Let's go through the word letter by letter:
   M - not a vowel
   U - vowel (count = 1)
   L - not a vowel
   T - not a vowel
   I - vowel (count = 2)
   M - not a vowel
   O - vowel (count = 3)
   D - not a vowel
   A - vowel (count = 4)
   L - not a vowel
   I - vowel (count = 5)
   T - not a vowel
   Y - not a vowel
Therefore, there are 5 vowels in the word 'Multimodality'.
   - Tool used: None needed.
   - Final answer: 5

3. **Query:** Is the number of letters in 'machine' greater than the number of vowels in 'reasoning'?
   - Reasoning: First, we need to count the number of letters in the word 'machine'.  Then, we need to count the number of vowels (a, e, i, o, u) in the word 'reasoning'. Finally, we compare the two counts to determine which is greater.
   Tool: string counter 'machine'
   Tool: string counter 'reasoning' (then count the vowels a, e, i, o, u manually from the result)
   Let's use the tools:
   Tool: string counter 'machine'
   Output: 7
   Tool: string counter 'reasoning'
   Output: 9
   Manual vowel count in 'reasoning':  'e', 'o', 'i', 'i'  (4 vowels)
   Now we compare:
   Number of letters in 'machine': 7
   Number of vowels in 'reasoning': 4
   7 > 4
   Final answer: Yes
   - Tool used: string counter
   - Final answer: Yes

4. **Query:** What is 15% of the sum of 40 and 60?
   - Reasoning: First, we need to find the sum of 40 and 60. Then, we need to calculate 15% of that sum.
   Step 1: Sum of 40 and 60
   40 + 60 = 100
   Step 2: Calculate 15% of 100
   15% of 100 can be calculated as (15/100) * 100 = 15
   - Tool used: None needed.
   - Final answer: 15

5. **Query:** Does the word 'Gemmini' contain more consonants than vowels?
   - Reasoning: To determine if 'Gemmini' contains more consonants than vowels, we first need to identify the vowels and consonants in the word. The vowels are 'e', 'i', 'i'. The consonants are 'G', 'm', 'm', 'n'.  There are 3 vowels and 4 consonants.  Therefore, the number of consonants is greater than the number of vowels.
   - Tool used: None needed.
   - Final answer: Yes

## How Prompt Decides Tool Usage
The prompt instructs the LLM to reason step-by-step and explicitly state if a tool (math or string) is needed. The script parses this reasoning to decide which function to call.

## API Key
Copy `.env.example` to `.env` and add your Gemmini API key:
```
GEMMINI_API_KEY=your_key_here
``` 