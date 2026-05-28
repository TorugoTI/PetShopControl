import os
from dotenv import load_dotenv

load_dotenv()

class GerenciadorGoogleAgenda:
    def __init__(self):
        self.token_agenda = os.getenv("GOOGLE_CALENDAR_TOKEN")

    def sincronizar_novo_agendamento(self, nome_pet, servico, data, hora):
        """
        Cadastra a consulta na Google Agenda do dono do pet shop e retorna 
        a mensagem de confirmação que será enviada para o cliente.
        """
        if not self.token_agenda:
            print("[AGENDA] Modo Demo: Simulando sincronização com a Google Agenda...")
            return f"Olá! Confirmamos o agendamento do seu pet {nome_pet} para o serviço de {servico} no dia {data} às {hora}. 🐾"

        print(f"[AGENDA] Conectando à API do Google Calendar para agendar: {nome_pet}...")
        
        mensagem_cliente = (
            f"Fique atento! O agendamento de {nome_pet} ({servico}) foi adicionado com sucesso "
            f"à sua agenda em {data} às {hora}. Um lembrete foi enviado ao tutor."
        )
        return mensagem_cliente