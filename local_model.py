import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import gc

class LocalCausalLMRunner:
    def __init__(self, model_path: str):
        self.total_run = 0
        self.model_path = model_path
        self.model_name = model_path.split("/")[-1]

        # ---- CUDA sanity (DO NOT TOUCH CUDA IF BROKEN) ----
        try:
            cuda_ok = torch.cuda.is_available()
        except Exception:
            cuda_ok = False

        print("CUDA available:", cuda_ok)
        print("CUDA device count:", torch.cuda.device_count())

        # ---- Select device safely ----
        if cuda_ok:
            self.device = torch.device("cuda")
            dtype = torch.bfloat16
            device_map = "auto"
        else:
            self.device = torch.device("cpu")
            dtype = torch.float32
            device_map = None   # IMPORTANT

        # ---- Load tokenizer ----
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            use_fast=True
        )

        # ---- Load model (SAFE) ----
        with torch.no_grad():
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map=device_map,
                dtype=dtype,
                low_cpu_mem_usage=True
            )

        self.model.eval()

        # ---- Diagnostics (guarded) ----
        if cuda_ok:
            print(f"Allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
            print(f"Cached:    {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

        print(f"Model loaded on: {self.device}")

    # --------------------------------------------------

    def extract_code(self, code: str):
        lang_labels = {"py", "python", "cpp", "c++", "c", "java", "go"}
        code = code.replace("\r\n", "\n").strip()
        start = code.find("```")
        if start == -1:
            return code  # keep everything if no code block
        end = code.find("```", start + 3)
        if end == -1:
            end = len(code)
        block = code[start + 3:end].strip()
        lines = block.splitlines()
        if lines and lines[0].strip().lower() in lang_labels:
            lines = lines[1:]  # remove language label
        return "\n".join(lines).strip()


    # --------------------------------------------------

    def run(self, message, max_new_tokens=1024):
        self.total_run += 1
        context_msg = ""
        user_msg = ""

        if message[0]["role"] == "system":
            context_msg = message[0]["content"]
            user_msg = message[1]["content"]
        else:
            user_msg = message[0]["content"]

        prompt = context_msg + "\n" + user_msg + "\n@@ Model's Response\n"

        # ---- HARD TOKEN CAP (MANDATORY) ----
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048   # SAFE FOR MAGICODER
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        input_len = inputs["input_ids"].shape[1]
        use_kv_cache = input_len <= 1024  # safe for 2 GPUs
        
        # ---- Generation (safe) ----
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=False,
                use_cache=use_kv_cache,
                max_new_tokens=max_new_tokens
            )

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        response = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        print("before")
        print("-"*100)
        print(response)
        print("="*100)
        response = response.split("@@ Model's Response\n")[-1]
        print("after")
        print("-"*100)
        print(response)
        print("="*100)
        
        if self.total_run % 50 == 0:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
        
        try:
            response = self.extract_code(response)            
            print("filtered")
            print("-"*100)
            print(after)
            print("="*100)

            return response
        except Exception:
            return response
