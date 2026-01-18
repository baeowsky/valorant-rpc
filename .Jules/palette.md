## 2025-10-27 - Localization Fallback Bug
**Learning:** The custom `Localizer.get_localized_text` implementation failed to fallback to English if the *last* key in the chain was missing in the target locale (it returned `None` instead of triggering the exception handler).
**Action:** Always ensure custom localization logic handles "leaf node missing" cases explicitly, not just intermediate node failures.
