# LIBRARY ERROR MESSAGES
JSON_LIBRARY_ERROR_MESSAGES = {
    "Expecting ',' delimiter": [
        "lack of a comma at the end of the line",
        "lack of a comma at the end of the above line",
        "unmatched brackets or quotes"
    ],
    "Expecting ':' delimiter": [
        "a missing colon between the key and the value"
    ],
    "Expecting property name enclosed in double quotes": [
        "the key is not enclosed in double quotes",
        "missing opening or closing quotes for key or value",
        "unexpected characters or tokens present",
        "trailing comma after the last key-value pair"
    ],
    "Expecting value": [
        "missing value for the key",
        "unexpected characters or tokens between the key and value",
        "unmatched quotes for value"
    ],
    "Invalid control character at": [
        "unmatched quotes in the JSON data",
        "improperly escaped characters"
    ],
    "Extra data": [
        "multiple JSON objects present",
        "extra brackets present"
    ]
}

YAML_LIBRARY_ERROR_MESSAGES = {
    "mapping values are not allowed here": [
        "missing colon in the line above",
        "missing mandatory space after the colon in the line above"
    ],
    "expected <block end>, but found": [
        "unexpected characters or tokens at the end of the line",
        "incorrect indentation",
        "missing closing quotes on the line above",
        "unmatched opening and closing quotes",
        "missing mandatory space after the character '-' in the line above"
    ],
    "could not find expected ':'": [
        "unexpected characters or tokens between the key and value",
        "missing mandatory space after the colon in the line above"
    ],
    "found unexpected end of stream": [
        "unmatched opening and closing quotes"
    ],
    "expected '<document start>', but found": [
        "unexpected characters or tokens at the start of the document"
    ],
    "expected alphabetic or numeric character": [
        "unexpected characters or tokens at the start of a string"
    ],
    "found undefined alias": [
        "missing definition of the alias",
        "misusing characters '*', or '&'"
    ],
    "expected chomping or indentation indicators, but found": [
        "unexpected characters or tokens present"
    ],
    "expected the node content, but found": [
        "unexpected characters or tokens present"
    ],
    "found character '@' that cannot start any token": [
        "having a token that starts with the character '@'"
    ]
}
