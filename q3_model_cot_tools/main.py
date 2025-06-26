import os
from dotenv import load_dotenv
from tools.math_tools import calculate_expression
from tools.string_tools import count_vowels, count_letters, count_consonants
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GEMMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_llm_reasoning(query):
    prompt = f"""
You are a helpful assistant. Given the following query, reason step by step (chain-of-thought). If you need to use a tool, say exactly which tool and what input to use. Available tools: calculator, string counter. Example format:
Reasoning: ...
Tool: <tool_name> <input>
Final answer: ...
Query: {query}
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def parse_and_execute(reasoning):
    lines = reasoning.split('\n')
    tool_used = None
    tool_result = None
    for line in lines:
        if line.startswith('Tool:'):
            tool_used = line[len('Tool:'):].strip()
            if tool_used.startswith('calculator'):
                expr = tool_used[len('calculator'):].strip()
                tool_result = calculate_expression(expr)
            elif tool_used.startswith('string counter'):
                arg = tool_used[len('string counter'):].strip().strip("'\"")
                if 'vowel' in lines[0].lower():
                    tool_result = count_vowels(arg)
                elif 'consonant' in lines[0].lower():
                    tool_result = count_consonants(arg)
                else:
                    tool_result = count_letters(arg)
    final_answer = None
    for line in lines:
        if line.startswith('Final answer:'):
            final_answer = line[len('Final answer:'):].strip()
    return lines[0], tool_used, tool_result, final_answer

def main():
    print("Welcome to the Tool-Enhanced Reasoning Script!")
    query = input("Enter your query: ")
    reasoning = get_llm_reasoning(query)
    print("\nLLM Reasoning:")
    print(reasoning)
    step, tool_used, tool_result, final_answer = parse_and_execute(reasoning)
    print(f"\nReasoning step: {step}")
    print(f"Tool used: {tool_used if tool_used else 'None'}")
    if tool_result is not None:
        print(f"Tool result: {tool_result}")
    print(f"Final answer: {final_answer}")

if __name__ == "__main__":
    main() 