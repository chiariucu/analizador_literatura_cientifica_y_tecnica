import os
import unittest
from unittest.mock import patch, AsyncMock
from models import Libro
from analyzer import AnalizadorBiblioteca
from api_client import ClienteOpenLibrary

class TestLibro(unittest.TestCase):
    """
    Pruebas unitarias para la clase Libro, validando inicialización y expresiones regulares.
    """

    def test_creacion_libro_valido(self):
        # Datos correctos simulando la respuesta de la API de Open Library
        datos = {
            "key": "/works/OL257912W",
            "title": "Introduction to Algorithms",
            "author_name": ["Thomas H. Cormen", "Charles E. Leiserson"],
            "first_publish_year": 1989,
            "edition_count": 4,
            "language": ["eng", "spa"]
        }
        
        libro = Libro(datos)
        
        self.assertEqual(libro.id_limpio, "OL257912W")
        self.assertEqual(libro.titulo, "Introduction to Algorithms")
        self.assertEqual(libro.autores, "Thomas H. Cormen, Charles E. Leiserson")
        self.assertEqual(libro.anio, 1989)
        self.assertEqual(libro.cant_ediciones, 4)
        self.assertTrue(libro.tiene_idioma("spa"))
        self.assertTrue(libro.tiene_idioma("ENG"))  # Prueba de case-insensitivity
        self.assertFalse(libro.tiene_idioma("fra"))

    def test_valores_por_defecto_y_seguridad(self):
        # Datos con campos vacíos o corruptos
        datos = {
            "key": "/books/OL9999M",
            # title ausente
            # author_name ausente
            "first_publish_year": "no_es_un_numero",
            "edition_count": None,
            "language": "no_es_una_lista"
        }
        
        libro = Libro(datos)
        
        self.assertEqual(libro.titulo, "Sin título")
        self.assertEqual(libro.autores, "Autor desconocido")
        self.assertEqual(libro.anio, 0)
        self.assertEqual(libro.cant_ediciones, 0)
        self.assertEqual(libro.idiomas, [])

    def test_validacion_regex_id_valido(self):
        # Formatos válidos de obras (/works/...) y ediciones (/books/...)
        l1 = Libro({"key": "/works/OL123456W"})
        l2 = Libro({"key": "/books/OL987654M"})
        
        self.assertEqual(l1.id_limpio, "OL123456W")
        self.assertEqual(l2.id_limpio, "OL987654M")

    def test_validacion_regex_id_invalido(self):
        # Formatos incorrectos deben lanzar ValueError
        casos_invalidos = [
            "/works/",                  # Vacío después de works
            "/works/OL123W/extra",       # Parte extra al final
            "OL12345W",                 # Sin prefijo /works/
            "/work/OL12345W",           # Singular 'work' en lugar de 'works'
            "/books/OL123M1",           # Dígito al final en lugar de letra
            "",                         # Cadena vacía
        ]
        
        for id_invalido in casos_invalidos:
            with self.assertRaises(ValueError):
                Libro({"key": id_invalido})


class TestAnalizadorBiblioteca(unittest.TestCase):
    """
    Pruebas unitarias para la lógica del Analizador (filtros, promedio y CSV).
    """

    def setUp(self):
        # Lista de libros simulados
        self.libros = [
            Libro({"key": "/works/OL1W", "title": "Libro A", "first_publish_year": 1995, "edition_count": 2, "language": ["eng"]}),
            Libro({"key": "/works/OL2W", "title": "Libro B", "first_publish_year": 2005, "edition_count": 8, "language": ["eng", "spa"]}),
            Libro({"key": "/works/OL3W", "title": "Libro C", "first_publish_year": 2015, "edition_count": 5, "language": ["spa"]}),
            Libro({"key": "/works/OL4W", "title": "Libro D", "first_publish_year": 2022, "edition_count": 1, "language": ["por"]}),
            Libro({"key": "/works/OL5W", "title": "Libro E", "first_publish_year": 0, "edition_count": 4, "language": []}) # Sin año
        ]
        self.analizador = AnalizadorBiblioteca(self.libros)

    def test_filtrar_por_decada(self):
        # Filtrar década 2000-2009
        libros_2000s = self.analizador.filtrar_por_decada(2000, 2009)
        self.assertEqual(len(libros_2000s), 1)
        self.assertEqual(libros_2000s[0].titulo, "Libro B")

        # Filtrar rango amplio
        libros_recientes = self.analizador.filtrar_por_decada(2010, 2030)
        self.assertEqual(len(libros_recientes), 2)
        nombres = [l.titulo for l in libros_recientes]
        self.assertIn("Libro C", nombres)
        self.assertIn("Libro D", nombres)

    def test_calcular_promedio_ediciones(self):
        # Promedio: (2 + 8 + 5 + 1 + 4) / 5 = 20 / 5 = 4.0
        promedio = self.analizador.calcular_promedio_ediciones()
        self.assertEqual(promedio, 4.0)

        # Caso de analizador vacío
        analizador_vacio = AnalizadorBiblioteca([])
        self.assertEqual(analizador_vacio.calcular_promedio_ediciones(), 0.0)

    def test_obtener_porcentajes_idiomas(self):
        # Total = 5 libros.
        # Libros en español (spa): 2 (Libro B, Libro C) -> 40%
        # Libros en inglés (eng): 2 (Libro A, Libro B) -> 40%
        # Libros en otros/vacíos: 2 (Libro D (por), Libro E (vacío)) -> 40%
        # Nota: La suma de porcentajes puede exceder 100% porque un libro puede estar en varios idiomas (porcentaje individual respecto a total)
        stats = self.analizador.obtener_porcentajes_idiomas()
        
        self.assertEqual(stats["cant_total"], 5)
        self.assertEqual(stats["cant_espanol"], 2)
        self.assertEqual(stats["cant_ingles"], 2)
        self.assertEqual(stats["espanol"], 40.0)
        self.assertEqual(stats["ingles"], 40.0)

    def test_obtener_clasicos(self):
        # Orden esperado por ediciones descendente:
        # Libro B (8), Libro C (5), Libro E (4), Libro A (2), Libro D (1)
        clasicos = self.analizador.obtener_clasicos(3)
        
        self.assertEqual(len(clasicos), 3)
        self.assertEqual(clasicos[0].titulo, "Libro B")
        self.assertEqual(clasicos[1].titulo, "Libro C")
        self.assertEqual(clasicos[2].titulo, "Libro E")

    def test_exportar_a_csv(self):
        nombre_test_csv = "temp_test_export.csv"
        
        # Asegurarse de que el archivo de prueba no exista previamente
        if os.path.exists(nombre_test_csv):
            os.remove(nombre_test_csv)
            
        try:
            self.analizador.exportar_a_csv(nombre_test_csv)
            self.assertTrue(os.path.exists(nombre_test_csv))
            
            # Validar contenido básico del CSV
            with open(nombre_test_csv, mode="r", encoding="utf-8") as f:
                lineas = f.readlines()
                self.assertGreater(len(lineas), 1)  # Cabecera + datos
                self.assertIn("ID Limpio;Titulo;Autores;Anio Publicacion;Ediciones;Idiomas", lineas[0])
                self.assertIn("OL1W;Libro A;Autor desconocido;1995;2;eng", lineas[1])
        finally:
            # Limpieza del archivo temporal
            if os.path.exists(nombre_test_csv):
                os.remove(nombre_test_csv)


class TestClienteOpenLibrary(unittest.IsolatedAsyncioTestCase):
    """
    Pruebas unitarias para el consumo de la API de Open Library de forma aislada (Mocking).
    """

    @patch("aiohttp.ClientSession.get")
    async def test_buscar_libros_async_mock(self, mock_get):
        # Datos simulados de la API de Open Library
        mock_response_json = {
            "numFound": 1,
            "docs": [
                {
                    "key": "/works/OL12345W",
                    "title": "Mocked Artificial Intelligence Book",
                    "author_name": ["Alan Turing"],
                    "first_publish_year": 1950,
                    "edition_count": 10,
                    "language": ["eng"]
                }
            ]
        }
        
        # Configurar el mock para retornar la respuesta JSON ficticia asíncronamente
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response_json)
        
        # Configurar el administrador de contexto asíncrono del session.get
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        cliente = ClienteOpenLibrary()
        libros_resultado = await cliente.buscar_libros_async("artificial intelligence")
        
        self.assertEqual(len(libros_resultado), 1)
        libro = libros_resultado[0]
        self.assertEqual(libro.titulo, "Mocked Artificial Intelligence Book")
        self.assertEqual(libro.id_limpio, "OL12345W")
        self.assertEqual(libro.autores, "Alan Turing")
        self.assertEqual(libro.anio, 1950)
        self.assertEqual(libro.cant_ediciones, 10)


if __name__ == "__main__":
    unittest.main()
