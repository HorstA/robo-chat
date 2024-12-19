# Robo-Chat

### 🚧under construction🚧

Robo-Chat ist ein Projekt, das zeigen soll, wie Multi-Agent-Systeme für die Kommunikation in der Robotik eingesetzt werden können.

Zur Zeit ist der Fokus auf Supervision, ein Art Chat-Room für Roboter mit Moderator.
Diser Fokus kann sich noch ändern.

Wichtig ist mir auch zu zeigen, dass Modularität ein wichtiger Faktor bei der Entwicklung ist und dass dies nicht auf Kosten der Hardwareanforderung geht.

Deshalb läuft alles (dieser Server, UnstructuredIO, PGVector, ...) in Portainer (~Docker) auf einem RasperryPI 4B mit 2GB ([LinkedIn-Post](https://www.linkedin.com/posts/horst-amper_llm-rag-l%C3%B6sung-auf-minimal-hardware-dsgvo-konform-activity-7269009508662722560-wk8D?utm_source=share&utm_medium=member_desktop))! \
Der bekommt einen Akku, WLAN und ein Breadboard und ist somit komplett kabellos und damit mobil.

Das Breadboard simuliert später die beteiligten Roboter, etwa einen autonomen Staubsauger o.ä.
Über die Pins vom Raspi werden LEDs angesteuert, die den Zustand simulieren (offline, ready, busy = aus, leuchtet, blinkt)

Die Dockerstruktur in Verbindung mit APIs liebe ich mittlerweilen. So können Teams an unterschiedlichen Stellen arbeiten und mit einem Befehl ihren Docker updaten. Sooo easy!

Das Projekt läuft mit mehreren LLMs und LLM-Anbieter.

Alle Einstellungen sollen in die ```.env```. Die dann logischerweise nicht ins GitHub-Repo!

Viel Spaß

## Installation

Mach alles über Poetry, PIP nervt ;-) \
kopiere die ```.env.example```, erstell dir daraus deine ```.env```

## Launch LangServe

```bash
poetry shell
langchain serve
```

## Bugfix

Mega-fieser Bug in Langchain. Ums kurz zu fassen. In den Tiefen der Runnables überschreibt Langchain die Runnabe_Config, so dass wenn du mit LangGraph einen Agent baust und ihn über LangServe bereitstellst, wird plötzlich von LangFuse (ich weiß, viele Langs) nicht mehr mitgeloggt. \
Das waren ein paar stressige Tage...

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
