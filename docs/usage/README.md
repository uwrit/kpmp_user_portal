# How to Use
## Retrieve Authorization for User By ID
The most common use case for this app is for a server side application, sitting behind a Shibboleth SP, to issue requests for user authorization when a user first logs into the application. In this situation, Shibboleth will have already provided the identity of the user, the application needs to complete the IAM picture by fetching the authorization data.

```
GET /api/user/johndoe@institution.edu HTTP/1.1
...snipped...
Host: userportal.kpmp.org
Accept: application/json
X-API-TOKEN: {client-token-issued-by-admin}
...snipped...
```
returns as json document structured like:
```typescript
{
    "_id": string,
    "shib_id": string,
    "first_name": string,
    "last_name": string,
    "email": string,
    "phone_numbers": string[],
    "fax_numbers": string[],
    "role": string,
    "job_title": string,
    "organization_id": string,
    "groups": string[],
}
```
for example:
```json
{
    "_id": "5cb63564cb58ef568573b14d",
    "shib_id": "johndoe@institution.edu",
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@dept.institution.edu",
    "phone_numbers": ["555-555-5555"],
    "fax_numbers": ["555-555-5556"],
    "role": "Tissue Registrar",
    "job_title": "Tissue Tech",
    "organization_id": "5cb63564cb58ef568573b12f",
    "groups": [
        "example_app_granting_group",
        "example_role_group",
        "example_app_admin_granting_group"
    ]
}
```

## Search Users
You can search for users using query parameters, so long as the document structure supports that field.
```
GET /api/user?last_name=Doe HTTP/1.1
...snipped...
Host: userportal.kpmp.org
Accept: application/json
X-API-TOKEN: {client-token-issued-by-admin}
...snipped...
```
returns an array of structures that looks like (note that groups are not available on this endpoint):
```typescript
{
    "_id": string,
    "shib_id": string,
    "first_name": string,
    "last_name": string,
    "email": string,
    "phone_numbers": string[],
    "fax_numbers": string[],
    "role": string,
    "job_title": string,
    "organization_id": string
}
```
for example:
```json
[
    {
        "_id": "5cb63564cb58ef568573b14d",
        "shib_id": "johndoe@institution.edu",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@dept.institution.edu",
        "phone_numbers": ["555-555-5555"],
        "fax_numbers": ["555-555-5556"],
        "role": "Tissue Registrar",
        "job_title": "Tissue Tech",
        "organization_id": "5cb63564cb58ef568573b12f"
    }
]
```