import requests
import json
import os
import base64
from PIL import Image
from tesserocr import PyTessBaseAPI
from datetime import datetime
import os

# Placeholder API keys (replace with actual keys)
GROK_API_KEY = "GROK_API_KEY"
OPENAI_API_KEY = "your_openai_api_key"
ANTHROPIC_API_KEY = "your_anthropic_api_key"

# Output directory for storing responses
OUTPUT_DIR = "/Users/sonmanik/Personal/projects/PaperX"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GRADING_PROMPT = """
You are an expert grader evaluating a student's question-and-answer submission. The input contains questions and their corresponding answers. Your task is to:

1. Grade each question based on correctness and completeness (0-100 score).
2. Provide a confidence score (0-100) for your grading accuracy.
3. Offer specific suggestions for improvement to achieve the maximum score.

Return the output in the following JSON format:
{
  "model": "<model_name>",
  "confidence_score": <overall_confidence_score>,
  "questions": [
    {
      "question": "<question_text>",
      "grade": <score_0_to_100>,
      "suggestions": "<specific_suggestions_for_improvement>"
    },
    ...
  ]
}
Ensure the output is valid JSON and contains all requested fields. Attached are images of questions and answers.
"""


def save_output(model_name, output, prefix=""):
    """Save model output to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}{model_name}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved {model_name} output to {filepath}")

def encode_images(image_paths):
    """Encode multiple images as base64."""
    image_data_list = []
    for idx, path in enumerate(image_paths):
        try:
            with open(path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode("utf-8")
                image_data_list.append({"index": idx + 1, "data": encoded, "path": path})
        except Exception as e:
            print(f"Error encoding {path}: {e}")
    return image_data_list


def call_grok_mini(text_input):
    """Call Grok Mini with text input."""
    url = "https://api.x.ai/v1/grok-mini"  # Hypothetical endpoint
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": GRADING_PROMPT.format(input_content=text_input)}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        result["model"] = "Grok Mini"
        save_output("grok_mini", result, "text_")
        return result
    except requests.RequestException as e:
        print(f"Grok Mini error: {e}")
        return None

def call_chatgpt_mini(text_input):
    """Call ChatGPT Mini with text input."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": GRADING_PROMPT.format(input_content=text_input)}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = json.loads(response.json()["choices"][0]["message"]["content"])
        result["model"] = "ChatGPT Mini"
        save_output("chatgpt_mini", result, "text_")
        return result
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"ChatGPT Mini error: {e}")
        return None

def call_claude(text_input):
    """Call Claude with text input."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json"}
    data = {
        "model": "claude-3-haiku-20240307",
        "messages": [{"role": "user", "content": GRADING_PROMPT.format(input_content=text_input)}],
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = json.loads(response.json()["content"][0]["text"])
        result["model"] = "Claude"
        save_output("claude", result, "text_")
        return result
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Claude error: {e}")
        return None

def call_grok_mini_image(image_paths):
    """Call Grok Mini with multiple images."""
    image_data_list = encode_images(image_paths)
    if not image_data_list:
        print("No images encoded successfully.")
        return None

    url = "https://api.x.ai/v1"  # Hypothetical endpoint
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    data = {
        "prompt": GRADING_PROMPT,
        "images": image_data_list  # Send list of images
    }
    
    try:
        print("test grok")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print(result)
        result["model"] = "Grok Mini"
        save_output("grok_mini", result, "image_")
        return result
    except requests.RequestException as e:
        print(f"Grok Mini image error: {e}")
        return None

def call_chatgpt_mini_image(image_paths, prompt):
    """Call ChatGPT Mini with multiple images."""
    image_data_list = encode_images(image_paths)
    if not image_data_list:
        print("No images encoded successfully.")
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": GRADING_PROMPT},
                *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img['data']}"}} 
                  for img in image_data_list]
            ]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = json.loads(response.json()["choices"][0]["message"]["content"])
        result["model"] = "ChatGPT Mini"
        save_output("chatgpt_mini", result, "image_")
        return result
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"ChatGPT Mini image error: {e}")
        return None

def call_claude_image(image_paths, prompt):
    """Call Claude with multiple images."""
    image_data_list = encode_images(image_paths)
    if not image_data_list:
        print("No images encoded successfully.")
        return None

    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json"}
    data = {
        "model": "claude-3-haiku-20240307",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": GRADING_PROMPT},
                *[{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img["data"]}} 
                  for img in image_data_list]
            ]
        }],
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = json.loads(response.json()["content"][0]["text"])
        result["model"] = "Claude"
        save_output("claude", result, "image_")
        return result
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Claude image error: {e}")
        return None


def extract_text_from_image(image_path):
    """Extract text from image using Tesseract OCR."""
    print("extract_text_from_image")
    tessdata_path = "/opt/homebrew/share/tessdata"
    try:
        with PyTessBaseAPI(path=tessdata_path) as api:
            print("opening image")
            image = Image.open(image_path)
            print(f"opened Image: {image_path}")
            api.SetImage(image)
            print("Set image successful, returning text")
            return api.GetUTF8Text()
    except Exception as e:
        print(f"OCR error: {e}")
        return ""

def compare_models_with_image(image_path, prompt):
    """Compare model outputs using image and prompt."""
    print("Comparing models with image input...")
    results = {
        "grok_mini": call_grok_mini_image(image_path, prompt),
        "chatgpt_mini": call_chatgpt_mini_image(image_path, prompt),
        "claude": call_claude_image(image_path, prompt)
    }
    return results

def compare_models_with_ocr(image_path, prompt):
    """Compare model outputs using OCR-extracted text and prompt."""
    print("Comparing models with OCR-extracted text...")
    text = extract_text_from_image(image_path)
    if not text:
        print("No text extracted from image.")
        return {}

    results = {
        "grok_mini": call_grok_mini(text),
        "chatgpt_mini": call_chatgpt_mini(text),
        "claude": call_claude(text)
    }
    return results

if __name__ == "__main__":
    # Example usage
    questions_image = "/Users/sonmanik/Personal/projects/PaperX/computer_organisation_qp.png"  # Replace with your image path
    # question_text = extract_text_from_image(questions_image)
    # print(question_text)
    answersText = ""
    rootDirectory = "/Users/sonmanik/Personal/projects/PaperX/answersToJpg/answer1"
    listOfAnswers = os.listdir(rootDirectory)
    listOfQuestionAndAnswers = [questions_image] + listOfAnswers
    print(listOfAnswers)
    # for answerLocation in listOfAnswers:
        # answersText+= extract_text_from_image(rootDirectory +"/" + answerLocation)

    # print(answersText)



    # inputPrompt = (f"{GRADING_PROMPT}", question_text, answersText)
    results = {
            "grok_mini": call_grok_mini_image(listOfQuestionAndAnswers),
            # "chatgpt_mini": call_chatgpt_mini_image(inputPrompt),
            # "claude": call_claude_image(inputPrompt)
        }
    
    print(results)
    #
    # prompt = "Grade the question-and-answer content in the provided input."
    #
    # # Test with image input
    # image_results = compare_models_with_image(image_path, prompt)
    # print("\nImage-based results:")
    # for model, result in image_results.items():
    #     if result:
    #         print(f"{model}: {json.dumps(result, indent=2)}")
    #
    # # Test with OCR-extracted text
    # ocr_results = compare_models_with_ocr(image_path, prompt)
    # print("\nOCR-based results:")
    # for model, result in ocr_results.items():
    #     if result:
    #         print(f"{model}: {json.dumps(result, indent=2)}")