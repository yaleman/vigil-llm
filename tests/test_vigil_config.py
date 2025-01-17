from pathlib import Path
from vigil.core.config import ConfigFile


def test_config() -> None:
    configfile = Path("conf/docker.conf")
    config = ConfigFile.from_config_file(configfile)
    print(config.model_dump_json(indent=4))
    assert config.embedding.model == "openai"
