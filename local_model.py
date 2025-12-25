import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class LocalCausalLMRunner:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model_name = model_path.split("/")[-1]

        print("CUDA available:", torch.cuda.is_available())
        print("CUDA device count:", torch.cuda.device_count())

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

        # Load model with device mapping
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",
            dtype=torch.bfloat16
        )

        print(f"Allocated: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        print(f"Cached:    {torch.cuda.memory_reserved(0) / 1024**2:.2f} MB")
        
        # Print memory footprint
        print(f"Memory footprint: {self.model.get_memory_footprint() / 1024**2:.2f} MB")
        
        # Check which device the model is on
        print(f"Model is loaded on: {self.model.device}")

    def extract_code(self, code):
        lang_labels = ["py", "Python", "python", "cpp", "c++", "C++", "C", "c", "Go", "go", "Java", "java"]
    
        # Normalize and strip the text
        code = code.replace('\r\n', '\n').strip()
    
        # Find first triple-quote block (''')
        first = code.find("```")
        if first == -1:
            return code  # No code block found
    
        # Find the second triple quote starting after the first
        second = code.find("```", first + 3)
        if second == -1:
            return code[3 + code.find("```")]  # No closing block found
    
        # Extract content between the triple quotes
        block = code[first + 3:second].strip()
    
        # Split into lines
        lines = block.splitlines()
    
        # Remove language label if present
        if lines:
            first_line = lines[0].strip("` ").strip()
            if first_line in lang_labels:
                lines = lines[1:]
    
        return "\n".join(lines).strip()
    
    def run(self, message, max_new_tokens=1000):
        context_msg = message[0]["content"] if message[0]["role"] == "system" else ""
        user_msg = message[1]["content"] if message[1]["role"] == "user" else message[0]["content"]
        prompt = context_msg + "\n" + user_msg + "\n@@ Model's Response\n"

        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        # Generate output
        outputs = self.model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=max_new_tokens,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True).split("@@ Model's Response\n")[-1]
        response = self.extract_code(response)
        return response
