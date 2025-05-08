"""
Para generar un ejecutable standalone (.exe) de este script con PyInstaller:
1. Asegurate de tener PyInstaller instalado:
   pip install pyinstaller

2. Ejecutá en la terminal:
   pyinstaller --noconsole --onefile --name ComparadorPPTX pptx_comparador_gui.py

Esto creará un ejecutable en la carpeta /dist que podrás distribuir sin necesidad de instalar Python.
"""

import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pptx import Presentation
from difflib import SequenceMatcher
from collections import defaultdict
import pandas as pd

class PPTXComparadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Comparador de PowerPoints")
        self.root.geometry("1000x600")

        self.similares = []  # Almacena tuplas con archivos similares o duplicados
        self.archivos = []   # Lista de todos los archivos pptx encontrados

        # Botón para elegir carpeta
        self.btn_seleccionar = tk.Button(root, text="📂 Seleccionar Carpeta", command=self.seleccionar_carpeta)
        self.btn_seleccionar.pack(pady=10)

        # Texto informativo sobre la carpeta elegida
        self.lbl_info = tk.Label(root, text="No hay carpeta seleccionada")
        self.lbl_info.pack()

        # Tabla para mostrar archivos comparados
        self.tree = ttk.Treeview(root, columns=("archivo1", "archivo2", "similitud", "borrar"), show="headings", selectmode="extended")
        for col in ("archivo1", "archivo2", "similitud", "borrar"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=250 if col != "similitud" else 80)
        self.tree.pack(expand=True, fill="both")

        # Botones adicionales
        self.exportar_btn = tk.Button(root, text="📤 Exportar a Excel", command=self.exportar_excel)
        self.exportar_btn.pack(pady=5)

        self.borrar_btn = tk.Button(root, text="🗑️ Borrar seleccionados", command=self.borrar_seleccionados)
        self.borrar_btn.pack(pady=5)

    def seleccionar_carpeta(self):
        # Abre diálogo para elegir carpeta
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.lbl_info.config(text=f"📁 Carpeta seleccionada: {carpeta}")
            self.procesar_carpeta(carpeta)

    def procesar_carpeta(self, carpeta):
        self.similares.clear()
        self.tree.delete(*self.tree.get_children())

        # 🔍 Buscar todos los archivos .pptx
        self.archivos = self.buscar_pptx(carpeta)
        hashes = defaultdict(list)
        contenidos = {}

        # 🧾 Recorremos todos los archivos y:
        # 1. Calculamos hash MD5 (para detectar duplicados exactos)
        # 2. Extraemos texto de las diapositivas (para similitud parcial)
        for archivo in self.archivos:
            h = self.hash_md5(archivo)
            hashes[h].append(archivo)
            contenidos[archivo] = self.extraer_texto(archivo)

        # 🧩 Comparación por HASH: si hay más de un archivo con mismo hash → son duplicados exactos
        for grupo in hashes.values():
            if len(grupo) > 1:
                # Iteramos sobre todos los pares posibles del grupo
                for i in range(len(grupo)):
                    for j in range(i+1, len(grupo)):
                        self.agregar_resultado(grupo[i], grupo[j], 1.0)

        # 📐 Comparación por contenido textual (diapositivas)
        # Recorremos todos los pares posibles de archivos diferentes
        for i in range(len(self.archivos)):
            for j in range(i+1, len(self.archivos)):
                a1, a2 = self.archivos[i], self.archivos[j]
                sim = self.similitud(contenidos[a1], contenidos[a2])
                if sim >= 0.85 and sim < 1.0:
                    self.agregar_resultado(a1, a2, sim)

    def agregar_resultado(self, archivo1, archivo2, sim):
        # Almacena el resultado y lo agrega visualmente a la tabla
        self.similares.append((archivo1, archivo2, sim))
        self.tree.insert("", "end", values=(archivo1, archivo2, f"{sim*100:.1f}%", archivo2))  # Por defecto se propone borrar archivo2

    def borrar_seleccionados(self):
        # Elimina el archivo marcado en la columna 'borrar' de cada fila seleccionada
        items = self.tree.selection()
        if not items:
            messagebox.showinfo("Info", "Seleccioná al menos una fila para borrar.")
            return

        confirm = messagebox.askyesno("Confirmar", "¿Seguro que querés borrar los archivos seleccionados?")
        if not confirm:
            return

        errores = []
        for item in items:
            valores = self.tree.item(item)["values"]
            archivo_borrar = valores[3]
            try:
                os.remove(archivo_borrar)
            except Exception as e:
                errores.append((archivo_borrar, str(e)))

        if errores:
            mensaje = "⚠️ Archivos con errores al borrar:\n" + "\n".join(f"{f}: {e}" for f, e in errores)
            messagebox.showwarning("Errores", mensaje)
        else:
            messagebox.showinfo("OK", "Archivos eliminados correctamente.")
        self.tree.delete(*items)

    def exportar_excel(self):
        # Exporta los archivos comparados a un archivo Excel
        if not self.similares:
            messagebox.showinfo("Sin datos", "No hay resultados para exportar.")
            return

        df = pd.DataFrame([{
            "Archivo 1": a1,
            "Archivo 2": a2,
            "Similitud (%)": round(sim * 100, 1)
        } for a1, a2, sim in self.similares])

        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if ruta:
            df.to_excel(ruta, index=False)
            messagebox.showinfo("Exportado", f"Archivo guardado en:\n{ruta}")

    # -------------------------------
    # FUNCIONES AUXILIARES
    # -------------------------------

    def buscar_pptx(self, carpeta):
        # Busca todos los archivos .pptx recursivamente
        return [os.path.join(root, f)
                for root, _, files in os.walk(carpeta)
                for f in files if f.lower().endswith(".pptx")]

    def hash_md5(self, archivo):
        # Calcula el hash MD5 (identificador único) de un archivo binario
        h = hashlib.md5()
        with open(archivo, "rb") as f:
            for bloque in iter(lambda: f.read(4096), b""):
                h.update(bloque)
        return h.hexdigest()

    def extraer_texto(self, archivo):
        # Lee cada diapositiva del archivo y extrae todo el texto visible
        try:
            prs = Presentation(archivo)
            return "\n".join(shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text"))
        except Exception:
            return ""

    def similitud(self, txt1, txt2):
        # Calcula cuán similares son dos textos (0.0 = nada parecido, 1.0 = iguales)
        return SequenceMatcher(None, txt1, txt2).ratio()

# --- EJECUCIÓN DE LA APLICACIÓN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PPTXComparadorApp(root)
    root.mainloop()
