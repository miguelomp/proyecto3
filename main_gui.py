import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from principal.modelos import Doctor, Paciente
from principal.autenticacion import ErrorDeLogin

class ErrorDeValidacion(Exception):
    #se muestra si dejan algun campo vacio

    pass

class ErrorAlProcesarDatos(Exception):
    #se muestra si no se cargan los datos correctamente

    pass

class AplicacionMedico:
    def __init__(self, root):
        #Configura la ventana principal,
        #inicializa las estructuras de datos
        #y decide qué pantalla mostrar al inicio.

        self.root = root
        self.root.title("Sistema médico")
        self.root.geometry("500x600")
        
        self.archivo_bd = "datos.json"
        self.lista_pacientes = []
        self.doctor_sistema = None
        
        self.contenedor = tk.Frame(self.root)
        self.contenedor.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.cargar_datos()

        if self.doctor_sistema:
            self.pantalla_login()
        else:
            self.pantalla_registro_doctor()

    def guardar_datos(self):
        #transforma los datos y descompone los objetos
        #para que el json los lea y guarde correctamente

        try:
            datos = {
                 "doctor": {
                    "nombre": self.doctor_sistema.nombre,
                    "edad": self.doctor_sistema.edad,
                    "usuario": self.doctor_sistema.usuario,
                    "clave": self.doctor_sistema.clave
                } if self.doctor_sistema else None,
                "pacientes": [
                    {
                        "nombre": p.nombre,
                        "edad": p.edad,
                        "padecimientos": p.padecimientos,
                        "peso": p.peso
                    } for p in self.lista_pacientes
                ]
            }
            with open(self.archivo_bd, "w") as f:
                json.dump(datos, f, indent=4)

        except Exception:

            raise ErrorAlProcesarDatos("No se pudieron guardar los cambios en el archivo.")

    def cargar_datos(self):
        #verifica que exista el archivo con los datos y vuelve a organizar los objetos

        if os.path.exists(self.archivo_bd):
            try:
                with open(self.archivo_bd, "r") as f:
                    datos = json.load(f)
                    if datos["doctor"]:
                        d = datos["doctor"]
                        self.doctor_sistema = Doctor(d["nombre"], d["edad"], d["usuario"], d["clave"])
                    
                    for p in datos["pacientes"]:
                        nuevo_p = Paciente(p["nombre"], p["edad"], p["padecimientos"], p["peso"])
                        self.lista_pacientes.append(nuevo_p)
            except (json.JSONDecodeError, KeyError):
                messagebox.showerror("Error", "No se pudo leer el archiovo")

    def limpiar_pantalla(self):
        #limpia la pantalla y vuelve a cargar
        #los datos nuevos para mostrar lo que se selecciona

        for w in self.contenedor.winfo_children():
            w.destroy()

    def pantalla_registro_doctor(self):
        #muetra el primer formulario,
        #solo es la primera vez para registrar el primer doctor

        self.limpiar_pantalla()
        tk.Label(self.contenedor, text="REGISTRO DEL DOCTOR", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(self.contenedor, text="Nombre:").pack()
        ent_nombre = tk.Entry(self.contenedor)
        ent_nombre.pack()
        
        tk.Label(self.contenedor, text="Usuario:").pack()
        ent_usuario = tk.Entry(self.contenedor)
        ent_usuario.pack()
        
        tk.Label(self.contenedor, text="Clave:").pack()
        ent_clave = tk.Entry(self.contenedor, show="*")
        ent_clave.pack()

        def guardar():
            try:
                if not (ent_nombre.get() and ent_usuario.get() and ent_clave.get()):
                    raise ErrorDeValidacion("Todos los campos de registro son obligatorios.")
                
                self.doctor_sistema = Doctor(ent_nombre.get(), 40, ent_usuario.get(), ent_clave.get())
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Doctor registrado correctamente.")
                self.pantalla_login()
            except ErrorDeValidacion as e:
                messagebox.showwarning("Validación", str(e))
            except ErrorAlProcesarDatos as e:
                messagebox.showerror("Archivo", str(e))

        tk.Button(self.contenedor, text="Registrar", command=guardar, bg="green", fg="white").pack(pady=20)

    def pantalla_login(self):
        
        #cuando yua hay un doctor guardado
        #pude los datos de ese doctor para poder entrar

        self.limpiar_pantalla()
        tk.Label(self.contenedor, text=f"Inicia sesión doctor: {self.doctor_sistema.nombre}", font=("Arial", 12)).pack(pady=10)
        
        tk.Label(self.contenedor, text="Usuario:").pack()
        ent_u = tk.Entry(self.contenedor)
        ent_u.pack()
        
        tk.Label(self.contenedor, text="Clave:").pack()
        ent_c = tk.Entry(self.contenedor, show="*")
        ent_c.pack()

        def intentar_login():
            try:
                if self.doctor_sistema.validar_acceso(ent_u.get(), ent_c.get()):
                    self.menu_operaciones()
            except ErrorDeLogin as e:
                messagebox.showerror("Error de Acceso", str(e))

        tk.Button(self.contenedor, text="Entrar", command=intentar_login).pack(pady=10)

    def menu_operaciones(self):
        #muestra el menu

        self.limpiar_pantalla()
        tk.Label(self.contenedor, text="MENÚ PRINCIPAL", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Button(self.contenedor, text="1. Crear paciente", width=30, command=self.form_paciente).pack(pady=5)
        tk.Button(self.contenedor, text="2. Ver pacientes", width=30, command=self.ver_pacientes).pack(pady=5)
        tk.Button(self.contenedor, text="3. Cerrar sesión", width=30, command=self.pantalla_login).pack(pady=5)
        tk.Button(self.contenedor, text="4. Salir", width=30, command=self.root.quit, bg="red", fg="white").pack(pady=5)

    def form_paciente(self):

        #muestra el formulario para guardar datos del paciente

        self.limpiar_pantalla()
        tk.Label(self.contenedor, text="Nuevo paciente", font=("Arial", 12)).pack(pady=10)
        
        campos = ["Nombre", "Edad", "Padecimientos", "Peso"]
        entradas = {}
        
        for campo in campos:
            tk.Label(self.contenedor, text=f"{campo}:").pack() 
            e = tk.Entry(self.contenedor)
            e.pack()
            entradas[campo] = e

        def guardar_p():
            try:
                # Validación manual rápida
                if not entradas["Nombre"].get() or not entradas["Edad"].get():
                    raise ErrorDeValidacion("El nombre y la edad son datos mínimos requeridos.")
                
                nuevo = Paciente(entradas["Nombre"].get(), entradas["Edad"].get(), 
                                entradas["Padecimientos"].get(), entradas["Peso"].get())
                self.lista_pacientes.append(nuevo)
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Paciente guardado en el sistema.")
                self.menu_operaciones()
            except ErrorDeValidacion as e:
                messagebox.showwarning("Validación", str(e))

        tk.Button(self.contenedor, text="Guardar", command=guardar_p).pack(pady=10)
        tk.Button(self.contenedor, text="Volver", command=self.menu_operaciones).pack()

    def ver_pacientes(self):

        #crea una lista visual escroleable
        #para mostrar los pacientes y sus datos generales

        self.limpiar_pantalla()
        tk.Label(self.contenedor, text="LISTA DE PACIENTES", font=("Arial", 12)).pack(pady=10)
        
        canvas = tk.Canvas(self.contenedor)
        scrollbar = tk.Scrollbar(self.contenedor, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for p in self.lista_pacientes:
            texto = f"{p.nombre} | Edad: {p.edad} | {p.padecimientos}"
            tk.Label(scrollable_frame, text=texto, relief="groove", width=50, anchor="w").pack(pady=2)
            
        canvas.pack(side="left", fill="both", expand=True) 
        scrollbar.pack(side="right", fill="y") 
        
        tk.Button(self.contenedor, text="Volver", command=self.menu_operaciones).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionMedico(root)
    root.mainloop()