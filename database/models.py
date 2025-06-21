from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ChecklistDia1(Base):
    __tablename__ = 'checklist_dia1'
    
    # Identificação
    id = Column(Integer, primary_key=True, autoincrement=True)
    sessao_id = Column(String(100), nullable=False, unique=True)  # ID único da sessão de checklist
    aplicador_nome = Column(String(255))
    local_aplicacao = Column(String(255))
    data_aplicacao = Column(DateTime, default=func.now())
    timestamp_inicio = Column(DateTime, default=func.now())
    timestamp_fim = Column(DateTime)
    status_checklist = Column(String(50), default='iniciado')  # iniciado, em_progresso, concluido
    
    # === ENVELOPES DE MATERIAL DE SALA - DIA 1 ===
    # Envelope - 1º dia de aplicação (sala)
    envelope_sala_dia1_presente = Column(Boolean)
    envelope_sala_dia1_foto = Column(Text)  # Path da foto
    envelope_sala_dia1_observacao = Column(Text)
    
    # Lista de presença do 1º dia
    lista_presenca_dia1_presente = Column(Boolean)
    lista_presenca_dia1_foto = Column(Text)
    lista_presenca_dia1_observacao = Column(Text)
    
    # Ata de sala do 1º dia
    ata_sala_dia1_presente = Column(Boolean)
    ata_sala_dia1_foto = Column(Text)
    ata_sala_dia1_observacao = Column(Text)
    
    # Avaliação de atendimento especializado
    avaliacao_especializada_dia1_presente = Column(Boolean)
    avaliacao_especializada_dia1_foto = Column(Text)
    avaliacao_especializada_dia1_observacao = Column(Text)
    
    # === ENVELOPES DE COORDENAÇÃO - DIA 1 ===
    # Envelope - 1º dia de aplicação (coordenação)
    envelope_coordenacao_dia1_presente = Column(Boolean)
    envelope_coordenacao_dia1_foto = Column(Text)
    envelope_coordenacao_dia1_observacao = Column(Text)
    
    # Cartão-resposta reserva
    cartao_resposta_reserva_dia1_presente = Column(Boolean)
    cartao_resposta_reserva_dia1_foto = Column(Text)
    cartao_resposta_reserva_dia1_observacao = Column(Text)
    
    # Ata de sala reserva (coordenação)
    ata_sala_reserva_dia1_presente = Column(Boolean)
    ata_sala_reserva_dia1_foto = Column(Text)
    ata_sala_reserva_dia1_observacao = Column(Text)
    
    # Lista de presença reserva (coordenação)
    lista_presenca_reserva_dia1_presente = Column(Boolean)
    lista_presenca_reserva_dia1_foto = Column(Text)
    lista_presenca_reserva_dia1_observacao = Column(Text)
    
    # Avaliação especializada reserva (coordenação)
    avaliacao_especializada_reserva_dia1_presente = Column(Boolean)
    avaliacao_especializada_reserva_dia1_foto = Column(Text)
    avaliacao_especializada_reserva_dia1_observacao = Column(Text)
    
    # === ENVELOPES AUXILIARES - DIA 1 ===
    # Envelope de porta-objetos - 1º dia
    envelope_porta_objetos_dia1_presente = Column(Boolean)
    envelope_porta_objetos_dia1_foto = Column(Text)
    envelope_porta_objetos_dia1_observacao = Column(Text)
    
    # Envelope de Sala Extra - 1º dia
    envelope_sala_extra_dia1_presente = Column(Boolean)
    envelope_sala_extra_dia1_foto = Column(Text)
    envelope_sala_extra_dia1_observacao = Column(Text)
    
    # === ENVELOPE TRANSPARENTE ===
    # Manuais
    manuais_presente = Column(Boolean)
    manuais_foto = Column(Text)
    manuais_observacao = Column(Text)
    
    # Crachás
    crachas_presente = Column(Boolean)
    crachas_foto = Column(Text)
    crachas_observacao = Column(Text)
    
    # Relação de candidatos e salas
    relacao_candidatos_salas_presente = Column(Boolean)
    relacao_candidatos_salas_foto = Column(Text)
    relacao_candidatos_salas_observacao = Column(Text)
    
    # === ITENS DE USO GERAL ===
    # Alicate
    alicate_presente = Column(Boolean)
    alicate_foto = Column(Text)
    alicate_observacao = Column(Text)
    
    # 3 canetas esferográficas
    canetas_presente = Column(Boolean)
    canetas_foto = Column(Text)
    canetas_observacao = Column(Text)
    
    # 2 pincéis
    pinceis_presente = Column(Boolean)
    pinceis_foto = Column(Text)
    pinceis_observacao = Column(Text)
    
    # 1 fita adesiva
    fita_adesiva_presente = Column(Boolean)
    fita_adesiva_foto = Column(Text)
    fita_adesiva_observacao = Column(Text)
    
    def __repr__(self):
        return f"<ChecklistDia1(sessao_id='{self.sessao_id}', aplicador='{self.aplicador_nome}', status='{self.status_checklist}')>"


class ChecklistDia2(Base):
    __tablename__ = 'checklist_dia2'
    
    # Identificação
    id = Column(Integer, primary_key=True, autoincrement=True)
    sessao_id = Column(String(100), nullable=False, unique=True)  # ID único da sessão de checklist
    aplicador_nome = Column(String(255))
    local_aplicacao = Column(String(255))
    data_aplicacao = Column(DateTime, default=func.now())
    timestamp_inicio = Column(DateTime, default=func.now())
    timestamp_fim = Column(DateTime)
    status_checklist = Column(String(50), default='iniciado')  # iniciado, em_progresso, concluido
    
    # === ENVELOPES DE MATERIAL DE SALA - DIA 2 ===
    # Envelope - 2º dia de aplicação (sala)
    envelope_sala_dia2_presente = Column(Boolean)
    envelope_sala_dia2_foto = Column(Text)
    envelope_sala_dia2_observacao = Column(Text)
    
    # Lista de presença do 2º dia
    lista_presenca_dia2_presente = Column(Boolean)
    lista_presenca_dia2_foto = Column(Text)
    lista_presenca_dia2_observacao = Column(Text)
    
    # Ata de sala do 2º dia
    ata_sala_dia2_presente = Column(Boolean)
    ata_sala_dia2_foto = Column(Text)
    ata_sala_dia2_observacao = Column(Text)
    
    # Avaliação de atendimento especializado
    avaliacao_especializada_dia2_presente = Column(Boolean)
    avaliacao_especializada_dia2_foto = Column(Text)
    avaliacao_especializada_dia2_observacao = Column(Text)
    
    # === ENVELOPES DE COORDENAÇÃO - DIA 2 ===
    # Envelope - 2º dia de aplicação (coordenação)
    envelope_coordenacao_dia2_presente = Column(Boolean)
    envelope_coordenacao_dia2_foto = Column(Text)
    envelope_coordenacao_dia2_observacao = Column(Text)
    
    # Cartão-resposta reserva
    cartao_resposta_reserva_dia2_presente = Column(Boolean)
    cartao_resposta_reserva_dia2_foto = Column(Text)
    cartao_resposta_reserva_dia2_observacao = Column(Text)
    
    # Ata de sala reserva (coordenação)
    ata_sala_reserva_dia2_presente = Column(Boolean)
    ata_sala_reserva_dia2_foto = Column(Text)
    ata_sala_reserva_dia2_observacao = Column(Text)
    
    # Lista de presença reserva (coordenação)
    lista_presenca_reserva_dia2_presente = Column(Boolean)
    lista_presenca_reserva_dia2_foto = Column(Text)
    lista_presenca_reserva_dia2_observacao = Column(Text)
    
    # Avaliação especializada reserva (coordenação)
    avaliacao_especializada_reserva_dia2_presente = Column(Boolean)
    avaliacao_especializada_reserva_dia2_foto = Column(Text)
    avaliacao_especializada_reserva_dia2_observacao = Column(Text)
    
    # Folha de rascunho reserva
    folha_rascunho_reserva_presente = Column(Boolean)
    folha_rascunho_reserva_foto = Column(Text)
    folha_rascunho_reserva_observacao = Column(Text)
    
    # === ENVELOPES AUXILIARES - DIA 2 ===
    # Envelope de porta-objetos - 2º dia
    envelope_porta_objetos_dia2_presente = Column(Boolean)
    envelope_porta_objetos_dia2_foto = Column(Text)
    envelope_porta_objetos_dia2_observacao = Column(Text)
    
    # Envelope de Sala Extra - 2º dia
    envelope_sala_extra_dia2_presente = Column(Boolean)
    envelope_sala_extra_dia2_foto = Column(Text)
    envelope_sala_extra_dia2_observacao = Column(Text)
    
    # Envelope de folhas de rascunho por sala
    envelope_folhas_rascunho_presente = Column(Boolean)
    envelope_folhas_rascunho_foto = Column(Text)
    envelope_folhas_rascunho_observacao = Column(Text)
    
    # === ENVELOPE TRANSPARENTE ===
    # Manuais
    manuais_presente = Column(Boolean)
    manuais_foto = Column(Text)
    manuais_observacao = Column(Text)
    
    # Crachás
    crachas_presente = Column(Boolean)
    crachas_foto = Column(Text)
    crachas_observacao = Column(Text)
    
    # Relação de candidatos e salas
    relacao_candidatos_salas_presente = Column(Boolean)
    relacao_candidatos_salas_foto = Column(Text)
    relacao_candidatos_salas_observacao = Column(Text)
    
    # === ITENS DE USO GERAL ===
    # Alicate
    alicate_presente = Column(Boolean)
    alicate_foto = Column(Text)
    alicate_observacao = Column(Text)
    
    # 3 canetas esferográficas
    canetas_presente = Column(Boolean)
    canetas_foto = Column(Text)
    canetas_observacao = Column(Text)
    
    # 2 pincéis
    pinceis_presente = Column(Boolean)
    pinceis_foto = Column(Text)
    pinceis_observacao = Column(Text)
    
    # 1 fita adesiva
    fita_adesiva_presente = Column(Boolean)
    fita_adesiva_foto = Column(Text)
    fita_adesiva_observacao = Column(Text)
    
    def __repr__(self):
        return f"<ChecklistDia2(sessao_id='{self.sessao_id}', aplicador='{self.aplicador_nome}', status='{self.status_checklist}')>" 