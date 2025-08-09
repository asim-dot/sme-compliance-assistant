from core.config import settings

def test_config():
    print(f"📋 Project: {settings.PROJECT_NAME}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔑 OpenAI API Key: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Missing'}")
    print(f"📁 Vector DB Path: {settings.VECTOR_DB_PATH}")
    
    if settings.OPENAI_API_KEY:
        print("🚀 Configuration looks good!")
    else:
        print("⚠️  You'll need to add your OpenAI API key to .env file")

if __name__ == "__main__":
    test_config()