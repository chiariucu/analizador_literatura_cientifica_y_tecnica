import asyncio
import re
import sys
from api_client import ClienteOpenLibrary
from analyzer import AnalizadorBiblioteca

def sanear_nombre_archivo(tematica: str) -> str:
    """
    Sanea el término de búsqueda usando expresiones regulares para convertirlo
    en un nombre de archivo CSV válido y limpio.
    """
    # Eliminar caracteres especiales
    saneado = re.sub(r"[^\w\s-]", "", tematica).strip().lower()
    # Reemplazar espacios y guiones repetidos por un guion bajo
    saneado = re.sub(r"[-\s]+", "_", saneado)
    return f"reporte_{saneado}.csv"

async def async_main():
    print("=" * 70)
    print("  ANALIZADOR CRÍTICO DE LITERATURA CIENTÍFICA Y TÉCNICA (API Open Library)")
    print("=" * 70)
    print("  Herramienta de Auditoría y Análisis Bibliográfico")
    print("-" * 70)
    
    # Solicitar temática de búsqueda al usuario
    tematica = input("\nIngrese la temática técnica o científica a auditar (ej. 'data science', 'python'): ").strip()
    if not tematica:
        print("[Error] La temática ingresada no puede estar vacía.")
        return

    print(f"\n[1/3] Conectando a la API de Open Library de forma asíncrona...")
    print(f"      Buscando obras literarias relacionadas con: '{tematica}'...")
    
    # Instanciar el cliente de API
    cliente = ClienteOpenLibrary()
    
    # Realizar la búsqueda asíncrona de hasta 120 libros para obtener una buena muestra
    libros = await cliente.buscar_libros_async(tematica, limit=120)
    
    total_recuperados = len(libros)
    if total_recuperados == 0:
        print("\n[Resultado] No se encontraron libros válidos para la temática especificada.")
        print("            Verifique su conexión a internet o intente con otro término.")
        return

    print(f"[2/3] Se recuperaron y validaron exitosamente {total_recuperados} registros bibliográficos.")
    print("[3/3] Iniciando el análisis estadístico de obsolescencia y brecha lingüística...")
    
    # Instanciar el Analizador
    analizador = AnalizadorBiblioteca(libros)
    
    # --- ANÁLISIS A: Obsolescencia Tecnológica (Distribución Temporal) ---
    print("\n" + "-" * 70)
    print(" METRICA A: INDICE DE VIGENCIA HISTÓRICA / DISTRIBUCIÓN POR DÉCADAS")
    print("-" * 70)
    
    # Filtrados por décadas usando programación funcional
    libros_pre_2000 = analizador.filtrar_por_decada(1900, 1999)
    libros_2000_2009 = analizador.filtrar_por_decada(2000, 2009)
    libros_2010_2019 = analizador.filtrar_por_decada(2010, 2019)
    libros_2020_pres = analizador.filtrar_por_decada(2020, 2030)
    
    # Libros sin año registrado
    libros_sin_anio = list(filter(lambda l: l.anio == 0, libros))
    
    print(f" * Décadas Anteriores (<2000): {len(libros_pre_2000):3d} libros ({len(libros_pre_2000)/total_recuperados*100:5.2f}%)  [Vigencia crítica]")
    print(f" * Década del 2000 (2000-2009): {len(libros_2000_2009):3d} libros ({len(libros_2000_2009)/total_recuperados*100:5.2f}%)  [Riesgo de obsolescencia]")
    print(f" * Década del 2010 (2010-2019): {len(libros_2010_2019):3d} libros ({len(libros_2010_2019)/total_recuperados*100:5.2f}%)  [Vigencia intermedia]")
    print(f" * Década Actual    (>= 2020): {len(libros_2020_pres):3d} libros ({len(libros_2020_pres)/total_recuperados*100:5.2f}%)  [Vanguardia tecnológica]")
    if libros_sin_anio:
        print(f" * Sin año registrado        : {len(libros_sin_anio):3d} libros ({len(libros_sin_anio)/total_recuperados*100:5.2f}%)")

    # --- ANÁLISIS B: Brecha Lingüística (Sesgo de Idioma) ---
    print("\n" + "-" * 70)
    print(" METRICA B: AUDITORÍA DE BRECHA LINGÜÍSTICA")
    print("-" * 70)
    idiomas_stats = analizador.obtener_porcentajes_idiomas()
    print(f" * Libros disponibles en INGLÉS (eng) : {idiomas_stats['cant_ingles']:3d} de {idiomas_stats['cant_total']} ({idiomas_stats['ingles']:.2f}%)")
    print(f" * Libros disponibles en ESPAÑOL (spa): {idiomas_stats['cant_espanol']:3d} de {idiomas_stats['cant_total']} ({idiomas_stats['espanol']:.2f}%)")
    print(f" * Brecha real de acceso directo      : {idiomas_stats['ingles'] - idiomas_stats['espanol']:.2f}% de desventaja lingüística")
    print(f"   Nota: Esto visualiza la falta de traducción y el sesgo de publicación en literatura técnica.")

    # --- ANÁLISIS C: Clásicos Imprescindibles y Métricas de Ediciones ---
    print("\n" + "-" * 70)
    print(" METRICA C: RECOMENDACIÓN DE 'CLÁSICOS' (MAYOR NÚMERO DE EDICIONES)")
    print("-" * 70)
    promedio_ediciones = analizador.calcular_promedio_ediciones()
    print(f" * Promedio global de ediciones por obra: {promedio_ediciones:.2f} ediciones.")
    
    clasicos = analizador.obtener_clasicos(5)
    print("\n Top 5 Clásicos de Referencia Identificados:")
    for idx, libro in enumerate(clasicos, 1):
        autor_corto = libro.autores if len(libro.autores) < 35 else f"{libro.autores[:32]}..."
        print(f"   {idx}. {libro.titulo[:40]:<40} | Autores: {autor_corto:<35} | Año: {libro.anio if libro.anio > 0 else 'N/D':<4} | Ediciones: {libro.cant_ediciones}")

    # --- EXPORTAR REPORTES ---
    print("\n" + "=" * 70)
    print(" EXPORTACIÓN DE RESULTADOS")
    print("=" * 70)
    desea_exportar = input("¿Desea exportar el listado completo de libros analizados a un archivo CSV? (S/N): ").strip().lower()
    
    if desea_exportar in ["s", "si", "yes", "y"]:
        nombre_csv = sanear_nombre_archivo(tematica)
        analizador.exportar_a_csv(nombre_csv)
    else:
        print("\nExportación omitida por el usuario.")

    print("\nGracias por utilizar el Analizador Crítico de Literatura Científica y Técnica.")

def main():
    # Asegurar soporte de encoding correcto en la terminal Windows
    if sys.platform.startswith("win"):
        import os
        os.system("chcp 65001 > nul")

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n\nEjecución cancelada por el usuario.")
    except Exception as e:
        print(f"\n[Error Crítico] Ocurrió una falla general: {e}")

if __name__ == "__main__":
    main()
