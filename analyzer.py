import csv
from models import Libro

class AnalizadorBiblioteca:
    """
    Clase encargada de procesar, auditar y analizar la colección de libros recuperada.
    Utiliza conceptos de programación funcional (map, filter, lambda) para realizar métricas.
    """

    def __init__(self, lista_libros: list[Libro]):
        """
        Inicializa el analizador con una lista de objetos Libro.
        """
        self.lista_libros: list[Libro] = lista_libros

    def filtrar_por_decada(self, anio_inicio: int, anio_fin: int) -> list[Libro]:
        """
        Filtra los libros publicados en una década o rango de años específico.
        Implementado con programación funcional (filter y lambda) para cumplir el requisito.
        """
        # Se filtran solo aquellos libros cuyo año sea válido y se encuentre en el rango
        return list(
            filter(
                lambda libro: libro.anio > 0 and (anio_inicio <= libro.anio <= anio_fin),
                self.lista_libros
            )
        )

    def calcular_promedio_ediciones(self) -> float:
        """
        Calcula el promedio de cantidad de ediciones entre los libros recolectados.
        Implementado con programación funcional (map y lambda) para cumplir la consigna planteada en el curso.
        """
        if not self.lista_libros:
            return 0.0

        # Mapea cada libro a su cantidad de ediciones y realiza la suma
        total_ediciones = sum(map(lambda libro: libro.cant_ediciones, self.lista_libros))
        return float(total_ediciones / len(self.lista_libros))

    def obtener_porcentajes_idiomas(self) -> dict[str, float]:
        """
        Calcula el porcentaje de libros disponibles en español (spa) e inglés (eng)
        sobre el total de libros recolectados, permitiendo diagnosticar la brecha lingüística.
        Implementado usando programación funcional (filter y lambda).
        """
        total_libros = len(self.lista_libros)
        if total_libros == 0:
            return {"espanol": 0.0, "ingles": 0.0, "otros": 0.0}

        # Filtrar libros con disponibilidad en español e inglés
        libros_es = list(filter(lambda l: l.tiene_idioma("spa"), self.lista_libros))
        libros_en = list(filter(lambda l: l.tiene_idioma("eng"), self.lista_libros))
        
        # Libros que no tienen 'spa' ni 'eng', o no tienen idiomas registrados
        libros_otros = list(filter(lambda l: not l.tiene_idioma("spa") and not l.tiene_idioma("eng"), self.lista_libros))

        porcentaje_es = (len(libros_es) / total_libros) * 100
        porcentaje_en = (len(libros_en) / total_libros) * 100
        porcentaje_otros = (len(libros_otros) / total_libros) * 100

        return {
            "espanol": round(porcentaje_es, 2),
            "ingles": round(porcentaje_en, 2),
            "otros": round(porcentaje_otros, 2),
            "cant_espanol": len(libros_es),
            "cant_ingles": len(libros_en),
            "cant_total": total_libros
        }

    def obtener_clasicos(self, top_n: int = 5) -> list[Libro]:
        """
        Identifica los "clásicos imprescindibles" ordenando los libros
        por cantidad de ediciones de forma descendente.
        """
        # Ordenación funcional usando la función integrada sorted y una expresión lambda
        return sorted(self.lista_libros, key=lambda l: l.cant_ediciones, reverse=True)[:top_n]

    def exportar_a_csv(self, nombre_archivo: str) -> None:
        """
        Exporta la lista actual de libros analizados a un archivo CSV estructurado.
        """
        try:
            with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo, delimiter=";")
                
                # Escribir la cabecera
                escritor.writerow([
                    "ID Limpio", 
                    "Titulo", 
                    "Autores", 
                    "Anio Publicacion", 
                    "Ediciones", 
                    "Idiomas"
                ])
                
                # Escribir cada registro de libro
                for libro in self.lista_libros:
                    idiomas_str = ", ".join(libro.idiomas) if libro.idiomas else "N/D"
                    escritor.writerow([
                        libro.id_limpio,
                        libro.titulo,
                        libro.autores,
                        libro.anio if libro.anio > 0 else "N/D",
                        libro.cant_ediciones,
                        idiomas_str
                    ])
            print(f"\n[Éxito] Reporte exportado correctamente a: '{nombre_archivo}'")
        except IOError as e:
            print(f"\n[Error] No se pudo exportar el archivo CSV: {e}")
