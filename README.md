# mikrotik-api

A tool for configuring a Mikrotik router via their API.

## Incantations

Basic proof-of-connection

```
<<< /login
<<< =name=admin
<<< =password=5LPLEPAYH4
<<< 
>>> !done
>>> 
/user/getall

<<< /user/getall
<<< 
>>> !re
>>> =.id=*1
>>> =name=admin
>>> =group=full
>>> =address=
>>> =last-logged-in=jan/02/1970 00:11:54
>>> =expired=false
>>> =disabled=false
>>> =comment=system default user
>>> 
>>> !done
>>> 
```


Basic failure to connect (wrong password)

```
python3 example.py 192.168.88.1 admin wrongpassword


<<< /login
<<< =name=admin
<<< =password=5LPLEPAYH
<<< 
>>> !trap
>>> =message=invalid user name or password (6)
>>> 
>>> !done
>>>
```
