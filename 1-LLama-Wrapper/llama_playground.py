import gradio as gr
import requests

# Replace with your Hugging Face API token
API_URL = "https://api-inference.huggingface.co/models/<your-llama-model>"
headers = {"Authorization": f"Bearer <your-HF-token>"}

def query(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    result = response.json()
    
    # Hugging Face sometimes returns text under different keys depending on the model
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"
    try:
        return result[0]['generated_text']
    except (IndexError, KeyError):
        return str(result)

# Gradio interface
iface = gr.Interface(
    fn=query,
    inputs="text",
    outputs="text",
    title="LLaMA Playground",
    description="Type a prompt and see LLaMA's response!"
)

iface.launch(server_name="0.0.0.0", server_port=7860, share=True)
