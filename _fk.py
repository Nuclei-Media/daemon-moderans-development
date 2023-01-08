import redis

# connect to docker redis

rd = redis.Redis(host="localhost", port=6379, db=0)
rd.set("test", str({"few": 123}))

print(rd.get("test"))
