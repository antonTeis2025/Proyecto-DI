from typing import List
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Province(Base):
    __tablename__ = "provincias"

    # Mapeamos 'id' de python a 'idprov' de la BBDD
    id: Mapped[int] = mapped_column("idprov", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("provincia", String(50), nullable=False)

    municipalities: Mapped[List["Municipio"]] = relationship("Municipio", back_populates="province")

    def __repr__(self):
        return f"<Province({self.name})>"


class Municipio(Base):
    __tablename__ = "municipios"

    # Mapeamos 'id' de python a 'idmuni' de la BBDD
    id: Mapped[int] = mapped_column("idmuni", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("municipio", String(100), nullable=False)

    # La FK apunta a 'provincias.idprov'
    province_id: Mapped[int] = mapped_column("idprov", ForeignKey("provincias.idprov"))

    province: Mapped["Province"] = relationship("Province", back_populates="municipalities")

    def __repr__(self):
        return f"<Municipio({self.name})>"