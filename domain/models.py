class PetModel:
    def __init__(self, id_pet, nome, especie, raca, nome_dono, telefone_dono):
        self.id = id_pet
        self.nome = nome
        self.especie = especie
        self.raca = raca
        self.nome_dono = nome_dono
        self.telefone_dono = telefone_dono

class AtendimentoModel:
    def __init__(self, id_atendimento, pet_id, servico, data_atendimento, hora_atendimento, valor, status="Agendado"):
        self.id = id_atendimento
        self.pet_id = pet_id
        self.servico = servico
        self.data_atendimento = data_atendimento
        self.hora_atendimento = hora_atendimento
        self.valor = float(valor)
        self.status = status

class GastoModel:
    def __init__(self, id_gasto, descricao, valor, data_gasto):
        self.id = id_gasto
        self.descricao = descricao
        self.valor = float(valor)
        self.data_gasto = data_gasto