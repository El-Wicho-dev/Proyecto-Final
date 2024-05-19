from Documentos.models import Documento

class Rutas_doc:
    def __init__(self, id_documento):
        self.id_documento = id_documento

    def get_editable(self):
        documento = Documento.objects.select_related('id_plantilla', 'id_linea').get(id_documento=self.id_documento)

        plantilla = documento.id_plantilla.nombre
        tipo_area = documento.id_plantilla.tipo_area
        area = documento.id_linea.area
        linea = documento.id_linea.linea
        nombre = f"{documento.id_plantilla.codigo}-{documento.id_linea.codigo} REV.{documento.rev_documento} {documento.nombre}"

        # Lógica para construir la ruta basada en los datos obtenidos
        if plantilla not in ["Plantilla", "Manual"]:
            if plantilla in ["Ayuda visual (Vertical)", "Ayuda visual (Horizontal)"]:
                plantilla = "Ayuda visual"
            if plantilla in ["Instrucciones de Operaciones (de proceso)", "Instrucciones de Operaciones (de sistema)"]:
                plantilla = "Instrucciones de Operaciones"

            if tipo_area == "1":
                ruta = f"{plantilla}/Clientes/{area}/{linea}/{nombre}"
            elif tipo_area == "2":
                ruta = f"{plantilla}/{linea}/{nombre}"
            elif tipo_area == "4":
                if area == "Departamento":
                    ruta = f"{plantilla}/{linea}/{nombre}"
                else:
                    ruta = f"{plantilla}/Clientes/{area}/{linea}/{nombre}"

            return ruta

    def get_pdf(self):
        documento = Documento.objects.select_related('id_plantilla', 'id_linea').get(id_documento=self.id_documento)

        plantilla = documento.id_plantilla.nombre
        tipo_area = documento.id_plantilla.tipo_area
        area = documento.id_linea.area
        linea = documento.id_linea.linea
        nombre = f"{documento.id_plantilla.codigo}-{documento.id_linea.codigo} REV.{documento.rev_documento} {documento.nombre}"

        # Lógica para construir la ruta basada en los datos obtenidos
        if plantilla not in ["Plantilla", "Manual"]:
            if plantilla in ["Ayuda visual (Vertical)", "Ayuda visual (Horizontal)"]:
                plantilla = "Ayuda visual"
            if plantilla in ["Instrucciones de Operaciones (de proceso)", "Instrucciones de Operaciones (de sistema)"]:
                plantilla = "Instrucciones de Operaciones"

            if tipo_area == "1":
                ruta = f"{plantilla}/Clientes/{area}/{linea}/{nombre}"
            elif tipo_area == "2":
                ruta = f"{plantilla}/{linea}/{nombre}"
            elif tipo_area == "4":
                if area == "Departamento":
                    ruta = f"{plantilla}/{linea}/{nombre}"
                else:
                    ruta = f"{plantilla}/Clientes/{area}/{linea}/{nombre}"

            ruta = f"{ruta}.pdf"

            return ruta