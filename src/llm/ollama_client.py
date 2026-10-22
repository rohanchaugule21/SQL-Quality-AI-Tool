"""
Ollama LLM Client - Connects to local Ollama for AI analysis
"""
import requests
import json


class OllamaClient:
    """Client for interacting with local Ollama LLM"""
    
    def __init__(self, model="deepseek-coder:6.7b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def chat(self, prompt: str) -> str:
        """Send a prompt to Ollama and get response"""
        
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure 'ollama serve' is running."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def explain_violation(self, code: str, violation: dict, schema_context: str = "") -> str:
        """Explain a SQL code violation with context"""
        
        prompt = f"""You are a SQL Server expert reviewing code.

Code Issue Found:
- Rule: {violation.get('rule_id')} - {violation.get('message')}
- Line: {violation.get('line')}
- Severity: {violation.get('severity')}

Code Context:
{code}

{f"Schema/Table Info: {schema_context}" if schema_context else ""}

Provide a clear, concise explanation:
1. Why this is a problem (2-3 sentences max)
2. How to fix it (show corrected code)
3. Impact if not fixed (1 sentence)

Be practical and specific. Keep total response under 200 words."""
        
        return self.chat(prompt)


# Quick test function
if __name__ == "__main__":
    # Test the client
    print("Testing Ollama connection...")
    client = OllamaClient()
    
    test_violation = {
        'rule_id': 'SQL001',
        'message': 'Avoid SELECT *',
        'line': 5,
        'severity': 'WARNING'
    }
    
    test_code = """
    CREATE PROCEDURE GetCustomers
    AS
    BEGIN
        SELECT * FROM Customers WHERE City = 'London'
    END
    """
    
    print("\nAsking AI to explain the violation...\n")
    response = client.explain_violation(test_code, test_violation)
    print(response)