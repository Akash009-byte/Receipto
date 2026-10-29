import base64
import json
import logging
from typing import Dict, Optional
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class ReceiptProcessor:
    """AI Agent for processing receipt images using OpenAI GPT-4 Vision."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            raise

    async def extract_receipt_data_with_gpt(self, image_path: str) -> Dict:
        """Extract receipt data from image using GPT-4 Vision."""
        try:
            logger.info(f"🤖 Processing receipt image: {image_path}")

            base64_image = self.encode_image_to_base64(image_path)

            prompt = """
            You are given a receipt image. Extract the following details in clean JSON format:
            {
              "vendor": "",
              "date": "",
              "items": [
                { "name": "",
                  "price": 0.00,
                  "product_id": ""
                }],
              "subtotal": 0.00,
              "tax": 0.00,
              "total": 0.00
            }
            Ensure all values are extracted as accurately as possible.
            If you cannot find a specific field, use empty string for text fields and 0.00 for numeric fields.
            """

            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",  # Updated to correct model name
                messages=[
                    {
                        "role": "user",
                        "content": [
                            { "type": "text", "text": prompt },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"📄 GPT Response received: {len(content)} characters")

            # Clean up the response
            if content.startswith("```json"):
                content = content[7:]  # remove ```json
            if content.endswith("```"):
                content = content[:-3]  # remove trailing ```

            try:
                parsed_data = json.loads(content)
                print(parsed_data)
                logger.info(f"✅ Successfully extracted receipt data: {parsed_data.get('vendor', 'Unknown vendor')}")
                return parsed_data
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse GPT response as JSON: {e}")
                return {
                    "error": "Failed to parse AI response",
                    "raw_output": content,
                    "json_error": str(e)
                }

        except Exception as e:
            logger.error(f"❌ Error processing receipt with AI: {e}")
            return {
                "error": "AI processing failed",
                "details": str(e)
            }

    def validate_receipt_data(self, data: Dict) -> bool:
        """Validate that the extracted receipt data has required fields."""
        required_fields = ["vendor", "date", "items", "total"]

        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False

        if not isinstance(data["items"], list):
            logger.warning("Items field is not a list")
            return False

        return True

    async def process_receipt_image(self, image_path: str) -> Dict:
        """Main method to process a receipt image and return structured data."""
        logger.info(f"🏪 Starting receipt processing for: {image_path}")

        # Check if file exists
        if not os.path.exists(image_path):
            error_msg = f"Image file not found: {image_path}"
            logger.error(error_msg)
            return {"error": error_msg}

        # Extract data using AI
        receipt_data = await self.extract_receipt_data_with_gpt(image_path)

        # Validate the extracted data
        if "error" not in receipt_data:
            is_valid = self.validate_receipt_data(receipt_data)
            receipt_data["validation_passed"] = is_valid

            if is_valid:
                logger.info(f"✅ Receipt processing completed successfully")
            else:
                logger.warning(f"⚠️ Receipt data validation failed")

        return receipt_data
