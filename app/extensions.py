from flask_sqlalchemy import SQLAlchemy
from app.tenant_query import TenantQuery
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

db = SQLAlchemy(query_class=TenantQuery)
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
