'''
OG Community User Get Function
'''
import os, jwt
from datetime import datetime
from django.db import connections

def CommunitySql(ogUserId: int):
    """Get Community User Info

    Args:
        ogUserId (int)
    Returns:
        id (int)
        email (str)
    """
    key1 = os.getenv('COMMUNITY_KEY_1')  
    key2 = os.getenv('COMMUNITY_KEY_2')
    with connections['community'].cursor() as cursor:
        cursor.execute("SELECT id, CAST(AES_DECRYPT(FROM_BASE64(email), SHA2(CONCAT(%s, %s), 256)) AS CHAR) AS email, name FROM User WHERE id = %s AND deletedAt IS NULL", [key1, key2, ogUserId])
        row = cursor.fetchone()
    
    return row

def checkOgToken(request) -> int:
    """Check the OG Community's Access Token.
    
    Args:
        request: The request object
    Returns:
        userId (int)
    """
    try:
        token = request.headers.get('Authorization')
        token = token.replace('Bearer ', '')
        
        ogUserInfo = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), 'HS256')
        now = datetime.now()
        if ogUserInfo['iat'] >= ogUserInfo['exp'] or now.timestamp() >= ogUserInfo['exp']:
            return 0
        return ogUserInfo['userId']
    except Exception as e:
        return 0

def getSubAccountIdByUserId(ogUserId: int):
    with connections['community'].cursor() as cursor:
        cursor.execute(
            """
            SELECT CONCAT('OG',y3,m1,i1,i4,i2,d1,i3,d2,m2,y4,l1) FROM
(
SELECT 
SUBSTR(U.i,1,2) AS i1,
SUBSTR(U.i,3,1) AS i2,
SUBSTR(U.i,4,4) AS i3,
SUBSTR(U.i,7,4) AS i4,
SUBSTR(U.y,1,1) AS y1,
SUBSTR(U.y,2,1) AS y2,
SUBSTR(U.y,3,1) AS y3,
SUBSTR(U.y,4,1) AS y4,
SUBSTR(U.m,1,1) AS m1,
SUBSTR(U.m,2,1) AS m2,
SUBSTR(U.d,1,1) AS d1,
SUBSTR(U.d,2,1) AS d2,
SUBSTR(U.l,1,1) AS l1
FROM
(SELECT 
	REVERSE(LPAD(id, 11, 0)) AS i,
	date_format(createdAt,'%%Y') AS y,
	date_format(createdAt,'%%m') AS m,
	date_format(createdAt,'%%d') AS d, 
	IF(signType = 'google', 8, IF(signType = 'apple', 7, 1)) AS l
FROM User WHERE id = %s) AS U) AS P
            """, [ogUserId])
        row = cursor.fetchone()
    
    if len(row) == 0:
        return None
    
    return row[0]

def getUserIdBySubAcct(subAcct):
    with connections['community'].cursor() as cursor:
        cursor.execute(
            """
            SELECT
CONCAT(2, 0,y3, y4) AS y,
CONCAT(m1, m2) AS m,
CONCAT(d1, d2) AS d,
CONCAT(l1) AS l,
TRIM(LEADING '0' FROM REVERSE(CONCAT(i1, i2, i3, i4))) AS id
FROM 
(SELECT 
SUBSTR(U.UID, 1+2, 1) AS y3,
SUBSTR(U.UID, 2+2, 1) AS m1,
SUBSTR(U.UID, 3+2, 2) AS i1,
SUBSTR(U.UID, 5+2, 4) AS i4,
SUBSTR(U.UID, 9+2, 1) AS i2,
SUBSTR(U.UID, 10+2, 1) AS d1,
SUBSTR(U.UID, 11+2, 4) AS i3,
SUBSTR(U.UID, 15+2, 1) AS d2,
SUBSTR(U.UID, 16+2, 1) AS m2,
SUBSTR(U.UID, 17+2, 1) AS y4,
SUBSTR(U.UID, 18+2, 1) AS l1
FROM
(SELECT %s AS UID) AS U) AS K;
            """, 
            [subAcct]
        )
        row = cursor.fetchone()
    
    return row