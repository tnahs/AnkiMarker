# anki-marker

<!-- TODO: Document example... -->


``` css

/* [addon-dir]/user_files/markers.css */

anki-marker .highlight {

    /**
    * highlight
    * ==abc==
    * <span class="highlight">abc</span>
    */

    color: hsla(35, 100%, 45%, 1.0);
    font-style: unset;
    font-weight: unset;
    text-decoration: unset;
    background-color: hsla(45, 100%, 75%, 1.0);
}
```

``` python

# [addon-dir]/user_files/markers.json

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
