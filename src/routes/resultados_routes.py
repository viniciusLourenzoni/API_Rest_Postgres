from fastapi import APIRouter, HTTPException
from sqlmodel import select
from src.config.database import get_session
from src.models.provas_model import Provas
from src.models.resultados_model import Resultados

resultados_router = APIRouter(prefix="/resultados")

@resultados_router.post("")
def cria_resultado(resultado: Resultados):
    with get_session() as session:
        
        statement = select(Provas).where(Provas.id == resultado.prova_id)
        prova = session.exec(statement).first()
        if not prova:
            raise HTTPException(
                status_code=404, detail="Prova não cadastrada.")
        
        respostas_corretas = [prova.q1, prova.q2, prova.q3, prova.q4,
                              prova.q5, prova.q6, prova.q7, prova.q8, prova.q9, prova.q10]
        respostas_aluno = [resultado.q1, resultado.q2, resultado.q3, resultado.q4,
                           resultado.q5, resultado.q6, resultado.q7, resultado.q8, resultado.q9, resultado.q10]

        nota = 0
        for resposta_correta, resposta_aluno in zip(respostas_corretas, respostas_aluno):
            if resposta_correta == resposta_aluno:
                nota += 1

        resultado.nota = nota

        session.add(resultado)
        session.commit()
        session.refresh(resultado)
        return resultado
    

@resultados_router.get("/{prova_id}")
def obter_resultados_prova(prova_id: int):
    with get_session() as session:
        
        prova = session.exec(select(Provas).where(
            Provas.id == prova_id)).first()
        if not prova:
            raise HTTPException(
                status_code=404, detail="Prova não encontrada.")
            
        resultados_alunos = session.exec(
            select(Resultados).where(Resultados.prova_id == prova_id)).all()

        dados_resposta = {
            "descricao": prova.descricao,
            "data_prova": prova.data_prova,
            "alunos": [
                {
                    "nome": resultado.nome,
                    "nota": resultado.nota,
                    "resultado_final": "aprovado" if resultado.nota >= 7 else "recuperação" if resultado.nota >= 5 else "reprovado"
                }
                for resultado in resultados_alunos
            ]
        }

        return dados_resposta
    
    
@resultados_router.patch("/{resultado_id}")
def atualizar_resposta(resultado_id: int, respostas: Resultados):
    with get_session() as session:
        resultado = session.exec(select(Resultados).where(
            Resultados.id == resultado_id)).first()
        if not resultado:
            raise HTTPException(
                status_code=404, detail="Resultado não encontrado.")

        prova = session.exec(select(Provas).where(
            Provas.id == resultado.prova_id)).first()

        for num in range(1, 11):
            setattr(resultado, f"q{num}", getattr(respostas, f"q{num}"))

        nota = sum(getattr(prova, f"q{num}") == getattr(
            resultado, f"q{num}") for num in range(1, 11))
        resultado.nota = nota

        session.commit()
        session.refresh(resultado)

        return resultado
