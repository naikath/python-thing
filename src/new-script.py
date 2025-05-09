import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pptx import Presentation
from difflib import SequenceMatcher
from collections import defaultdict
import pandas as pd

def custom_prompt(parent):
    # Create a modal top-level window
    top = tk.Toplevel(parent)
    top.title("Elige una opción")
    top.grab_set()  # Makes the prompt modal (blocks main window)

    result = {"value": None}

    tk.Label(top, text="¿Qué querés hacer?").pack(padx=20, pady=10)

    def choose(option):
        result["value"] = option
        top.destroy()

    # Buttons with custom return values
    tk.Button(top, text="Archivo1", command=lambda: choose("1")).pack(side="left", padx=10, pady=10)
    tk.Button(top, text="Archivo2", command=lambda: choose("2")).pack(side="left", padx=10, pady=10)
    tk.Button(top, text="Cancelar", command=top.destroy).pack(side="left", padx=10, pady=10)

    top.wait_window()  # Waits until this window is closed
    return result["value"]




class AppCompararPptx:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Comparador de PowerPoints")
        self.root.geometry("1000x600")

        self.archivos_similares = []  # Almacena tuplas con archivos similares o duplicados
        self.archivos = []   # Lista de todos los archivos pptx encontrados

        # Botón para elegir carpeta
        # UI setup
        self.boton_seleccionar = tk.Button(root, text="📂 Seleccionar Carpeta", command=self.seleccionar_carpeta)
        self.boton_seleccionar.pack(pady=10)

        # Texto informativo sobre la carpeta elegida
        self.texto_info = tk.Label(root, text="No hay carpeta seleccionada")
        self.texto_info.pack()

        # Tabla para mostrar archivos comparados
        self.tree = ttk.Treeview(root, columns=("archivo1", "archivo2", "similitud", "borrar"), show="headings", selectmode="extended")
        for col in ("archivo1", "archivo2", "similitud", "borrar"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=250 if col != "similitud" else 80)
        self.tree.pack(expand=True, fill="both")

        # Botones adicionales
        self.boton_exportar = tk.Button(root, text="📤 Exportar a Excel", command=self.exportar_excel)
        self.boton_exportar.pack(pady=5)

        self.boton_borrar = tk.Button(root, text="🗑️ Borrar seleccionados", command=self.borrar_seleccionados)
        self.boton_borrar.pack(pady=5)

    def seleccionar_carpeta(self):
        # Abre diálogo para elegir carpeta
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.texto_info.config(text=f"📁 Carpeta seleccionada: {carpeta}")
            self._procesar_carpeta(carpeta)

    def _procesar_carpeta(self, carpeta):
        self.archivos_similares.clear()
        self.tree.delete(*self.tree.get_children())
        # 🔍 Buscar todos los archivos .pptx
        self.archivos = self._buscar_pptx(carpeta)

        hashes = defaultdict(list)
        textos = {}

        # 🧾 Recorremos todos los archivos y:
        # 1. Calculamos hash MD5 (para detectar duplicados exactos)
        # 2. Extraemos texto de las diapositivas (para similitud parcial)
        for archivo in self.archivos:
            h = self._hash_md5(archivo)
            hashes[h].append(archivo)
            textos[archivo] = self._extraer_texto(archivo)

        # 🧩 Comparación por HASH: si hay más de un archivo con mismo hash → son duplicados exactos
        for grupo in hashes.values():
            if len(grupo) > 1:
                # Iteramos sobre todos los pares posibles del grupo
                for i in range(len(grupo)):
                    for j in range(i + 1, len(grupo)):
                        self._agregar_resultado(grupo[i], grupo[j], 1.0)

        # 📐 Comparación por contenido textual (diapositivas)
        # Recorremos todos los pares posibles de archivos diferentes
        for i in range(len(self.archivos)):
            for j in range(i + 1, len(self.archivos)):
                a1, a2 = self.archivos[i], self.archivos[j]
                sim = self._similitud(textos[a1], textos[a2])
                if 0.85 <= sim < 1.0:
                    self._agregar_resultado(a1, a2, sim)

    def _agregar_resultado(self, archivo1, archivo2, similitud):
        # Almacena el resultado y lo agrega visualmente a la tabla
        self.archivos_similares.append((archivo1, archivo2, similitud))
        self.tree.insert("", "end", values=(archivo1, archivo2, f"{similitud * 100:.1f}%", archivo2))
        # Por defecto se propone borrar archivo2


    def borrar_seleccionados(self):
        # Elimina el archivo marcado en la columna 'borrar' de cada fila seleccionada
        items = self.tree.selection()
        if not items:
            messagebox.showinfo("Info", "Seleccioná al menos una fila para borrar.")
            return

        # confirm = messagebox.askyesno("Confirmar", "¿Seguro que querés borrar los archivos seleccionados?")
        # if not confirm:
        #     return
        


        errores = []
        for item in items:

            archivo_borrar = self.tree.item(item)["values"][3]
            res = custom_prompt(root)
            print("Elegiste:", res)
            try:
                # os.remove(archivo_borrar)
                pass
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
        if not self.archivos_similares:
            messagebox.showinfo("Sin datos", "No hay resultados para exportar.")
            return

        df = pd.DataFrame([{
            "Archivo 1": a1,
            "Archivo 2": a2,
            "Similitud (%)": round(sim * 100, 1)
        } for a1, a2, sim in self.archivos_similares])

        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if ruta:
            df.to_excel(ruta, index=False)
            messagebox.showinfo("Exportado", f"Archivo guardado en:\n{ruta}")

    # -------------------------------
    # FUNCIONES AUXILIARES
    # -------------------------------

    @staticmethod
    def _buscar_pptx(carpeta):
        # Busca todos los archivos .pptx recursivamente
        return [os.path.join(root, f)
                for root, _, files in os.walk(carpeta)
                for f in files if f.lower().endswith(".pptx")]

    @staticmethod
    def _hash_md5(archivo):
        # Calcula el hash MD5 (identificador único) de un archivo binario
        h = hashlib.md5()
        with open(archivo, "rb") as f:
            for bloque in iter(lambda: f.read(4096), b""):
                h.update(bloque)
        return h.hexdigest()

    @staticmethod
    def _extraer_texto(archivo):
        # Lee cada diapositiva del archivo y extrae todo el texto visible
        try:
            prs = Presentation(archivo)
            return "\n".join(shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text"))
        except:
            return ""

    @staticmethod
    def _similitud(txt1, txt2):
        # Calcula cuán similares son dos textos (0.0 = nada parecido, 1.0 = iguales)
        return SequenceMatcher(None, txt1, txt2).ratio()

# --- EJECUCIÓN DE LA APLICACIÓN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AppCompararPptx(root)
    root.mainloop()
