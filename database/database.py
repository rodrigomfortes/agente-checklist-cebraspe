from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from contextlib import contextmanager
from typing import Optional
from .models import Base, ChecklistDia1, ChecklistDia2

# Configuração do banco de dados
# Nota: Alguns warnings de tipo são normais com SQLAlchemy 2.0
DATABASE_URL = "sqlite:///./database/checklist_cebraspe.db"

# Criar diretório se não existir
os.makedirs(os.path.dirname("database/checklist_cebraspe.db"), exist_ok=True)

# Engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necessário para SQLite
    echo=False  # Mude para True se quiser ver os SQL logs
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def init_database():
    """
    Inicializa o banco de dados criando todas as tabelas
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

def get_db_session() -> Session:
    """
    Retorna uma sessão do banco de dados
    """
    return SessionLocal()

@contextmanager
def get_db():
    """
    Context manager para gerenciar sessões do banco de dados
    Uso: 
        with get_db() as db:
            # operações no banco
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

class ChecklistDatabase:
    """
    Classe para operações específicas do checklist
    """
    
    @staticmethod
    def criar_checklist_dia1(sessao_id: str, aplicador_nome: Optional[str] = None, local_aplicacao: Optional[str] = None):
        """
        Cria checklist com todos os campos _presente iniciados como False
        """
        with get_db() as db:
            checklist = ChecklistDia1(
                sessao_id=sessao_id,
                aplicador_nome=aplicador_nome,
                local_aplicacao=local_aplicacao,
                status_checklist='iniciado'
            )

            # Inicializa todos os campos _presente como False
            for coluna in ChecklistDia1.__table__.columns:
                if "_presente" in coluna.name:
                    setattr(checklist, coluna.name, False)

            db.add(checklist)
            db.commit()
            db.refresh(checklist)
            return checklist.id

    
    @staticmethod
    def criar_checklist_dia2(sessao_id: str, aplicador_nome: Optional[str] = None, local_aplicacao: Optional[str] = None):
        """
        Cria checklist com todos os campos _presente iniciados como False
        """
        with get_db() as db:
            checklist = ChecklistDia2(
                sessao_id=sessao_id,
                aplicador_nome=aplicador_nome,
                local_aplicacao=local_aplicacao,
                status_checklist='iniciado'
            )

            # Inicializa todos os campos _presente como False
            for coluna in ChecklistDia2.__table__.columns:
                if "_presente" in coluna.name:
                    setattr(checklist, coluna.name, False)

            db.add(checklist)
            db.commit()
            db.refresh(checklist)
            return checklist.id

    @staticmethod
    def atualizar_item_dia1(sessao_id: str, campo: str, presente: Optional[bool] = None, foto: Optional[str] = None, observacao: Optional[str] = None):
        """
        Atualiza um item específico do checklist dia 1
        """
        with get_db() as db:
            checklist = db.query(ChecklistDia1).filter(ChecklistDia1.sessao_id == sessao_id).first()
            if not checklist:
                raise ValueError(f"Checklist não encontrado para sessão {sessao_id}")
            
            # Atualiza os campos correspondentes
            if presente is not None:
                setattr(checklist, f"{campo}_presente", presente)
            if foto is not None:
                setattr(checklist, f"{campo}_foto", foto)
            if observacao is not None:
                setattr(checklist, f"{campo}_observacao", observacao)
            
            db.commit()
            return checklist
    
    @staticmethod
    def atualizar_item_dia2(sessao_id: str, campo: str, presente: Optional[bool] = None, foto: Optional[str] = None, observacao: Optional[str] = None):
        """
        Atualiza um item específico do checklist dia 2
        """
        with get_db() as db:
            checklist = db.query(ChecklistDia2).filter(ChecklistDia2.sessao_id == sessao_id).first()
            if not checklist:
                raise ValueError(f"Checklist não encontrado para sessão {sessao_id}")
            
            # Atualiza os campos correspondentes
            if presente is not None:
                setattr(checklist, f"{campo}_presente", presente)
            if foto is not None:
                setattr(checklist, f"{campo}_foto", foto)
            if observacao is not None:
                setattr(checklist, f"{campo}_observacao", observacao)
            
            db.commit()
            return checklist
    
    @staticmethod
    def buscar_checklist_dia1(sessao_id: str):
        """
        Busca um checklist do dia 1 por sessão e retorna todos os campos, inclusive os itens
        """
        with get_db() as db:
            checklist = db.query(ChecklistDia1).filter(ChecklistDia1.sessao_id == sessao_id).first()
            if checklist:
                resultado = {}
                for coluna in ChecklistDia1.__table__.columns:
                    resultado[coluna.name] = getattr(checklist, coluna.name)
                return resultado
            return None

    
    @staticmethod
    def buscar_checklist_dia2(sessao_id: str):
        with get_db() as db:
            checklist = db.query(ChecklistDia2).filter(ChecklistDia2.sessao_id == sessao_id).first()
            if checklist:
                resultado = {}
                for coluna in ChecklistDia2.__table__.columns:
                    resultado[coluna.name] = getattr(checklist, coluna.name)
                return resultado
            return None

    
    @staticmethod
    def finalizar_checklist_dia1(sessao_id: str):
        """
        Marca o checklist do dia 1 como concluído
        """
        with get_db() as db:
            checklist = db.query(ChecklistDia1).filter(ChecklistDia1.sessao_id == sessao_id).first()
            if checklist:
                setattr(checklist, 'status_checklist', 'concluido')
                from sqlalchemy.sql import func
                setattr(checklist, 'timestamp_fim', func.now())
                db.commit()
                return checklist
            return None
    
    @staticmethod
    def finalizar_checklist_dia2(sessao_id: str):
        """
        Marca o checklist do dia 2 como concluído
        """
        with get_db() as db:
            checklist = db.query(ChecklistDia2).filter(ChecklistDia2.sessao_id == sessao_id).first()
            if checklist:
                setattr(checklist, 'status_checklist', 'concluido')
                from sqlalchemy.sql import func
                setattr(checklist, 'timestamp_fim', func.now())
                db.commit()
                return checklist
            return None

    @staticmethod
    def listar_faltantes(sessao_id: str) -> list:
        """
        Retorna uma lista dos campos que ainda estão como não preenchidos (presente=False) no checklist dia 1
        """
        with get_db() as db:
            checklist = db.query(ChecklistDia1).filter(ChecklistDia1.sessao_id == sessao_id).first()
            if not checklist:
                return []

            faltantes = []
            for coluna in ChecklistDia1.__table__.columns:
                if "_presente" in coluna.name:
                    if getattr(checklist, coluna.name) is False:
                        campo = coluna.name.replace("_presente", "")
                        faltantes.append(campo)
            return faltantes

    @staticmethod
    def resetar_checklist(sessao_id: str):
        """
        Reseta todos os campos _presente para False no checklist do dia 1
        """
        with get_db() as db:
            checklist = db.query(ChecklistDia1).filter(ChecklistDia1.sessao_id == sessao_id).first()
            if checklist:
                for coluna in ChecklistDia1.__table__.columns:
                    if "_presente" in coluna.name:
                        setattr(checklist, coluna.name, False)
                db.commit()

    @staticmethod
    def resetar_checklist_dia2(sessao_id: str):
        """
        Reseta todos os campos _presente para False no checklist do dia 2
        """
        with get_db() as db:
            checklist = db.query(ChecklistDia2).filter(ChecklistDia2.sessao_id == sessao_id).first()
            if checklist:
                for coluna in ChecklistDia2.__table__.columns:
                    if "_presente" in coluna.name:
                        setattr(checklist, coluna.name, False)
                setattr(checklist, 'status_checklist', 'iniciado')
                db.commit()
