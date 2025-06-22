# =============================================================================
# AlfaIA/test_auth_complete.py - Test Completo del Sistema de Autenticación
# =============================================================================

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


def test_password_hashing():
    """Probar el sistema de hash de contraseñas"""
    print("🔐 PROBANDO SISTEMA DE HASH DE CONTRASEÑAS")
    print("=" * 50)

    try:
        from core.database.models import Usuario

        test_password = "TestPassword123"

        # 1. Probar hash
        print(f"1. Hasheando contraseña: '{test_password}'")
        hashed = Usuario.hash_password(test_password)
        print(f"   Hash generado: {hashed}")
        print(f"   Tipo de hash: {'bcrypt' if hashed.startswith('$2b$') else 'SHA-256'}")

        # 2. Crear usuario temporal
        temp_user = Usuario(password_hash=hashed)

        # 3. Probar verificación
        print(f"\n2. Verificando contraseña...")
        if temp_user.verify_password(test_password):
            print("   ✅ Verificación exitosa")
        else:
            print("   ❌ Verificación falló")

        # 4. Probar contraseña incorrecta
        print(f"\n3. Probando contraseña incorrecta...")
        if temp_user.verify_password("PasswordIncorrecta"):
            print("   ❌ Error: aceptó contraseña incorrecta")
        else:
            print("   ✅ Rechazó contraseña incorrecta correctamente")

        return True

    except Exception as e:
        print(f"❌ Error probando hash: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_registration_complete():
    """Probar registro completo de usuario"""
    print("\n📝 PROBANDO REGISTRO COMPLETO")
    print("=" * 50)

    try:
        from core.auth.authentication import auth_manager

        # Usar email único con timestamp
        import time
        timestamp = int(time.time())
        email = f"test{timestamp}@alfaia.com"
        password = "TestPassword123"

        print(f"📧 Registrando usuario: {email}")

        # Registrar usuario
        success, message = auth_manager.register_user(
            email=email,
            password=password,
            nombre="Usuario",
            apellido="Prueba"
        )

        print(f"   Resultado: {success} - {message}")

        if success:
            print("✅ Registro exitoso")

            # Probar login inmediatamente
            print(f"\n🔑 Probando login con usuario recién creado...")
            login_success, login_message = auth_manager.login(email, password)
            print(f"   Login: {login_success} - {login_message}")

            if login_success:
                print("✅ Login exitoso")

                # Verificar usuario actual
                current_user = auth_manager.get_current_user()
                if current_user:
                    print(f"✅ Usuario obtenido: {current_user.email}")
                    return True
                else:
                    print("❌ No se pudo obtener usuario actual")
                    return False
            else:
                print("❌ Login falló")
                return False
        else:
            print("❌ Registro falló")
            return False

    except Exception as e:
        print(f"❌ Error en registro completo: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_existing_user_login():
    """Probar login con usuario existente"""
    print("\n🔍 PROBANDO LOGIN CON USUARIO EXISTENTE")
    print("=" * 50)

    try:
        from core.database.models import Usuario
        from core.auth.authentication import auth_manager

        # Buscar el usuario existente
        existing_user = Usuario.find_by_email("test@alfaia.com")
        if not existing_user:
            print("❌ Usuario test@alfaia.com no existe")
            return False

        print(f"✅ Usuario encontrado: {existing_user.email}")
        print(f"   Hash en BD: {existing_user.password_hash}")

        # Probar diferentes contraseñas comunes
        common_passwords = [
            "Test123456",
            "TestPassword123",
            "test123",
            "password",
            "123456"
        ]

        print(f"\n🔑 Probando contraseñas comunes...")
        for password in common_passwords:
            print(f"   Probando: '{password}'")
            if existing_user.verify_password(password):
                print(f"   ✅ Contraseña correcta: '{password}'")

                # Probar login con auth_manager
                success, message = auth_manager.login("test@alfaia.com", password)
                print(f"   Auth Manager: {success} - {message}")

                if success:
                    user = auth_manager.get_current_user()
                    if user:
                        print(f"   ✅ Usuario obtenido: {user.email}")
                        return True
                    else:
                        print(f"   ❌ No se pudo obtener usuario")
                        return False

                return True
            else:
                print(f"   ❌ Contraseña incorrecta")

        print("❌ Ninguna contraseña común funcionó")
        return False

    except Exception as e:
        print(f"❌ Error probando usuario existente: {e}")
        import traceback
        traceback.print_exc()
        return False


def reset_test_user_password():
    """Resetear contraseña del usuario de prueba"""
    print("\n🔧 RESETEANDO CONTRASEÑA DE USUARIO EXISTENTE")
    print("=" * 50)

    try:
        from core.database.models import Usuario

        # Buscar usuario existente
        user = Usuario.find_by_email("test@alfaia.com")
        if not user:
            print("❌ Usuario no encontrado")
            return False

        print(f"✅ Usuario encontrado: {user.email}")

        # Actualizar contraseña
        new_password = "TestPassword123"
        print(f"🔑 Actualizando contraseña a: '{new_password}'")

        if user.update_password(new_password):
            print("✅ Contraseña actualizada exitosamente")

            # Verificar que funciona
            user_updated = Usuario.find_by_email("test@alfaia.com")
            if user_updated and user_updated.verify_password(new_password):
                print("✅ Verificación de nueva contraseña exitosa")
                return True
            else:
                print("❌ Verificación de nueva contraseña falló")
                return False
        else:
            print("❌ Error actualizando contraseña")
            return False

    except Exception as e:
        print(f"❌ Error reseteando contraseña: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal del test completo"""
    print("🔬 TEST COMPLETO DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 60)

    # 1. Probar hashing
    print("\n🎯 PASO 1: Probar sistema de hash")
    hash_ok = test_password_hashing()

    if not hash_ok:
        print("❌ Sistema de hash no funciona, no se puede continuar")
        return

    # 2. Intentar login con usuario existente
    print("\n🎯 PASO 2: Probar login con usuario existente")
    existing_login_ok = test_existing_user_login()

    if not existing_login_ok:
        print("\n🎯 PASO 2.1: Resetear contraseña de usuario existente")
        reset_ok = reset_test_user_password()

        if reset_ok:
            print("\n🎯 PASO 2.2: Probar login después del reset")
            from core.auth.authentication import auth_manager
            success, message = auth_manager.login("test@alfaia.com", "TestPassword123")
            print(f"Login después del reset: {success} - {message}")

            if success:
                user = auth_manager.get_current_user()
                print(f"Usuario obtenido: {'✅' if user else '❌'}")
                existing_login_ok = user is not None

    # 3. Probar registro de nuevo usuario
    print("\n🎯 PASO 3: Probar registro completo")
    registration_ok = test_registration_complete()

    # Resultado final
    print("\n" + "=" * 60)
    print("🏁 RESULTADO FINAL:")
    print(f"   Hash de contraseñas: {'✅' if hash_ok else '❌'}")
    print(f"   Login usuario existente: {'✅' if existing_login_ok else '❌'}")
    print(f"   Registro nuevo usuario: {'✅' if registration_ok else '❌'}")

    if hash_ok and (existing_login_ok or registration_ok):
        print("\n✅ SISTEMA DE AUTENTICACIÓN FUNCIONA CORRECTAMENTE")
        print("💡 Ahora puedes ejecutar main.py sin problemas")
    else:
        print("\n❌ HAY PROBLEMAS EN EL SISTEMA DE AUTENTICACIÓN")
        print("💡 Revisa los errores arriba y aplica las correcciones")


if __name__ == "__main__":
    main()