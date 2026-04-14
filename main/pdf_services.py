from fpdf import FPDF

class Remito(FPDF):
    def __init__(self, id_operacion, fecha, nombre, localidad, direccion, productos, apellido=" ", cuit=" "):
        # FPDF con orientación Horizontal (Landscape) y tamaño A5 (la mitad de un A4)
        super().__init__(orientation='L', format='A5')
        self.id_operacion = id_operacion
        self.fecha = fecha
        self.nombre = nombre
        self.apellido = apellido
        self.localidad = localidad
        self.direccion = direccion
        self.productos = productos
        self.cuit = cuit

    def header(self):
        # Borde Exterior: El alto de un A5 apaisado es 148mm. Limitamos la caja hasta 138.
        self.rect(10, 10, 190, 128)
        # Línea horizontal divisoria debajo del encabezado principal
        self.line(10, 45, 200, 45) 
        
        # ID formateado
        id_str = str(self.id_operacion).zfill(5)
        
        # Casilla 'X'
        self.set_font('Arial', 'B', 24)
        self.rect(95, 12, 15, 15)
        self.set_xy(95, 12)
        self.cell(15, 15, 'X', 0, 0, 'C')
        
        # Texto debajo de 'X'
        self.set_font('Arial', 'B', 6)
        self.set_xy(87.5, 29)
        self.cell(30, 3, 'DOCUMENTO', 0, 2, 'C')
        self.cell(30, 3, 'NO VALIDO COMO', 0, 2, 'C')
        self.cell(30, 3, 'FACTURA', 0, 2, 'C')
        
        # Línea vertical central debajo del texto
        self.line(102.5, 38, 102.5, 45)
        
        # Textos de la derecha
        self.set_font('Arial', 'B', 18)
        self.set_xy(105, 12)
        self.cell(95, 10, 'REMITO', 0, 1, 'C')
        
        self.set_font('Arial', '', 14)
        self.set_xy(105, 22)
        self.cell(95, 10, f'Nº {id_str}', 0, 1, 'C')
        
        self.set_font('Arial', '', 9)
        self.set_xy(135, 33)
        self.cell(50, 4, 'FECHA', 0, 1, 'C')
        
        # Cajas de Fecha
        self.rect(142, 37, 10, 6)
        self.rect(154, 37, 10, 6)
        self.rect(166, 37, 12, 6)
        
        d, m, y = "", "", ""
        if hasattr(self.fecha, "strftime"):
             d, m, y = self.fecha.strftime("%d"), self.fecha.strftime("%m"), self.fecha.strftime("%Y")
        elif isinstance(self.fecha, str):
            parts = []
            if '-' in self.fecha:
                parts = self.fecha.split('-')
            elif '/' in self.fecha:
                parts = self.fecha.split('/')
            
            if len(parts) == 3:
                if len(parts[0]) == 4: # yyyy-mm-dd
                    d, m, y = parts[2], parts[1], parts[0]
                else: # dd-mm-yyyy
                    d, m, y = parts[0], parts[1], parts[2]
            else:
                d = self.fecha

        if len(y) == 2: y = "20" + y

        self.set_xy(142, 37)
        self.cell(10, 6, str(d)[:2], 0, 0, 'C')
        self.set_xy(154, 37)
        self.cell(10, 6, str(m)[:2], 0, 0, 'C')
        self.set_xy(166, 37)
        self.cell(12, 6, str(y)[:4], 0, 0, 'C')
        
        # Datos del Cliente
        self.set_font('Arial', '', 10)
        self.set_xy(10, 47)
        self.cell(20, 6, ' Señor(es):')
        self.cell(170, 6, f' {self.nombre} {self.apellido}')
        self.line(10, 54, 200, 54)
        
        self.set_xy(10, 55)
        self.cell(20, 6, ' Domicilio:')
        dir_str = self.direccion if self.direccion else ""
        loc_str = self.localidad if self.localidad else ""
        domicilio = f' {dir_str}' + (f' - {loc_str}' if loc_str else '')
        self.cell(170, 6, domicilio)
        self.line(10, 62, 200, 62)
        
        self.set_xy(10, 63)
        self.cell(20, 6, ' CUIT:')
        self.cell(170, 6, f' {self.cuit if self.cuit else ""}')
        self.line(10, 70, 200, 70)
        
        # Títulos de Columnas (Cantidad, Detalle, Precio U.)
        self.set_font('Arial', 'B', 10)
        self.set_xy(10, 70)
        self.cell(25, 8, 'CANT.', 0, 0, 'C')
        self.cell(135, 8, 'DETALLE', 0, 0, 'C')
        self.cell(30, 8, 'Precio U.', 0, 0, 'C')
        self.line(10, 78, 200, 78)
        
        # Líneas verticales de las columnas hasta el fondo de la caja (Y=138 en A5 apaisado)
        self.line(35, 70, 35, 138)
        self.line(170, 70, 170, 138)

    def draw_products(self):
        self.set_font('Arial', '', 10)
        y_pos = 78
        
        for prod in self.productos:
            # Procesar si prod es diccionaro u objeto
            cant = str(prod.get('cantidad', '')) if isinstance(prod, dict) else str(getattr(prod, 'cantidad', ''))
            
            if isinstance(prod, dict):
                detalle = str(prod.get('detalle', prod.get('nombre', prod.get('producto', '-'))))
                precio = str(prod.get('precio_unitario', prod.get('precio', '-')))
            else:
                if hasattr(prod, 'producto'):
                    detalle = getattr(prod.producto, 'nombre', str(prod.producto))
                    precio = str(getattr(prod.producto, 'precio', getattr(prod, 'precio', '-')))
                else:
                    detalle = str(getattr(prod, 'detalle', getattr(prod, 'nombre', '-')))
                    precio = str(getattr(prod, 'precio_unitario', getattr(prod, 'precio', '-')))

            self.set_xy(10, y_pos)
            self.cell(25, 8, f"{cant}", 0, 0, 'C')
            self.set_xy(35, y_pos)
            self.cell(135, 8, f' {detalle}', 0, 0, 'L')
            
            precio_val = f"${precio}" if precio.replace('.', '', 1).isdigit() else precio
            self.set_xy(170, y_pos)
            self.cell(30, 8, precio_val, 0, 0, 'C')
            
            y_pos += 8
            self.line(10, y_pos, 200, y_pos)
            
            # Limite para el salto de página: no pasar de Y=138
            if y_pos >= 130:
                self.add_page()
                y_pos = 78

    def footer(self):
        pass
        
    def generate_pdf(self, path=None):
        self.add_page()
        self.draw_products()
        # Si queremos guardarlo localmente se envia path. 
        if path:
            return self.output(path)
        else:
            # Si no hay path se asume que queremos los bytes crudos (por ej. para Django)
            # En fpdf2 esto devuelve bytes, en la versión anterior devuelve un string con charset 'latin1'
            try:
                # FPDF2
                # Lo pasamos a 'bytes' inmutables obligatoriamente porque Django HttpResponse 
                # destruye los 'bytearray' al iterarlos como enteros.
                salida = self.output()
                return bytes(salida) if isinstance(salida, bytearray) else salida
            except TypeError:
                # FPDF 1.7.x
                return self.output(dest='S').encode('latin1')