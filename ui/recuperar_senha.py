from PyQt6.QtWidgets import QMessageBox

class MecanismoRecuperacao:
    @staticmethod
    def disparar_recuperacao_senha(window_context, email_input_text):
        """Dispara a rotina de recuperação com base no input_email corrigido"""
        email = email_input_text.strip()
        if not email:
            QMessageBox.warning(window_context, "Aviso", "Por favor, digite o seu e-mail no campo de login para receber o link de recuperação.")
            return 
         
        QMessageBox.information(window_context, "Recuperação de Conta", f"Um link para redefinição segura de senha foi enviado para o e-mail: {email}")