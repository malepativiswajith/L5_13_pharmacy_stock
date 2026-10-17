# Static Code Analysis Issues

Line numbers refer to the original `pharmacy_system.py` from the starter repository and may shift after edits.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| SQL injection in patient lookup | Security — High | 382–387 | The patient name was interpolated directly into SQL with `%`, allowing input to alter the query. | Use a parameterized query with `?` placeholders and pass the name as a parameter. |
| Broad exception handling in dispensing | Reliability — High | 397–416 | A bare `except:` swallowed every error, including programming errors, and returned `False` without explaining the cause. | Validate expected conditions explicitly and avoid catching exceptions that should not be hidden. |
| Dispensing beyond available stock | Logic bug — High | 409–410 | The stock count was decremented without checking availability, so stock could become negative. | Check medicine existence and available quantity before changing stock. Reject non-positive quantities. |
| Allergy matching is case-sensitive and simplistic | Safety/logic — High | 403–407 | A case mismatch such as `ibuprofen` versus `Ibuprofen` can bypass a direct string check. | Normalize case and whitespace, split stored allergy entries, and compare normalized medicine names. |
| Mutable default argument | Bug/maintainability — Medium | 389 | `batch_log=[]` reuses the same list across calls, so batch records can leak between calls. | Use `None` as the default and create a new list inside the function. |
| File handles not safely managed | Reliability — Medium | 432–449 | Files were opened without `with`; errors could leave resources unclosed or be silently ignored. | Use context managers, explicit UTF-8 encoding, and catch only expected file/JSON errors. |
| Expiry reporting includes already expired medicines | Logic bug — Medium | 418–430 | A negative day difference can still be less than `days`, so expired items may be reported as “expiring soon.” | Compare dates against today and the cutoff date, excluding items whose expiry is before today. |
| Inconsistent function naming and style | Style — Low | 451 | `printStock` does not follow Python's `snake_case` naming convention; spacing and imports were inconsistent. | Rename it to `print_stock`, remove unused imports, and format consistently. |
| Negative stock setup value | Data validation — Medium | 471 | The demo added `-15` units of Ibuprofen, creating an invalid stock count. | Reject non-positive stock additions and correct the demo data to use a positive quantity. |
