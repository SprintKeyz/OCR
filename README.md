## APIs and Libraries Tested

- Google Vision AI
- EasyOCR
- ChatGPT Vision
- PyTesseract

## Running Examples

> Note: When running cloud-based projects, API keys and credentials are not included since this is a public repo. To run ChatGPT Vision, you need to create a `secrets.py` file inside the `chatgpt_vision` directory, then create a variable called `openai_api_key` and set it equal to your key. For Google Vision AI, you need to create a GCP project and use the Google Cloud CLI to authenticate your project and connect it to a cloud account.

1. Create a virtual environment using `python -m venv venv`
2. Activate said environment using `.\venv\bin\activate` on windows or `source venv/bin/activate` on linux
3. Install dependencies with `pip install -r requirements.txt`
4. Run the examples: `cd` into the proper folder, then run the test.py program within it.
