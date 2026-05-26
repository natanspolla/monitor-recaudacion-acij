# Monitor de Recaudación Nacional · ACIJ

Visualización interactiva de la recaudación nacional argentina, basada en datos oficiales de ARCA (ex AFIP).

Desarrollado por [ACIJ](https://www.acij.org.ar) — Asociación Civil por la Igualdad y la Justicia.

## Funcionalidades

- **Evolución anual**: barras apiladas por categoría impositiva, desde 2003 a la fecha
- **Evolución mensual**: líneas por categoría para el año seleccionado; la serie se corta en el último mes con datos disponibles
- **Comparador de períodos**: selección libre de meses y años para comparar, con vista "por mes" o "acumulado anual"
- Cada sección permite alternar entre **gráfico** y **tabla**
- Ajuste por **inflación (IPC)** con base en el último mes con dato de recaudación, o valores nominales

## Datos

Los datos de recaudación provienen de los informes mensuales publicados por ARCA (ex AFIP). El índice de precios al consumidor (IPC) utilizado para el ajuste por inflación es publicado por el INDEC.

Los datos están embebidos directamente en el archivo HTML para permitir su uso sin servidor.

## Uso

Abrí `recaudacion_v4.html` directamente en el navegador. No requiere servidor ni conexión a internet.

### Actualizar los datos

1. Colocá el nuevo archivo Excel de ARCA en el directorio junto con `afip_dashboard_v3.html`
2. Ejecutá el script de inyección en PowerShell:
   ```powershell
   .\inject_data.ps1
   ```
3. Abrí `recaudacion_v4.html` en el navegador

## Tecnologías

- [Chart.js 4.4](https://www.chartjs.org/) — visualizaciones
- [SheetJS (xlsx) 0.18](https://sheetjs.com/) — lectura de archivos Excel en el navegador
- HTML/CSS/JS puro — sin frameworks ni dependencias externas salvo las anteriores (cargadas desde CDN)
