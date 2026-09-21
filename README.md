# Titan Infra Test code

This repository contains an application that queries and stores usernames and its birthdays.

Unless configured, the data is stored locally in an SQLite database.

:memo: [Architecture](./ARCHITECTURE.md)

### Example requests

```sh
# Create new user
curl -v -XPUT -H "Content-Type: application/json" -d '{"birthdate": "2000-09-24"}' http://127.0.0.1:8000/hello/yourusername

# Get user
curl http://127.0.0.1:8000/hello/yourusername
```
