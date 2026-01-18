## 2024-05-22 - [HIGH] Reflected XSS in Webserver
**Vulnerability:** Reflected Cross-Site Scripting (XSS) in Flask routes `/valorant/request` and `/valorant/join`. The `region` parameter was reflected directly in the response.
**Learning:** Returning f-strings from Flask routes returns `text/html` by default, and f-strings do not provide automatic escaping. This allows XSS if user input is included.
**Prevention:** Always use `markupsafe.escape()` to sanitize user input before including it in response strings, or use a templating engine (Jinja2) which handles escaping automatically.
