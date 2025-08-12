# generate_hashes.py (MODIFICADO para hashing sin salt)
#import hashlib
#
#def _generar_hash_contrasena(contrasena_texto_plano):
#    """Genera el hash SHA256 de una contraseña en texto plano."""
#    return hashlib.sha256(contrasena_texto_plano.encode()).hexdigest()
#lol
#print("--- Generando credenciales para usuarios (SIN SALT) ---")
#
## Para usuario1
#username1 = "usuario1"
#password1 = "pass123"
#hash1 = _generar_hash_contrasena(password1)
#print(f"\nUsuario: {username1}")
#print(f"  Contraseña: {password1}")
#print(f"  Hash: {hash1}")
#
## Para admin
#username_admin = "admin"
#password_admin = "adminpass"
#hash_admin = _generar_hash_contrasena(password_admin)
#print(f"\nUsuario: {username_admin}")
#print(f"  Contraseña: {password_admin}")
#print(f"  Hash: {hash_admin}")
#
#print("\n--- Copia estos valores en tu data/users.json, eliminando las líneas de 'salt' ---")
