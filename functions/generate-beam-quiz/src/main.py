import os
import time
import json
import random
import base64
from google import genai
from google.genai import types


def generate(client, profession, experience):
    
    model = "gemini-2.5-flash-preview-04-17"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""You are helping me onboard users to a professional connection app called Beam, where users can beam their details (name, experience, expertise) and can connect with nearby professionals.

As part of the verification process, we need to verify that people that are truly in that field and have that level of experience.

So I will give your the profile of a person and you will generate a list of 10 multiple choice questions and answers which are suitable to their level. The questions should be easily answerable for a person at that skill level because they will only have 5 seconds to pick an answer

Profile
Field: {profession}
Years of Experience: {experience}"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.OBJECT,
                required = ["question", "options", "answer"],
                properties = {
                    "question": genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                    "options": genai.types.Schema(
                        type = genai.types.Type.ARRAY,
                        items = genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                    ),
                    "answer": genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                },
            ),
        ),
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    
    return response.text


# This Appwrite function will be executed every time your function is triggered
def main(context):
    # Log that the function is being executed
    context.log("Beam Quiz Generation Function Running...")
    
    try:

        # Parse request body
        # Appwrite passes the request body as a string, so we need to parse it
        if context.req.body:
            try:
                body = context.req.body
                context.log(f"Request body: {body}")
            except json.JSONDecodeError:
                context.log("Failed to parse request body as JSON")
                return context.res.json({"error": "Invalid JSON in request body"})
        else:
            body = {}

        # Get parameters from the request body
        profession = body.get("profession")
        experience = body.get("experience", 1)
        
        # Validate required parameters
        if not profession:
            context.log("Missing required parameter: profession")
            return context.res.json({"error": "profession is required"})

        gemini_api_key = os.environ.get("GEMINI_API_KEY")

        client = genai.Client(
            api_key=gemini_api_key,
        )
            
        # Validate that credentials are available
        if not gemini_api_key:
            context.log("Gemini credentials not configured")
            return context.res.json({"error": "Gemini credentials are not set"})
        
        
        response = generate(client, profession, experience)

        if len(response) == 0: return context.res.json({"error": "Quiz list is empty"})
        
        if len(response >= 5):
            final_response = random.sample(response, 5)
        else:
            final_response = response
        
        # Return the token directly in the response
        # This matches what your Flutter client expects
        return context.res.json({
            "questions": final_response
        })
        
    except Exception as e:
        context.error(f"Error generating quiz: {str(e)}")
        return context.res.json({"error": str(e)})
