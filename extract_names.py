from pydantic import BaseModel
from pathlib import Path 
from typing import List, Dict 
from langgraph.prebuilt import create_react_agent
from prompts import transcript_extract_all_names
from dotenv import load_dotenv
from google import genai 
import asyncio 
import json 

load_dotenv()

class NameList(BaseModel):
    name_list: List[str]

def load_the_transcript(file_path: str) -> str:
    with open(file_path, mode='r') as file:
        return file.read()
    
async def generate_ai_response(file_path: str):
    client = genai.Client()
    model_name = 'gemini-2.5-pro'
    transcript = load_the_transcript(file_path)
    response = await client.aio.models.generate_content(
        model=model_name,
        contents=transcript_extract_all_names(transcript),
        config={
            "response_mime_type": "application/json",
            "response_schema": NameList,
        },
    )
    if response and response.parsed:
        my_result = dict(response.parsed)
        return (my_result, file_path)
    return ({},"")

def get_normalized_path(file: str) -> str:
    return "".join(file.split('/')[-1].split('.')[0].split())
async def main() -> str:
    refactored_file_names = {}
    for file in Path("transcripts").iterdir():
        refactored_file_name = get_normalized_path(file.name)
        refactored_file_names[refactored_file_name] = str(file)
        print(refactored_file_name)
    
    for file in Path("extracted_transcripts").iterdir():
        file = get_normalized_path(file.name)
        if file in refactored_file_names:
            refactored_file_names.pop(file)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(generate_ai_response(value)) for _, value in refactored_file_names.items()]
    for task in tasks:
        result = task.result()
        if result[1] != "":
            refactored_file_name = get_normalized_path(result[1])
            with open(f"extracted_transcripts/extracted_names_{refactored_file_name}.json", mode= 'w', encoding='utf-8') as file:
                json.dump(result[0]["name_list"], file)

if __name__ == "__main__":
    asyncio.run(main())