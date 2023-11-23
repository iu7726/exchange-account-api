import random, string

def getRequestParams(queryParam):
    params = {}
    for p in queryParam:
        params[p] = queryParam[p]
    
    return params

def random_string(length=6):
    """Generate a random string of given length."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

