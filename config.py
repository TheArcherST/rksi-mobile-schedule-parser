import yaml

from pydantic import BaseModel, Field


class Config(BaseModel):
    bot_token: str = Field(regex='[0-9]+:.*')
    owner_id: int
    userflow_path: str = Field('userflow.json')


with open('config.yaml') as fs:
    config = Config.parse_obj(yaml.safe_load(fs))
