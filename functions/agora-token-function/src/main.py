import os
import time
from agora_token_builder import RtcTokenBuilder

def main(context):
    # Retrieve Agora credentials from environment variables
    app_id = os.environ.get("AGORA_APP_ID")
    app_certificate = os.environ.get("AGORA_APP_CERTIFICATE")

    # Validate that credentials are available
    if not app_id or not app_certificate:
        return context.res.json({"error": "Agora credentials are not set."}, status_code=500)

    print(context.req.body)

    # Access the request body directly
    body = context.req.body

    channel_name = body.get("channelName")
    uid = body.get("uid", 0)  # Default to 0 if not provided
    expire_time = body.get("expireTime", 3600)  # Default to 1 hour

    # Validate required parameters
    if not channel_name:
        return context.res.json({"error": "channelName is required."}, status_code=400)

    # Generate token
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expire_time

    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, 1, privilege_expired_ts
    )

    return context.res.json({"token": token})
