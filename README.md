# anki-marker

<!-- TODO: Doument example -->


In `[addon-dir]/user_files/user.css`...

``` css

anki-marker .accent {

    /**
    * accent
    * *abc*
    * <span class="accent">abc</span>
    */

    color: hsla(230, 60%, 70%, 1.0);;
    font-style: unset;
    font-weight: 400;
    text-decoration: unset;
    background-color: unset;
}

```

In `[addon-dir]/config.json`...

``` json
{
    "add_context_menu": true,
    "parent_classnames": [],
    "styles": [
        {
            "name": "Accent",
            "markup": "*",
            "classname": "accent"
        }
    ]
}
```
