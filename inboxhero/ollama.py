import json
import urllib.request
import urllib.error

class OllamaError(RuntimeError):
    pass

class Ollama:
    def __init__(self, model="qwen3.5", base_url="http://127.0.0.1:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.calls = 0

    def generate(self, prompt, temperature=0.0):
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False,
                              "options": {"temperature": temperature}}).encode()
        req = urllib.request.Request(self.base_url + "/api/generate", data=payload,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise OllamaError(f"Ollama HTTP {e.code}: {e.read().decode(errors='replace')}") from e
        except (urllib.error.URLError, TimeoutError) as e:
            raise OllamaError(f"Ollama unavailable: {e}") from e
        self.calls += 1
        return data.get("response", "").strip()

    def json(self, prompt):
        text = self.generate(prompt)
        if text.startswith("```"):
            text = text.strip().strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise OllamaError(f"Model did not return valid JSON: {text[:500]}") from e
