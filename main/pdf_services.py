from fpdf import FPDF

class Remito(FPDF):
    def __init__(self, id_operacion, fecha, nombre, localidad, direccion, productos, apellido=" ", cuit=" "):
        # A4 Apaisado (Landscape): 297mm x 210mm
        super().__init__(orientation='L', format='A4')
        self.set_auto_page_break(auto=True, margin=5)
        self.id_operacion = id_operacion
        self.fecha = fecha
        self.nombre = nombre
        self.apellido = apellido
        self.localidad = localidad
        self.direccion = direccion
        self.productos = productos
        self.cuit = cuit

    def header(self):
        self.dibujar_esqueleto(0, "ORIGINAL")
        self.dibujar_esqueleto(148.5, "DUPLICADO")

    def dibujar_esqueleto(self, offset_x, etiqueta):
        # Esqueleto principal del comprobante
        self.set_line_width(0.3)
        self.rect(offset_x + 5, 5, 138.5, 200)
        
        # Etiqueta Superior Center
        self.set_font('Arial', 'B', 8)
        self.set_xy(offset_x + 5, 5)
        self.cell(138.5, 5, etiqueta, 0, 0, 'C')

        self.line(offset_x + 5, 45, offset_x + 143.5, 45) 
        
        id_str = str(self.id_operacion).zfill(5)
        
        # Casilla 'X'
        self.set_font('Arial', 'B', 24)
        self.rect(offset_x + 68, 12, 12, 12)
        self.set_xy(offset_x + 68, 12)
        self.cell(12, 12, 'X', 0, 0, 'C')
        
        # Texto debajo de 'X'
        self.set_font('Arial', 'B', 5)
        self.set_xy(offset_x + 60, 26)
        self.cell(28, 3, 'DOCUMENTO', 0, 2, 'C')
        self.cell(28, 3, 'NO VALIDO COMO', 0, 2, 'C')
        self.cell(28, 3, 'FACTURA', 0, 2, 'C')
        
        self.line(offset_x + 74, 38, offset_x + 74, 45)
        
        # Textos de la derecha
        self.set_font('Arial', 'B', 18)
        self.set_xy(offset_x + 80, 12)
        self.cell(63.5, 10, 'REMITO', 0, 1, 'C')
        
        self.set_font('Arial', '', 14)
        self.set_xy(offset_x + 80, 22)
        self.cell(63.5, 8, f'Nº {id_str}', 0, 1, 'C')
        
        self.set_font('Arial', '', 9)
        self.set_xy(offset_x + 80, 30)
        self.cell(63.5, 5, 'FECHA', 0, 1, 'C')
        
        # Fecha
        self.rect(offset_x + 90, 36, 12, 6)
        self.rect(offset_x + 104, 36, 12, 6)
        self.rect(offset_x + 118, 36, 16, 6)
        
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
                if len(parts[0]) == 4:
                    d, m, y = parts[2], parts[1], parts[0]
                else:
                    d, m, y = parts[0], parts[1], parts[2]
            else:
                d = self.fecha

        if len(y) == 2: y = "20" + y

        self.set_xy(offset_x + 90, 36)
        self.cell(12, 6, str(d)[:2], 0, 0, 'C')
        self.set_xy(offset_x + 104, 36)
        self.cell(12, 6, str(m)[:2], 0, 0, 'C')
        self.set_xy(offset_x + 118, 36)
        self.cell(16, 6, str(y)[:4], 0, 0, 'C')
        
        # Datos del Cliente
        self.set_font('Arial', '', 9)
        self.set_xy(offset_x + 5, 47)
        self.cell(133.5, 6, f' Señor/a: {self.nombre} {self.apellido}')
        self.line(offset_x + 5, 54, offset_x + 143.5, 54)
        
        self.set_xy(offset_x + 5, 55)
        dir_str = self.direccion if self.direccion else ""
        loc_str = self.localidad if self.localidad else ""
        domicilio = f'{dir_str}' + (f' - {loc_str}' if loc_str else '')
        self.cell(133.5, 6, f' Domicilio: {domicilio}')
        self.line(offset_x + 5, 62, offset_x + 143.5, 62)
        
        self.set_xy(offset_x + 5, 63)
        self.cell(133.5, 6, f' CUIT: {self.cuit if self.cuit else ""}')
        self.line(offset_x + 5, 70, offset_x + 143.5, 70)
        
        # Columnas
        self.set_font('Arial', 'B', 9)
        self.set_xy(offset_x + 5, 70)
        self.cell(20, 8, 'CANT.', 0, 0, 'C')
        self.cell(88.5, 8, 'DETALLE', 0, 0, 'C')
        self.cell(30, 8, 'Precio U.', 0, 0, 'C')
        self.line(offset_x + 5, 78, offset_x + 143.5, 78)
        
        # Lineas verticales de la tabla
        self.line(offset_x + 25, 70, offset_x + 25, 205)
        self.line(offset_x + 113.5, 70, offset_x + 113.5, 205)

    def draw_products(self):
        self.set_font('Arial', '', 9)
        y_pos = 78
        total_monto = 0.0
        
        for prod in self.productos:
            cant = str(prod.get('cantidad', '')) if isinstance(prod, dict) else str(getattr(prod, 'cantidad', ''))
            
            if isinstance(prod, dict):
                detalle = str(prod.get('detalle', prod.get('nombre', prod.get('producto', '-'))))
                precio_str = str(prod.get('precio_unitario', prod.get('precio', '-')))
            else:
                if hasattr(prod, 'producto'):
                    detalle = getattr(prod.producto, 'nombre', str(prod.producto))
                    precio_str = str(getattr(prod.producto, 'precio', getattr(prod, 'precio', '-')))
                else:
                    detalle = str(getattr(prod, 'detalle', getattr(prod, 'nombre', '-')))
                    precio_str = str(getattr(prod, 'precio_unitario', getattr(prod, 'precio', '-')))
                    
            try:
                c = float(cant)
                p = float(precio_str)
                total_monto += (c * p)
            except ValueError:
                pass
            
            precio_val = f"${precio_str}" if precio_str.replace('.', '', 1).isdigit() else precio_str

            self.escribir_fila(0, y_pos, cant, detalle, precio_val)
            self.escribir_fila(148.5, y_pos, cant, detalle, precio_val)
            
            y_pos += 8
            self.line(5, y_pos, 143.5, y_pos)
            self.line(148.5 + 5, y_pos, 148.5 + 143.5, y_pos)
            
            if y_pos >= 193:
                self.add_page()
                y_pos = 78

        self.dibujar_total(0, total_monto)
        self.dibujar_total(148.5, total_monto)

    def escribir_fila(self, offset_x, y, c, d, p):
        self.set_xy(offset_x + 5, y)
        self.cell(20, 8, c, 0, 0, 'C')
        self.set_xy(offset_x + 25, y)
        # Mostrar el detalle con limite de caracteres y ajustado
        self.cell(88.5, 8, f' {d[:48]}', 0, 0, 'L')
        self.set_xy(offset_x + 113.5, y)
        self.cell(30, 8, p, 0, 0, 'C')

    def dibujar_total(self, offset_x, total_monto):
        self.set_fill_color(255, 255, 255)
        # Dibujamos en la base del remito
        self.rect(offset_x + 103.5, 193, 40, 12, 'DF')
        
        self.set_xy(offset_x + 103.5, 193)
        self.set_font('Arial', 'B', 8)
        self.cell(40, 5, 'TOTAL', 0, 2, 'C')
        
        self.set_font('Arial', 'B', 11)
        precio_formateado = f"${total_monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.cell(40, 7, precio_formateado, 0, 0, 'C')
        
    def generate_pdf(self, path=None):
        self.add_page()
        self.draw_products()
        if path:
            return self.output(path)
        else:
            try:
                salida = self.output()
                return bytes(salida) if isinstance(salida, bytearray) else salida
            except TypeError:
                return self.output(dest='S').encode('latin1')