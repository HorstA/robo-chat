# robo-chat

## Installation

Install the LangChain CLI if you haven't yet

```bash
pip install -U langchain-cli
```

## Launch LangServe

```bash
poetry shell
langchain serve
```

## Bugfix

in ```/home/horst/.cache/pypoetry/virtualenvs/lff-llm-api-UtOJtALA-py3.12/lib/python3.12/site-packages/langgraph/utils/config.py```

überschreibt ensure_config die Callbackhandler

### Workaround

```py
def ensure_config(*configs: Optional[RunnableConfig]) -> RunnableConfig:
    """Ensure that a config is a dict with all keys present.

    Args:
        config (Optional[RunnableConfig], optional): The config to ensure.
          Defaults to None.

    Returns:
        RunnableConfig: The ensured config.
    """
    empty = RunnableConfig(
        tags=[],
        metadata=ChainMap(),
        callbacks=None,
        recursion_limit=DEFAULT_RECURSION_LIMIT,
        configurable={},
    )
    if var_config := var_child_runnable_config.get():
        empty.update(
            {
                k: v.copy() if k in COPIABLE_KEYS else v  # type: ignore[attr-defined]
                for k, v in var_config.items()
                if v is not None
            },
        )
    for config in configs:
        if config is None:
            continue
        for k, v in config.items():
            if v is not None and k in CONFIG_KEYS:
                # BUGFIX: callbacks are overwritten
                if k == "callbacks" and isinstance(empty[k], list):
                    empty[k] = empty[k] + v
                else:
                    empty[k] = v  # type: ignore[literal-required]
                # END BUGFIX
        for k, v in config.items():
            if v is not None and k not in CONFIG_KEYS:
                empty[CONF][k] = v
    for key, value in empty[CONF].items():
        if (
            not key.startswith("__")
            and isinstance(value, (str, int, float, bool))
            and key not in empty["metadata"]
        ):
            empty["metadata"][key] = value
    return empty
```
