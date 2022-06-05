from pydantic import BaseSettings


class Settings(BaseSettings):
    jira_login: str
    jira_password: str
    jira_base_url: str

    sqlite_db_path: str
    timezone: str

    class Config:
        env_file = ".env"
