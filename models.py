import re

class Libro:
    """
    Representa una obra literaria técnica o científica recuperada de la API de Open Library.
    """

    def __init__(self, datos_json: dict):
        """
        Inicializa un objeto Libro a partir de un diccionario JSON de la API.
        Realiza control y validación de datos de manera defensiva (no se almacena como libro si no cumple condiciones).
        """
        # Extraer el título
        self.titulo: str = datos_json.get("title", "Sin título").strip()

        # Extraer autores y convertirlos a un solo string delimitado por comas
        autores_lista = datos_json.get("author_name", [])
        if isinstance(autores_lista, list) and autores_lista:
            self.autores: str = ", ".join(autores_lista)
        else:
            self.autores: str = "Autor desconocido"

        # Extraer el año de primera publicación de manera segura (evitando nulos)
        anio_raw = datos_json.get("first_publish_year")
        try:
            self.anio: int = int(anio_raw) if anio_raw is not None else 0
        except (ValueError, TypeError):
            self.anio: int = 0

        # Extraer cantidad de ediciones registradas de manera segura
        ediciones_raw = datos_json.get("edition_count")
        try:
            self.cant_ediciones: int = int(ediciones_raw) if ediciones_raw is not None else 0
        except (ValueError, TypeError):
            self.cant_ediciones: int = 0

        # Extraer lista de idiomas (códigos de 3 letras de la biblioteca, ej: ['eng', 'spa'])
        self.idiomas: list[str] = datos_json.get("language", [])
        if not isinstance(self.idiomas, list):
            self.idiomas = []

        # Atributos de identificación y limpieza por expresiones regulares
        self.id_crudo: str = datos_json.get("key", "")
        self.id_limpio: str = self.limpiar_id_con_regex()

    def limpiar_id_con_regex(self) -> str:
        """
        Limpia y valida el id_crudo usando expresiones regulares.
        Espera un formato del tipo '/works/OLXXXXXW' o '/books/OLXXXXXM'.
        Devuelve únicamente el código limpio (ej.: 'OLXXXXXW').
        Si el formato es inválido o está vacío, lanza un ValueError.
        """
        if not self.id_crudo:
            raise ValueError("El ID crudo está vacío o no fue especificado.")
        patron = r"^/(?:works|books)/(OL\d+[A-Z])$"
        coincidencia = re.match(patron, self.id_crudo)

        if coincidencia:
            return coincidencia.group(1)
        else:
            raise ValueError(f"Formato de ID crudo inválido: '{self.id_crudo}'.")

    def tiene_idioma(self, codigo_idioma: str) -> bool:
        """
        Determina si el libro está disponible en el idioma con el código especificado.
        """
        # Limpieza simple para evitar problemas de mayúsculas/minúsculas y espacios
        codigo = codigo_idioma.strip().lower()
        return any(idioma.strip().lower() == codigo for idioma in self.idiomas)

    def __repr__(self) -> str:
        return f"Libro(id='{self.id_limpio}', titulo='{self.titulo[:30]}...', anio={self.anio}, ediciones={self.cant_ediciones})"
