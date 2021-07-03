# anki-marker

## Installation

Download `*.ankiaddon` from `./bundle`

## Usage

TODO

``` css
/* [addon-dir]/user_files/markers.css */

anki-marker .highlight {

    /**
    * name:     highlight
    * syntax:   ==abc==
    * html:     <span class="highlight">abc</span>
    */

    color: hsla(35, 100%, 45%, 1.0);
    font-style: unset;
    font-weight: unset;
    text-decoration: unset;
    background-color: hsla(45, 100%, 75%, 1.0);
}
```

``` json
// [addon-dir]/user_files/markers.json

{
    "parent-classnames": [],
    "styles": [
        {
            "name": "Highlight",
            "markup": "==",
            "classname": "highlight"
        },
    ]
}
```

## Development

```shell
export ANKI_ADDON_DEV=True
```
