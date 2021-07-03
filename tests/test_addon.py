# import pathlib

# import pytest
# from addon.src.addon import AnkiMarker
# from addon.src.errors import ConfigError


# def test_config_missing() -> None:

#     # When running in Anki, '<AnkiMarker>' is not instantiated with a
#     # 'config' but reads 'markers.json' from  the addon directory. This
#     # path is stored as a class variable in '<AnkiMarker>.config_path'. We
#     # simulate a missing file by monkey-patching 'config_path'.
#     AnkiMarker.config_path = pathlib.Path("/missing/path/to/styles.json")

#     with pytest.raises(ConfigError):
#         AnkiMarker()


# def test_config_empty() -> None:

#     with pytest.raises(ConfigError):
#         AnkiMarker(config=[])

#     with pytest.raises(ConfigError):
#         AnkiMarker(config={})


# def test_config_missing_styles() -> None:

#     # Missing 'styles'.
#     bad_config: dict = {}
#     with pytest.raises(ConfigError):
#         AnkiMarker(config=bad_config)
