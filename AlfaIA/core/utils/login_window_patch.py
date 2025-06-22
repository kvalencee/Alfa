# =============================================================================
# AlfaIA/core/utils/login_window_patch.py - Parche para corregir login_window.py
# =============================================================================

"""
Este archivo contiene las correcciones necesarias para login_window.py
Aplicar estos cambios manualmente al archivo original.
"""

# REEMPLAZAR la clase AuthWorker en login_window.py con esta versión:

AUTHWORKER_REPLACEMENT = '''
class AuthWorker(QThread):
    """Worker thread para operaciones de autenticación - CORREGIDO"""
    auth_completed = pyqtSignal(bool, str, object)  # Agregamos object para pasar el usuario

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Ejecutar operación de autenticación - VERSIÓN CORREGIDA"""
        try:
            from core.auth.authentication import auth_manager

            print(f"🔧 AuthWorker ejecutando operación: {self.operation}")

            if self.operation == "login":
                success, message = auth_manager.login(
                    self.kwargs['email'],
                    self.kwargs['password']
                )

                # Si el login fue exitoso, obtener el usuario inmediatamente
                user = None
                if success:
                    print("✅ Login exitoso en AuthWorker, obteniendo usuario...")
                    user = auth_manager.get_current_user()
                    if user:
                        print(f"✅ Usuario obtenido en AuthWorker: {user.email}")
                    else:
                        print("⚠️ Usuario no obtenido inmediatamente, pero login exitoso")

                self.auth_completed.emit(success, message, user)

            elif self.operation == "register":
                success, message = auth_manager.register_user(**self.kwargs)
                self.auth_completed.emit(success, message, None)
            else:
                self.auth_completed.emit(False, "Operación no válida", None)

        except Exception as e:
            print(f"❌ Error en AuthWorker: {e}")
            import traceback
            traceback.print_exc()
            self.auth_completed.emit(False, f"Error: {str(e)}", None)
'''

# REEMPLAZAR el método on_login_completed en LoginForm con esta versión:

ON_LOGIN_COMPLETED_REPLACEMENT = '''
    def on_login_completed(self, success: bool, message: str, user=None):
        """Resultado del login con mejor UX - VERSIÓN CORREGIDA"""
        print(f"🎯 Login completado: success={success}, message={message}, user={'Sí' if user else 'No'}")

        self.set_loading_state(False)

        if success:
            # Mostrar brevemente éxito antes de continuar
            self.login_button.setText("¡Éxito!")
            self.login_button.setStyleSheet(self.login_button.styleSheet().replace(
                self.settings.COLORS['blue_educational'], self.settings.COLORS['green_success']
            ))

            # Pequeño delay para mostrar el éxito y luego emitir señal
            print("✅ Login exitoso, emitiendo señal en 500ms...")
            QTimer.singleShot(500, self.login_success.emit)
        else:
            print(f"❌ Login falló: {message}")
            QMessageBox.warning(self, "Error de inicio de sesión", message)
            self.password_input.clear()
            self.password_input.setFocus()
'''

print("📝 Parche de login_window.py creado")
print("🔧 Aplicar manualmente estos cambios al archivo login_window.py:")
print("1. Reemplazar la clase AuthWorker")
print("2. Reemplazar el método on_login_completed en LoginForm")
print("3. Cambiar la línea de conexión de auth_completed para incluir 3 parámetros")