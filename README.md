<style>
    mark {
        padding: 1px 3px;
        color: hsla(35, 100%, 45%, 1) !important;
        background: hsla(45, 100%, 75%, 1) !important;
        border-radius: 3px;
    }
</style>

# AnkiMarker

Add custom Markdown-like <mark>highlighting</mark> to your Anki cards!

<!--
## Installation

Download and run the latest [`AnkiMarker.ankiaddon`][releases] release.
-->

## Usage

```css
marker.highlight {
    /**
    * name:     highlight
    * syntax:   ==abc==
    * html:     <span class="highlight">abc</span>
    */

    color: hsla(35, 100%, 45%, 1);
    font-style: unset;
    font-weight: unset;
    text-decoration: unset;
    background-color: hsla(45, 100%, 75%, 1);
}
```

```json
{
    "parent-classes": [],
    "styles": [
        {
            "name": "Highlight",
            "markup": "==",
            "classes": ["highlight"]
        }
    ]
}
```

## Development

1. Install the required `[python-version]`. See the [Anki development][anki-dev]
   docs for more information.

    ```shell
    pyenv install [python-version]
    ```

2. Clone this repository.

    ```shell
    git clone git@github.com:tnahs/AnkiMarker.git
    ```

3. Set `[python-version]` as the local version:

    ```shell
    cd ./AnkiMarker
    pyenv local [python-version]
    ```

4. Create and enter a virtual environment:

    ```shell
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    ```

5. Install required packages:

    ```shell
    pip install -r requirements.txt
    ```

6. Set development environment variables. See
   [Anki development | Environment Variables][env-var] for more information.

    Required:

    ```shell
    export ANKI_ADDON_DEVELOPMENT=1
    ```

    Optional:

    ```shell
    export ANKIDEV=1
    export LOGTERM=1
    export DISABLE_QT5_COMPAT=1
    ```

[anki-dev]: https://github.com/ankitects/anki/blob/main/docs/development.md
[env-var]: https://github.com/ankitects/anki/blob/main/docs/development.md#environmental-variables
[releases]: https://github.com/tnahs/AnkiMarker/releases
