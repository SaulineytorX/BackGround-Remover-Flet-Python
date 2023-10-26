import os
from datetime import datetime
from rembg import remove
from typing import Dict
import shutil
import re

import flet as ft
from flet import (
    Column,
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    FilePickerUploadEvent,
    FilePickerUploadFile,
    ProgressRing,
    Ref,
    Row,
    Text,
    icons,
)

def main(page: ft.Page):
    page.title = "Remueve el fondo de tus imagenes"
    page.scroll = "adaptive "
    title_text = ft.Row(
        controls=[
            ft.Stack(
            [
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            "Remueve el fondo de tus imagenes",
                            ft.TextStyle(
                                size=40,
                                weight=ft.FontWeight.BOLD,
                                foreground=ft.Paint(
                                    color=ft.colors.BLUE_700,
                                    stroke_width=6,
                                    stroke_join=ft.StrokeJoin.ROUND,
                                    style=ft.PaintingStyle.STROKE,
                                ),
                            ),
                        ),
                    ],
                ),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            "Remueve el fondo de tus imagenes",
                            ft.TextStyle(
                                size=40,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.GREY_300,
                            ),
                        ),
                    ],
                ),
            ]
        )
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )
    page.add(title_text)
    subtitle_text = ft.Row(
        [
            ft.Text(
                "By Saulineytor",
                style=ft.TextStyle(
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.colors.BLUE_700,
                ),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    page.add(subtitle_text)
        
        
        
#-------------------------------------------------------------------------------------------------------    
    #Carga de imagenes 
    prog_bars: Dict[str, ProgressRing] = {}
    files = Ref[Column]()
    upload_button = Ref[ElevatedButton]()

    def file_picker_result(e: FilePickerResultEvent):
        upload_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(Row([prog, Text(f.name)]))
        page.update()

    def on_upload_progress(e: FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = FilePicker(on_result=file_picker_result, on_upload=on_upload_progress)

    def upload_files(e): 
        uf = []
        if file_picker.result is not None and file_picker.result.files is not None:
            for f in file_picker.result.files:
                uf.append(
                    f.name,
                ),
                print(f.path)
                upload_path=os.path.join(os.getcwd(),"input")
                shutil.copy(f.path,upload_path)
                # Llamar manualmente a la función on_upload_progress
                on_upload_progress(FilePickerUploadEvent(f.name, 100,None))
            file_picker.upload(uf)

    # hide dialog in a overlay
    page.overlay.append(file_picker)
#Fin de la carga de imagenes ##############################################################################################################
    page.add(
        ft.Row(
            [
                ElevatedButton(
                    "Seleciona tus imagenes...",
                    icon=icons.FOLDER_OPEN,
                    on_click=lambda _: file_picker.pick_files(file_type = ft.FilePickerFileType.IMAGE,
                                                              allow_multiple=True),
                    
                ),
                Column(ref=files),
                ElevatedButton(
                    "Subir imagenes",
                    ref=upload_button,
                    icon=icons.UPLOAD,
                    on_click=upload_files,
                    disabled=True,
                ),
                ElevatedButton(
                    "Quitar fondo",
                    on_click=lambda _: (remover.process_images(),mostrar_imagen2()),
                    
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )
 
#Inicio de la funcion mostrar imagen
    def mostrar_imagen():
        page.add(
            ft.Container(
                ft.Image(
                    src=f"{background_output}",
                    width=300,
                    height=300,
                    border_radius=ft.border_radius.all(10),
                    ),
                on_click=lambda _: os.startfile(os.path.dirname(background_output))
            )
        )
    def mostrar_imagen2(rutas_imagenes):
        column = ft.Column()
        for ruta in rutas_imagenes:
            column.controls.append(
                ft.Container(
                    ft.Image(
                        src=f"{ruta}",
                        width=300,
                        height=300,
                        border_radius=ft.border_radius.all(10),
                    ),
                    on_click=lambda _: os.startfile(os.path.dirname(ruta))
                )
            )
        page.add(column)
            

#Fin de la funcion mostrar imagen    
#Clase para remover el fondo de las imagenes##############################################################################################################
class BackgroundRemover:
    def __init__(self,input_folder,output_folder) :
        self.input_folder = input_folder
        self.output_folder = output_folder

    def process_images(self):
        today=datetime.now().strftime('%Y-%m-%d %H-%M-%S') #obtiene la fecha y hora actual
        processed_folder = os.path.join(self.output_folder,today)#crea la carpeta de procesados con la fecha y hora
        os.makedirs(processed_folder, exist_ok=True)#crea la carpeta de procesados si no existe

        for filename in os.listdir(self.input_folder):#recorre el directorio de imagenes
            if filename.endswith(('.png','.jpg','.jpeg')):
                input_path = os.path.join(self.input_folder,filename)# crea el path de la imagen original
                output_path = os.path.join(processed_folder,filename)# crea el path de la imagen procesada
                self._remove_background(input_path,output_path)# remueve el fondo de la imagen
                self._move_originals(input_path,processed_folder) #mover imagenes originales a la carpeta de procesados

    def _remove_background(self,input_p,output_p):
        rutas_imagenes = []
        global background_output
        with open(input_p,'rb') as inp, open(output_p,'wb') as outp: #abre la imagen original y la imagen procesada
            background_output = remove(inp.read()) #remove background de la imagen
            outp.write(background_output) #escribe la imagen procesada
            print('Imagen procesada: ',output_p)
            background_output = output_p
            rutas_imagenes.append(background_output)
        return output_p


    def _move_originals(self,input_p,dest_p):
        originals_folder = os.path.join(dest_p,'originals')#crea la carpeta de originales
        os.makedirs(originals_folder, exist_ok=True) #crea la carpeta de originales si no existe

        filename = os.path.basename(input_p) #obtiene el nombre del archivo
        new_path = os.path.join(originals_folder,filename) #crea el path de la imagen original
        os.rename(input_p,new_path) #mueve la imagen original a la carpeta de originales
        
        
    def _create_folders(self):
        os.makedirs(output_folder, exist_ok=True)


if __name__ == '__main__':
    input_folder = 'input' #crea las variables de input y output 
    output_folder = 'output' #crea las variables de input y output
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    remover = BackgroundRemover(input_folder,output_folder) #crea el objeto BackgroundRemover
    remover.process_images() #ejecuta el proceso de remover el fondo de las imagenes
    
 
#Fin de la clase BackgroundRemover##############################################################################################################    
    
ft.app(target=main, upload_dir="input")

