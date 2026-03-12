import requests


class StoryGenerator:

    def __init__(self, config):

        self.api_url = config["ai"]["api_url"]
        self.api_key = config["ai"]["api_key"]
        self.model = config["ai"]["model"]
        self.temperature = config["ai"]["temperature"]
        self.max_tokens = config["ai"]["max_tokens"]

    def generate(self, prompt):

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        r = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=120
        )

        r.raise_for_status()

        data = r.json()

        return data["choices"][0]["message"]["content"]