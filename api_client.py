import abc
import aiohttp
import sys
from models import Libro

class ClienteApi(abc.ABC):
    """
    Clase abstracta base para clientes de API que recuperan información bibliográfica.
    """

    def __init__(self, url_base: str):
        self.url_base: str = url_base

    @abc.abstractmethod
    async def buscar_libros_async(self, tematica: str) -> list[Libro]:
        """
        Método abstracto asíncrono para buscar libros según una temática.
        """
        pass


class ClienteOpenLibrary(ClienteApi):
    """
    Cliente para consumir la API de búsqueda de Open Library de forma asíncrona.
    """

    def __init__(self, url_base: str = "https://openlibrary.org"):
        super().__init__(url_base)

    async def buscar_libros_async(self, tematica: str, limit: int = 100) -> list[Libro]:
        """
        Busca libros sobre una temática específica en Open Library.
        Realiza la consulta de forma asíncrona mediante aiohttp.
        Retorna una lista de objetos Libro validados.
        """
        url = f"{self.url_base}/search.json"
        
        # Parámetros para limitar los campos devueltos y optimizar el rendimiento.
        # Esto reduce drásticamente el tamaño del JSON de respuesta.
        params = {
            "q": tematica,
            "fields": "key,title,author_name,first_publish_year,edition_count,language",
            "limit": limit
        }

        # Configurar un User-Agent identificable según los términos de uso de Open Library.
        headers = {
            "User-Agent": "AnalizadorCriticoLiteratura/1.0 (contacto: openlibrary-app@example.com)"
        }

        libros_validados = []

        try:
            # Crear una sesión asíncrona temporal para la petición
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=15) as response:
                    if response.status != 200:
                        print(f"Error de API: Servidor respondió con estado {response.status}", file=sys.stderr)
                        return []

                    # Esperar la respuesta en formato JSON
                    datos_respuesta = await response.json()
                    documentos = datos_respuesta.get("docs", [])

                    for doc in documentos:
                        try:
                            # Instanciamos el objeto Libro. El constructor llamará internamente 
                            # a limpiar_id_con_regex(), que levantará ValueError si el ID es corrupto (no coincide con métricas).
                            libro = Libro(doc)
                            libros_validados.append(libro)
                        except ValueError as err_val:
                            # Capturar errores de validación de datos para libros específicos 
                            # y continuar procesando los demás sin detener el sistema.
                            # (Ej.: si el ID no sigue el patrón de Open Library).
                            print(f"[Validación Omitida] {err_val}", file=sys.stderr)
                            continue

        except aiohttp.ClientError as client_err:
            print(f"Error de conexión de red: {client_err}", file=sys.stderr)
        except Exception as e:
            print(f"Ocurrió un error inesperado al consumir la API: {e}", file=sys.stderr)

        return libros_validados
