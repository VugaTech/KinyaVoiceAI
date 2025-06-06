class Settings :
  def __init__(self):
    self.port = 8000
    self.host = f"http://localhost:{self.port}"
    self.language = "en"
    self.version = "v1"
    self.name = f"KinyaVoice AI {self.version}"
    self.description = "KinyaVoice AI is a voice assistant that can help you with various tasks."
    self.authors = []
    self.db_config = {
      "host" : "localhost",
      "port" : 5432,
      "user" : "postgres",
      "password" : "#nelprox92",
      "db_name" : "kinyvoiceai"
    }
    self.cors_origins = ["*"]
    self.api_prefix = f"/api/{self.version}"

  def get_db_url(self):
    return f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['db_name']}"
  
  def get_cors_origins(self):
    return self.cors_origins
  
  def get_app_url(self):
    return self.host

