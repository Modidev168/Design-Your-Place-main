import requests
from django.conf import settings

MODEL_NAME = "@cf/black-forest-labs/flux-2-klein-9b"

def generate_room_design(design):
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{settings.CLOUDFLARE_ACCOUNT_ID}/ai/run/{MODEL_NAME}"
    )
    with open(design.original_image.path,"rb") as image_file:
        files = {
            "input_image_0": (
                design.original_image.name,
                image_file,
                "image/jpeg"
            ),
        }

        prompt = f"""
            Redesign this existing {design.room_type} in a
            {design.design_style} interior design style.

            IMPORTANT:
            - Preserve the original room architecture.
            - Keep walls in the same positions.
            - Keep windows and doors in the same positions.
            - Keep the camera perspective.
            - Keep the room proportions.
            - Replace or improve furniture and decoration.
            - Improve lighting.
            - Create a realistic professional interior design.
            - Do not change the basic structure of the room.

            User's additional requirements:
            {design.prompt}

            The result should look like a realistic photograph
            of the redesigned room.
            """
        data = {
            "prompt": prompt,
            "width":1024,
            "height":1024,
            "guidance":4.0,
            }
        headers = {
            "Authorization": (
                f"Bearer {settings.CLOUDFLARE_API_TOKEN}"
            ),
        }
        response = requests.post(
            url,
            headers = headers,
            files = files,
            data=data,
            timeout = 180,
        )
    print("Cloudflare status:",response.status_code)
    if response.status_code != 200:
            print("Cloudflare error:")
            print(response.text)

            raise Exception(
             f"Cloudflare API error: {response.text}"
        )
    result = response.json()

    print("Cloudflare response received")

    if not result.get("success"):
        raise Exception(
            f"Cloudflare generation failed: {result}"
        )

    # Cloudflare returns the generated image as base64
    image_base64 = result["result"]["image"]

    return image_base64
