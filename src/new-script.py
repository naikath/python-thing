import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from difflib import SequenceMatcher
from collections import defaultdict
import pandas as pd

from pptx import Presentation
from docx import Document
from openpyxl import load_workbook

def custom_prompt(parent, archivo1, archivo2):
    top = tk.Toplevel(parent)
    top.title("¿Qué archivo querés borrar?")
    top.grab_set()

    result = {"value": None}

    tk.Label(top, text="Elegí el archivo a borrar:", font=("Segoe UI", 10, "bold")).pack(padx=20, pady=(10, 5))
    tk.Label(top, text=f"1️⃣ {archivo1}").pack(padx=20, pady=2)
    tk.Label(top, text=f"2️⃣ {archivo2}").pack(padx=20, pady=2)

    def choose(option):
        result["value"] = option
        top.destroy()

    frame = tk.Frame(top)
    frame.pack(pady=10)
    tk.Button(frame, text="🗑️ Borrar Archivo 1", command=lambda: choose("A")).pack(side="left", padx=5)
    tk.Button(frame, text="🗑️ Borrar Archivo 2", command=lambda: choose("B")).pack(side="left", padx=5)
    tk.Button(frame, text="Cancelar", command=top.destroy).pack(side="left", padx=5)

    top.wait_window()
    return result["value"]

# Clase principal de la aplicación para comparar archivos PPTX
class ComparadorArchivosApp:
    def __init__(self, root):
        # Inicializa la ventana principal
        self.root = root
        # Título de la ventana
        self.root.title("🧠 Comparador de Archivos")
        # Tamaño de la ventana
        self.root.geometry("1000x600")

        # Lista que almacena los resultados de archivos similares
        self.similares = []
        # Lista que almacena los archivos pptx encontrados en la carpeta seleccionada
        self.archivos = []
        # Carpeta de base elegida, para calcular rutas relativas
        self.carpeta_base = ""

        # Botón para seleccionar la carpeta donde se encuentran los archivos PPTX
        self.btn_seleccionar = tk.Button(root, text="📂 Seleccionar Carpeta", command=self.seleccionar_carpeta)
        self.btn_seleccionar.pack(pady=10)

        # Etiqueta para mostrar información sobre la carpeta seleccionada
        self.lbl_info = tk.Label(root, text="No hay carpeta seleccionada")
        self.lbl_info.pack()

        # Tabla con columnas agrupadas por tipo de archivo
        self.tree = ttk.Treeview(root, columns=("tipo", "archivo1", "archivo2", "similitud"), show="headings", selectmode="extended")
        for col in ("tipo", "archivo1", "archivo2", "similitud"):
            # Establece el nombre de cada columna
            self.tree.heading(col, text=col)
            # Ajusta el tamaño de las columnas
            self.tree.column(col, width=150 if col == "tipo" else 300)
        # Agrega la tabla a la ventana
        self.tree.pack(expand=True, fill="both")

        # Botón para exportar los resultados a un archivo de Excel
        self.exportar_btn = tk.Button(root, text="📤 Exportar a Excel", command=self.exportar_excel)
        self.exportar_btn.pack(pady=5)

        # Botón para borrar los archivos seleccionados en la tabla
        self.borrar_btn = tk.Button(root, text="🗑️ Borrar seleccionados", command=self.borrar_seleccionados)
        self.borrar_btn.pack(pady=5)

    def seleccionar_carpeta(self):
        # Método para seleccionar la carpeta con archivos PPTX
        # Abre el cuadro de diálogo para seleccionar una carpeta
        carpeta = filedialog.askdirectory()
        if carpeta:
            # Actualiza el texto de la etiqueta con la carpeta seleccionada
            self.lbl_info.config(text=f"📁 Carpeta seleccionada: {carpeta}")
            self.carpeta_base = carpeta
            # Procesa los archivos dentro de la carpeta
            self.procesar_carpeta(carpeta)

    def procesar_carpeta(self, carpeta):
        # Procesa todos los archivos pptx en la carpeta seleccionada
        # Limpia la lista de archivos similares
        self.similares.clear()
        # Elimina todas las filas de la tabla
        self.tree.delete(*self.tree.get_children())

        # 🔍 Buscar todos los archivos .pptx en la carpeta seleccionada
        self.archivos = self.buscar_archivos(carpeta)
        # Diccionario para almacenar los archivos agrupados por hash
        hashes = defaultdict(list)
        # Diccionario para almacenar el texto extraído de cada archivo
        contenidos = {}

        # 🧾 Recorremos todos los archivos y realizamos dos procesos:
        # 1. Calcular el hash MD5 para detectar duplicados exactos
        # 2. Extraer el texto de cada diapositiva para comparar su contenido textual
        for archivo in self.archivos:
            # Calcula el hash MD5 del archivo
            h = self.hash_md5(archivo)
            # Agrupa el archivo por su hash
            hashes[h].append(archivo)
            # Extrae el texto del archivo
            contenidos[archivo] = self.extraer_texto(archivo)

        # 🧩 Comparación por HASH: si hay más de un archivo con el mismo hash, son duplicados exactos
        for grupo in hashes.values():
            if len(grupo) > 1:
                # Compara todos los pares posibles dentro del grupo de archivos con el mismo hash
                for i in range(len(grupo)):
                    for j in range(i+1, len(grupo)):
                        # Añade los duplicados exactos a la lista
                        self.agregar_resultado(grupo[i], grupo[j], 1.0)

        # 📐 Comparación por contenido textual (diapositivas)
        # Compara todos los pares de archivos diferentes
        for i in range(len(self.archivos)):
            for j in range(i+1, len(self.archivos)):
                # Selecciona dos archivos distintos
                a1, a2 = self.archivos[i], self.archivos[j]
                tipo1 = os.path.splitext(a1)[1].lower()
                tipo2 = os.path.splitext(a2)[1].lower()
                if tipo1 != tipo2:
                    # comparo solo entre mismos tipos
                    continue
                texto1 = self.limpiar_texto(contenidos[a1])
                texto2 = self.limpiar_texto(contenidos[a2])
                # Calcula la similitud de su contenido textual
                sim = self.similitud(texto1, texto2)
                if sim >= 0.85 and sim < 1.0:
                    # Añade los archivos con similitud parcial a la lista
                    self.agregar_resultado(a1, a2, sim)

        # Ordenar por tipo
        self.similares.sort(key=lambda x: x[0])

        # Volver a mostrar la tabla ordenada
        self.tree.delete(*self.tree.get_children())
        for tipo, a1, a2, sim in self.similares:
            self.tree.insert("", "end", values=(tipo, a1, a2, f"{sim*100:.1f}%"))

    def agregar_resultado(self, archivo1, archivo2, sim):
        # Agrega un resultado de comparación a la tabla y a la lista de resultados
        # Ruta relativa
        rel1 = os.path.relpath(archivo1, self.carpeta_base)
        # Ruta relativa
        rel2 = os.path.relpath(archivo2, self.carpeta_base)
        tipo = os.path.splitext(archivo1)[1].replace('.', '').upper()
        # Almacena el resultado de la comparación y lo muestra en la tabla
        # Guarda el par de archivos y su similitud
        self.similares.append((tipo, rel1, rel2, sim))

    def borrar_seleccionados(self):
        # Método para eliminar los archivos seleccionados en la tabla
        # Obtiene los elementos seleccionados
        items = self.tree.selection()
        if not items:
            # Muestra un mensaje si no se seleccionó nada
            messagebox.showinfo("Info", "Seleccioná al menos una fila para borrar.")
            return

        # Confirma si realmente se quieren borrar los archivos
        confirm = messagebox.askyesno("Confirmar", "¿Seguro que querés borrar los archivos seleccionados?")
        if not confirm:
            # Si no se confirma, no hace nada
            return

        # Lista para almacenar posibles errores al intentar borrar los archivos
        errores = []

        # Copia de los items porque vamos a ir modificando el tree
        for item in list(items):
            # Obtiene los valores de la fila seleccionada
            valores = self.tree.item(item)["values"]
            _, archivo1_rel, archivo2_rel, _ = valores

            # Usamos el custom_prompt para elegir cuál borrar
            eleccion = custom_prompt(self.root, archivo1_rel, archivo2_rel)
            if eleccion == "A":
                archivo_borrar_rel = archivo1_rel
            elif eleccion == "B":
                archivo_borrar_rel = archivo2_rel
            else:
                continue  # Si se canceló, no hace nada

            archivo_borrar_abs = os.path.join(self.carpeta_base, archivo_borrar_rel)

            try:
                # Intenta eliminar el archivo
                os.remove(archivo_borrar_abs)
            except Exception as e:
                # Si hay error, lo almacena
                errores.append((archivo_borrar_rel, str(e)))
                continue

            # Eliminar de self.similares
            self.similares = [tpl for tpl in self.similares if archivo_borrar_rel not in tpl]

            # Refrescar la tabla
            # Elimina las filas seleccionadas de la tabla
            self.tree.delete(*self.tree.get_children())
            for tipo, a1, a2, sim in self.similares:
                self.tree.insert("", "end", values=(tipo, a1, a2, f"{sim*100:.1f}%"))

        if errores:
            # Si hubo errores, muestra un mensaje con los detalles
            mensaje = "⚠️ Archivos con errores al borrar:\n" + "\n".join(f"{f}: {e}" for f, e in errores)
            messagebox.showwarning("Errores", mensaje)
        else:
            # Muestra mensaje si se borraron correctamente
            messagebox.showinfo("OK", "Archivos eliminados correctamente.")

    def exportar_excel(self):
        # Método para exportar los resultados a un archivo Excel
        if not self.similares:
            # Muestra mensaje si no hay resultados
            messagebox.showinfo("Sin datos", "No hay resultados para exportar.")
            return

        # Convierte los resultados a un DataFrame de Pandas
        df = pd.DataFrame([{
            "Tipo": tipo,
            "Archivo 1": a1,
            "Archivo 2": a2,
            "Similitud (%)": round(sim * 100, 1)
        } for tipo, a1, a2, sim in self.similares])

        # Abre el cuadro de diálogo para elegir la ruta y el nombre del archivo a guardar
        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if ruta:
            # Exporta los datos a un archivo Excel
            df.to_excel(ruta, index=False)
            # Muestra mensaje de éxito
            messagebox.showinfo("Exportado", f"Archivo guardado en:\n{ruta}")

    # -------------------------------
    # FUNCIONES AUXILIARES
    # -------------------------------

    def buscar_archivos(self, carpeta):
        # Busca todos los archivos .pptx en la carpeta de forma recursiva
        extensiones = (".pptx", ".docx", ".xlsx")
        return [os.path.join(root, f)
                for root, _, files in os.walk(carpeta)
                for f in files if f.lower().endswith(extensiones)]

    def hash_md5(self, archivo):
        # Calcula el hash MD5 (identificador único) de un archivo binario
        h = hashlib.md5()
        with open(archivo, "rb") as f:
            # Lee el archivo en bloques
            for bloque in iter(lambda: f.read(4096), b""):
                # Actualiza el hash con cada bloque
                h.update(bloque)
        # Retorna el hash MD5
        return h.hexdigest()

    def extraer_texto(self, archivo):
        # Detecta tipo de archivo y aplica extractor correspondiente
        if archivo.lower().endswith(".pptx"):
            return self.extraer_texto_pptx(archivo)
        elif archivo.lower().endswith(".docx"):
            return self.extraer_texto_docx(archivo)
        elif archivo.lower().endswith(".xlsx"):
            return self.extraer_texto_xlsx(archivo)
        return ""

    def extraer_texto_pptx(self, archivo):
        # Extrae el texto de todas las diapositivas de un archivo pptx
        prs = Presentation(archivo)
        return "\n".join(shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text"))

    def extraer_texto_docx(self, archivo):
        doc = Document(archivo)
        contenido = []
        for para in doc.paragraphs:
            if para.text.strip():
                contenido.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    contenido.append(cell.text)
        return "\n".join(contenido)

    def extraer_texto_xlsx(self, archivo):
        wb = load_workbook(archivo, data_only=True)
        contenido = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                contenido.extend([str(cell) for cell in row if cell is not None])
        return "\n".join(contenido)

    def limpiar_texto(self, texto):
        return " ".join(texto.lower().split())

    def similitud(self, txt1, txt2):
        # Calcula la similitud entre dos textos
        return SequenceMatcher(None, txt1, txt2).ratio()

# --- EJECUCIÓN DE LA APLICACIÓN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ComparadorArchivosApp(root)
    root.mainloop()
