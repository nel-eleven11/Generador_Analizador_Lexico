# Diseño de Lenaguajes de Programación
"""
Autores:
    Nelson García Bravatti
    Joaquín Puente
    Ricardo Chuy
Archivo:
    Este archivo se encarga de leer los archivos YALex para luego crear un archivo json con las expresiones regulares.

"""
class readYalex:

    def __init__(self, yalex_file):
        self.yalex_file = yalex_file
        self.tamanio_buffer = 10
        self.inicio = 0
        self.avance = 10

    def read_file(self):
        with open(self.yalex_file, "r", encoding="utf-8") as f:
            return list(f.read())

    def cargar_buffer(self, entrada):
        buffer = entrada[self.inicio:self.inicio + self.tamanio_buffer]
        if len(buffer) < self.tamanio_buffer:
            buffer.append("eof")  # Agrega eof si el buffer es más pequeño de lo esperado
        return buffer

    def read_and_print(self):
        """Lee el archivo y muestra su contenido en bloques de tamaño buffer."""
        entrada = self.read_file()
        while self.inicio < len(entrada):
            buffer = self.cargar_buffer(entrada)
            print("".join(buffer))  # Imprime el contenido del buffer como string
            self.inicio += self.avance  # Avanza en el archivo
