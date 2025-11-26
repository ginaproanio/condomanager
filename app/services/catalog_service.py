from app.extensions import cache
from app.models import Module

class CatalogService:
    @staticmethod
    @cache.cached(timeout=3600, key_prefix='global_active_modules')
    def get_active_modules():
        """
        Retorna la lista de módulos activos globalmente.
        Cacheado por 1 hora ya que esto raramente cambia.
        """
        return Module.query.filter_by(status='ACTIVE').all()

