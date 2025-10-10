import os
import logging
from jinja2 import Environment, FileSystemLoader
from ghostai.pipeline.pipeline import Pipeline

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def run_demo():
    # Setup logging before creating pipeline
    
    templates = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith(".jinja")]
    print(f"\n🧪 Running GhostAI DLP on {len(templates)} Jinja templates...\n")

    # Initialize GhostAI DLP pipeline
    pipeline = Pipeline()

    for tname in templates:
        template = env.get_template(tname)
        # Create comprehensive context for all templates
        context = {
            # Basic variables
            "user": "John Doe",
            "email": "john.doe@example.com", 
            "api_key": "sk-proj-abc123fakeKEY",
            "ssn": "123-45-6789",
            "password": "SuperSecret123!",
            
            # Safe prompt template
            "user_name": "John Doe",
            "doc_text": "This is a sample document about machine learning.",
            "doc_category": "Technical",
            "doc_priority": "High",
            "output_format": "Markdown",
            "max_length": "500",
            "writing_style": "Professional",
            "department": "Engineering",
            "project_name": "ML Pipeline",
            
            # Leak payload template
            "user": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "(555) 123-4567",
                "ssn": "123-45-6789",
                "api_key": "sk-proj-abc123fakeKEY"
            },
            "db": {
                "password": "SuperSecret123!",
                "user": "admin",
                "host": "localhost",
                "port": "5432",
                "name": "mydb"
            },
            "aws": {
                "access_key": "AKIAIOSFODNN7EXAMPLE",
                "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            },
            "env": {
                "openai_key": "sk-proj-abc123fakeKEY"
            },
            "jwt": {
                "secret": "myJWTSecretKey123"
            },
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----",
            
            # Code review template
            "developer": {"name": "Jane Smith", "email": "jane.smith@company.com"},
            "pr": {"number": "123"},
            "repo": {"name": "myapp"},
            "code_changes": "Added authentication middleware",
            "env": {"name": "production"},
            "auth": {"method": "JWT", "roles": "admin,user"},
            "data": {"protection": "encrypted"},
            
            # Incident report template
            "incident": {"id": "INC-2024-001", "severity": "High", "status": "Open"},
            "service": {"name": "user-service", "env": "production", "account": "service-account", "api_key": "sk-proj-abc123fakeKEY"},
            "users": {"count": "150", "list": "john.doe@company.com, jane.smith@company.com"},
            "error": {"message": "Database connection timeout", "stack": "ConnectionError at line 45"},
            "logs": {"location": "/var/log/app.log"},
            
            # API docs template
            "api": {"endpoint": "/api/v1/users", "method": "POST", "version": "v1"},
            "auth": {"type": "Bearer", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "key": "sk-abc123fakeKEY"},
            "user": {"id": "12345", "email": "john.doe@example.com", "phone": "(555) 123-4567", "ssn": "123-45-6789"},
            "response": {"content_type": "application/json", "status_codes": "200, 400, 401"},
            "db": {"table": "users", "connection_string": "postgresql://admin:MyPassword123@localhost:5432/mydb", "credentials": "admin:MyPassword123"},
            
            # Support ticket template
            "ticket": {"id": "TICKET-2024-001", "priority": "High", "status": "Open"},
            "customer": {"name": "John Doe", "email": "john.doe@example.com", "phone": "(555) 123-4567", "ssn": "123-45-6789", "account_id": "ACC-12345"},
            "issue": {"description": "Unable to login to account"},
            "redis": {"password": "RedisSecret123!"},
            "logs": {"error": "Authentication failed", "stack": "AuthError at line 23", "user_agent": "Mozilla/5.0..."}
        }
        
        rendered = template.render(**context)
        
        print(f"--- Testing {tname} ---")
        result = pipeline.run(rendered)
        
        if result["score"] > 0:
            print(f"🚨 BLOCKED: {len(result['flags'])} scanner(s) flagged, {sum(len(scanner['reasons']) for scanner in result['breakdown'] if scanner['flagged'])} findings")
            for scanner in result['breakdown']:
                if scanner['flagged']:
                    print(f"   📊 {scanner['name']}: {len(scanner['reasons'])} findings")
        else:
            print("✅ CLEAN")
        print()

if __name__ == "__main__":
    run_demo()
