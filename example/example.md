```bash
$ curl localhost:8000
Hello, World!


$ curl localhost:8000/users/auth/
{"password": ["This field is required."], "username": ["This field is required."]}


$ curl localhost:8000/users/auth/ -vd 'username=testuser&password=invalidpassword'
{"__all__": ["Please enter a correct username and password. Note that both fields may be case-sensitive."]}


$ curl localhost:8000/users/auth/ -d 'username=testuser&password=testpassword'  -D -
...
Set-Cookie:  sessionid=cakahlvj97a12hsk5f5s8fxpts05iz1f; expires=Wed, 17-Jan-2018 07:29:42 GMT; HttpOnly; Max-Age=1209600; Path=/
...
true


$ curl localhost:8000/users/groups/ -d ''
{"name": ["This field is required."]}


$ curl localhost:8000/users/groups/ -d 'name=test'
{"id": 420, "name": "test", "permissions": []}


$ curl localhost:8000/users/groups/
[{"id": 102, "name": "lol", "permissions": []}, {"id": 420, "name": "test", "permissions": []}]


$ curl localhost:8000/users/group/420
{"name": "test", "id": 420, "permissions": []}


$ curl localhost:8000/users/group/420 -X PATCH
{"name": ["This field is required."]}


$ curl localhost:8000/users/group/420 --request PATCH -d 'name=TESTME'
{"id": 420, "permissions": [], "name": "TESTME"}


$ curl localhost:8000/users/group/420 --request DELETE
1


$ curl localhost:8000/users/group/420 -D - -so /dev/null
HTTP/1.0 404 Not Found
...
```

