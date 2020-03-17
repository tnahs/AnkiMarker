# anki-marker

<!-- TODO: Doument example... -->


``` css

/* [addon-dir]/user_files/user.css */

anki-marker .accent {

    /**
    * accent
    * *abc*
    * <span class="accent">abc</span>
    */

    color: hsla(230, 60%, 70%, 1.0);
    font-style: unset;
    font-weight: 400;
    text-decoration: unset;
    background-color: unset;
}
```

``` json

// [addon-dir]/user_files/styles.json

{
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
