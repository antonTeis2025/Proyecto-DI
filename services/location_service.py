from typing import List, Optional
from sqlalchemy import select
from database import get_session
from models.locations import Province, Municipio  # Asegúrate de importar Municipio


class LocationService:

    @staticmethod
    def get_all_provinces() -> List[Province]:
        """Devuelve todas las provincias ordenadas alfabéticamente."""
        with get_session() as session:
            # 1. Construimos la sentencia (select), NO la ejecutamos aún
            stmt = select(Province).order_by(Province.name)

            # 2. La pasamos a scalars() para ejecutarla y obtener objetos limpios
            return list(session.scalars(stmt).all())


    @staticmethod
    def get_province_by_name(name: str) -> Optional[Province]:
        with get_session() as session:
            stmt = select(Province).where(Province.name == name)
            return session.scalar(stmt)

    @staticmethod
    def get_municipalities_by_province(province_id: int) -> List[Municipio]:
        """Devuelve los municipios filtrados por ID de provincia."""
        with get_session() as session:
            stmt = (
                select(Municipio)
                .where(Municipio.province_id == province_id)
                .order_by(Municipio.name)
            )
            return list(session.scalars(stmt).all())


    @staticmethod
    def get_province_by_municipality(municipality_id: int) -> Optional[Province]:
        """
        Dado el ID de un municipio, devuelve el objeto Provincia al que pertenece.
        Realiza un JOIN optimizado.
        """
        with get_session() as session:
            # SELECT Province.* FROM provinces
            # JOIN municipios ON municipios.idprov = provinces.idprov
            # WHERE municipios.idmuni = :id
            stmt = select(Province).join(Municipio).where(Municipio.id == municipality_id)
            return session.scalar(stmt)


    @staticmethod
    def get_municipio_by_id(id: int) -> Optional[Municipio]:
        with get_session() as session:
            stmt = select(Municipio).where(Municipio.id == id)
            return session.scalar(stmt)