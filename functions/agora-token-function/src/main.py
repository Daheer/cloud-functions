from appwrite.client import Client
import os
import time
from agora_token_builder import RtcTokenBuilder
import json

# This Appwrite function will be executed every time your function is triggered
def main(context):
    # Log that the function is being executed
    context.log("Agora Token Generator function executing")
    
    try:
        # Parse request body
        # Appwrite passes the request body as a string, so we need to parse it
        if context.req.body:
            try:
                body = json.loads(context.req.body)
                context.log(f"Request body: {body}")
            except json.JSONDecodeError:
                context.log("Failed to parse request body as JSON")
                return context.res.json({"error": "Invalid JSON in request body"}, status_code=400)
        else:
            body = {}
        
        # Get parameters from the request body
        channel_name = body.get("channelName")
        uid = body.get("uid", 0)  # Default to 0 if not provided
        expire_time = body.get("expireTime", 3600)  # Default to 1 hour
        
        # Validate required parameters
        if not channel_name:
            context.log("Missing required parameter: channelName")
            return context.res.json({"error": "channelName is required"}, status_code=400)
            
        # Retrieve Agora credentials from environment variables
        app_id = os.environ.get("AGORA_APP_ID")
        app_certificate = os.environ.get("AGORA_APP_CERTIFICATE")
        
        # Validate that credentials are available
        if not app_id or not app_certificate:
            context.log("Agora credentials not configured")
            return context.res.json({"error": "Agora credentials are not set"}, status_code=500)
        
        # Generate token
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expire_time
        
        # Build token with UID
        token = RtcTokenBuilder.buildTokenWithUid(
            app_id, 
            app_certificate, 
            channel_name, 
            uid, 
            1,  # Role: 1 for publisher
            privilege_expired_ts
        )
        
        context.log(f"Token generated successfully for channel: {channel_name}")
        
        # Return the token directly in the response
        # This matches what your Flutter client expects
        return context.res.json({
            "token": token
        })
        
    except Exception as e:
        context.error(f"Error generating token: {str(e)}")
        return context.res.json({"error": str(e)}, status_code=500)
