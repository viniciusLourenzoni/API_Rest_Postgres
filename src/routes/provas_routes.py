from sqlmodel import select
from fastapi import APIRouter, HTTPException
from psycopg2 import IntegrityError
from src.models.resultados_model import Resultados
from src.models.provas_model import Provas
from src.config.database import get_session

provas_router = APIRouter(prefix="/provas")

@provas_router.post("")
def cria_prova(prova: Provas):
    with get_session() as session:
        existe_prova = session.query(Provas).filter(
            Provas.descricao == prova.descricao, Provas.data_prova == prova.data_prova).first()
        if existe_prova:
            raise HTTPException(status_code=400, detail="Prova já cadastrada.")
        try:
            session.add(prova)
            session.commit()
            session.refresh(prova)
            return prova
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=400, detail="Erro ao cadastrar prova.")


@provas_router.delete("/{prova_id}")
def excluir_prova(prova_id: int):
    with get_session() as session:
        
        if session.exec(select(Resultados).where(Resultados.prova_id == prova_id)).first():
            raise HTTPException(
                status_code=400, detail="Não é possível excluir a prova com resultados associados.")

        prova = session.exec(select(Provas).where(
            Provas.id == prova_id)).first()
        if not prova:
            raise HTTPException(
                status_code=404, detail="Prova não encontrada.")

        session.delete(prova)
        session.commit()

        return {"message": "Prova excluída com sucesso."}
