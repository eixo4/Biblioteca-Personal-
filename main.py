import sqlite3
import os


class Biblioteca:
    def __init__(self, nombre_bd="biblioteca.db"):
        # Conectamos a la base de datos (se crea si no existe)
        self.conn = sqlite3.connect(nombre_bd)
        self.cursor = self.conn.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        sql = """
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            genero TEXT,
            estado TEXT CHECK(estado IN ('Leído', 'No leído'))
        )
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def agregar_libro(self, titulo, autor, genero, estado):
        try:
            sql = "INSERT INTO libros (titulo, autor, genero, estado) VALUES (?, ?, ?, ?)"
            self.cursor.execute(sql, (titulo, autor, genero, estado))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al agregar: {e}")
            return False

    def listar_libros(self):
        self.cursor.execute("SELECT * FROM libros")
        return self.cursor.fetchall()

    def buscar_libros(self, termino):
        sql = """
        SELECT * FROM libros 
        WHERE titulo LIKE ? OR autor LIKE ? OR genero LIKE ?
        """
        # Los signos % permiten buscar coincidencias parciales
        term = f"%{termino}%"
        self.cursor.execute(sql, (term, term, term))
        return self.cursor.fetchall()

    def actualizar_libro(self, id_libro, nuevo_titulo, nuevo_autor, nuevo_genero, nuevo_estado):
        try:
            sql = """
            UPDATE libros 
            SET titulo = ?, autor = ?, genero = ?, estado = ?
            WHERE id = ?
            """
            self.cursor.execute(sql, (nuevo_titulo, nuevo_autor, nuevo_genero, nuevo_estado, id_libro))
            self.conn.commit()
            return self.cursor.rowcount > 0  # Retorna True si se modificó algo
        except sqlite3.Error as e:
            print(f"Error al actualizar: {e}")
            return False

    def eliminar_libro(self, id_libro):
        try:
            sql = "DELETE FROM libros WHERE id = ?"
            self.cursor.execute(sql, (id_libro,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar: {e}")
            return False

    def cerrar(self):
        self.conn.close()

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_tabla(libros):
    if not libros:
        print("\n(No se encontraron libros)")
        return

    print("\n" + "=" * 85)
    print(f"{'ID':<5} | {'TÍTULO':<25} | {'AUTOR':<20} | {'GÉNERO':<15} | {'ESTADO':<10}")
    print("-" * 85)
    for libro in libros:
        print(f"{libro[0]:<5} | {libro[1]:<25} | {libro[2]:<20} | {libro[3]:<15} | {libro[4]:<10}")
    print("=" * 85 + "\n")


def menu_principal():
    biblioteca = Biblioteca()

    while True:
        print("\n--- 📚 GESTOR DE BIBLIOTECA PERSONAL ---")
        print("1. Agregar nuevo libro")
        print("2. Ver todos los libros")
        print("3. Buscar libro")
        print("4. Actualizar libro")
        print("5. Eliminar libro")
        print("6. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            print("\n--- Agregar Libro ---")
            titulo = input("Título: ")
            autor = input("Autor: ")
            genero = input("Género: ")

            # Validación simple del estado
            while True:
                estado_opt = input("¿Leído? (s/n): ").lower()
                if estado_opt in ['s', 'n']:
                    estado = "Leído" if estado_opt == 's' else "No leído"
                    break
                print("Por favor, ingrese 's' para sí o 'n' para no.")

            if biblioteca.agregar_libro(titulo, autor, genero, estado):
                print("✅ ¡Libro agregado correctamente!")

        elif opcion == '2':
            libros = biblioteca.listar_libros()
            mostrar_tabla(libros)

        elif opcion == '3':
            termino = input("\nIngrese término de búsqueda (título, autor o género): ")
            resultados = biblioteca.buscar_libros(termino)
            mostrar_tabla(resultados)

        elif opcion == '4':
            print("\n--- Actualizar Libro ---")
            # Primero mostramos los libros para que el usuario vea el ID
            mostrar_tabla(biblioteca.listar_libros())
            try:
                id_libro = int(input("Ingrese el ID del libro a modificar: "))

                # Pedimos nuevos datos
                print("(Deje vacío para mantener el valor actual)")
                n_titulo = input("Nuevo título: ")
                n_autor = input("Nuevo autor: ")
                n_genero = input("Nuevo género: ")
                n_estado_in = input("Nuevo estado (s/n, vacío para saltar): ").lower()

                # Buscamos el libro actual para rellenar vacíos
                cursor_temp = biblioteca.conn.cursor()
                cursor_temp.execute("SELECT * FROM libros WHERE id=?", (id_libro,))
                libro_actual = cursor_temp.fetchone()

                if libro_actual:
                    # Si el usuario dejó vacío, usamos el dato que ya existía
                    final_titulo = n_titulo if n_titulo else libro_actual[1]
                    final_autor = n_autor if n_autor else libro_actual[2]
                    final_genero = n_genero if n_genero else libro_actual[3]

                    if n_estado_in == 's':
                        final_estado = "Leído"
                    elif n_estado_in == 'n':
                        final_estado = "No leído"
                    else:
                        final_estado = libro_actual[4]

                    if biblioteca.actualizar_libro(id_libro, final_titulo, final_autor, final_genero, final_estado):
                        print("✅ ¡Libro actualizado!")
                    else:
                        print("❌ Error al actualizar.")
                else:
                    print("❌ ID no encontrado.")

            except ValueError:
                print("❌ El ID debe ser un número.")

        elif opcion == '5':
            print("\n--- Eliminar Libro ---")
            mostrar_tabla(biblioteca.listar_libros())
            try:
                id_libro = int(input("Ingrese el ID del libro a eliminar: "))
                confirmacion = input(f"¿Seguro que desea eliminar el libro {id_libro}? (s/n): ")

                if confirmacion.lower() == 's':
                    if biblioteca.eliminar_libro(id_libro):
                        print("✅ Libro eliminado.")
                    else:
                        print("❌ No se encontró ese ID.")
                else:
                    print("Operación cancelada.")
            except ValueError:
                print("❌ El ID debe ser un número.")

        elif opcion == '6':
            print("¡Hasta luego!")
            biblioteca.cerrar()
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu_principal()